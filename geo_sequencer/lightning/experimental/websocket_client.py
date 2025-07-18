#!/usr/bin/env python3
"""
WebSocket Client for Geo Sequencer
A mature client implementation that connects to the geo sequencer WebSocket
and streams coordinate data with error handling and reconnection logic.
"""

import asyncio
import json
import logging
import signal
import sys
import time
from typing import Optional, Dict, Any
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI, WebSocketException


class GeoSequencerClient:
    """
    A robust WebSocket client for receiving streaming Earth coordinates
    from the Geo Sequencer server.
    """

    def __init__(
        self,
        server_url: str = "ws://localhost:8000/ws",
        reconnect_delay: float = 5.0,
        max_reconnect_attempts: int = 10,
        ping_interval: float = 20.0,
        ping_timeout: float = 10.0,
    ):
        """
        Initialize the WebSocket client.

        Args:
            server_url: WebSocket server URL
            reconnect_delay: Delay between reconnection attempts (seconds)
            max_reconnect_attempts: Maximum number of reconnection attempts
            ping_interval: Interval for sending ping frames (seconds)
            ping_timeout: Timeout for ping responses (seconds)
        """
        self.server_url = server_url
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_running = False
        self.reconnect_attempts = 0
        self.message_count = 0
        self.start_time = time.time()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _setup_logging(self):
        """Configure logging for the client."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("geo_client.log"),
            ],
        )

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def connect(self) -> bool:
        """
        Establish WebSocket connection to the server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to {self.server_url}...")

            self.websocket = await websockets.connect(
                self.server_url,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                close_timeout=10.0,
            )

            self.logger.info("Successfully connected to WebSocket server")
            self.reconnect_attempts = 0
            return True

        except InvalidURI as e:
            self.logger.error(f"Invalid WebSocket URI: {e}")
            return False
        except OSError as e:
            self.logger.error(f"Connection failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection: {e}")
            return False

    async def disconnect(self):
        """Close the WebSocket connection."""
        if self.websocket:
            try:
                await self.websocket.close()
                self.logger.info("WebSocket connection closed")
            except Exception as e:
                self.logger.error(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None

    def process_coordinate_data(self, data: Dict[str, Any]):
        """
        Process incoming coordinate data.
        Override this method to customize data processing.

        Args:
            data: Dictionary containing coordinate information
        """
        self.message_count += 1

        # Extract coordinate information
        latitude = data.get("latitude", "N/A")
        longitude = data.get("longitude", "N/A")
        timestamp = data.get("timestamp", "N/A")

        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time

        # Stream the raw coordinate data
        self.logger.info(
            f"[{self.message_count:04d}] "
            f"Coordinates: {latitude:.6f}, {longitude:.6f} | "
            f"Timestamp: {timestamp} | "
            f"Elapsed: {elapsed_time:.1f}s"
        )

        # Print raw data to stdout for streaming
        print(f"RAW_DATA: {json.dumps(data)}")

    async def listen_for_messages(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    # Parse JSON message
                    data = json.loads(message)
                    self.process_coordinate_data(data)

                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON message: {e}")
                    self.logger.debug(f"Raw message: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")

        except ConnectionClosed as e:
            self.logger.warning(f"WebSocket connection closed: {e}")
            raise
        except WebSocketException as e:
            self.logger.error(f"WebSocket error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in message listener: {e}")
            raise

    async def run_with_reconnect(self):
        """Run the client with automatic reconnection logic."""
        while self.is_running and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                # Attempt to connect
                if await self.connect():
                    # Listen for messages
                    await self.listen_for_messages()
                else:
                    # Connection failed
                    self.reconnect_attempts += 1
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        self.logger.info(
                            f"Reconnection attempt {self.reconnect_attempts}/"
                            f"{self.max_reconnect_attempts} in {self.reconnect_delay}s..."
                        )
                        await asyncio.sleep(self.reconnect_delay)
                    else:
                        self.logger.error("Maximum reconnection attempts reached")
                        break

            except (ConnectionClosed, WebSocketException, OSError) as e:
                self.logger.warning(f"Connection lost: {e}")
                await self.disconnect()

                if self.is_running:
                    self.reconnect_attempts += 1
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        self.logger.info(
                            f"Reconnecting in {self.reconnect_delay}s... "
                            f"(attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})"
                        )
                        await asyncio.sleep(self.reconnect_delay)
                    else:
                        self.logger.error("Maximum reconnection attempts reached")
                        break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                break

        await self.disconnect()

    def start(self):
        """Start the WebSocket client."""
        self.is_running = True
        self.start_time = time.time()
        self.logger.info("Starting Geo Sequencer WebSocket client...")

        try:
            asyncio.run(self.run_with_reconnect())
        except KeyboardInterrupt:
            self.logger.info("Client interrupted by user")
        finally:
            self.stop()

    def stop(self):
        """Stop the WebSocket client."""
        self.is_running = False
        self.logger.info(
            f"Client stopped. Total messages received: {self.message_count}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        elapsed_time = time.time() - self.start_time
        return {
            "messages_received": self.message_count,
            "elapsed_time": elapsed_time,
            "messages_per_second": (
                self.message_count / elapsed_time if elapsed_time > 0 else 0
            ),
            "reconnect_attempts": self.reconnect_attempts,
            "is_running": self.is_running,
        }


def main():
    """Main function to run the WebSocket client."""
    import argparse

    parser = argparse.ArgumentParser(description="Geo Sequencer WebSocket Client")
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws",
        help="WebSocket server URL (default: ws://localhost:8000/ws)",
    )
    parser.add_argument(
        "--reconnect-delay",
        type=float,
        default=5.0,
        help="Delay between reconnection attempts in seconds (default: 5.0)",
    )
    parser.add_argument(
        "--max-reconnects",
        type=int,
        default=10,
        help="Maximum number of reconnection attempts (default: 10)",
    )
    parser.add_argument(
        "--ping-interval",
        type=float,
        default=20.0,
        help="Ping interval in seconds (default: 20.0)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and start client
    client = GeoSequencerClient(
        server_url=args.url,
        reconnect_delay=args.reconnect_delay,
        max_reconnect_attempts=args.max_reconnects,
        ping_interval=args.ping_interval,
    )

    try:
        client.start()
    except Exception as e:
        print(f"Error starting client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
