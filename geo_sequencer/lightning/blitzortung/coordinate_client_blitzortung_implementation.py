#!/usr/bin/env python3
"""
Blitzortung Coordinate Client
A coordinate client that connects to Blitzortung real-time lightning data and integrates
with the geo sequencer architecture.
"""

import asyncio
import json
import logging
import random
import ssl
import time
from typing import Dict, Any, Optional, Callable, Awaitable
import websockets
from websockets.exceptions import ConnectionClosed

from geo_sequencer.coordinate_client import CoordinateClient


class BlitzortungCoordinateClient(CoordinateClient):
    """
    Coordinate client for Blitzortung real-time lightning data.
    Connects to Blitzortung WebSocket servers and streams lightning strikes as coordinates.
    """

    def __init__(
        self,
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        reconnect_delay: float = 5.0,
        max_reconnect_attempts: int = 10,
    ):
        """
        Initialize the Blitzortung coordinate client.

        Args:
            callback: Async callback function to handle coordinate data
            reconnect_delay: Delay between reconnection attempts in seconds
            max_reconnect_attempts: Maximum number of reconnection attempts
        """
        super().__init__(callback)
        self.reconnect_delay = reconnect_delay
        self.max_reconnect_attempts = max_reconnect_attempts

        # Blitzortung WebSocket configuration
        self.hosts = ["ws1", "ws3", "ws7", "ws8"]
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.current_host = None

        # SSL context for Blitzortung servers
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

        # Statistics
        self.strike_count = 0
        self.connection_attempts = 0

    def decode(self, b: bytes) -> str:
        """
        Decode Blitzortung compressed message format.
        This is the same decoder used in the existing Blitzortung client.
        """
        e = {}
        d = list(b)
        c = d[0]
        f = c
        g = [c]
        h = 256
        o = h
        for b in range(1, len(d)):
            a = ord(d[b])
            a = d[b] if h > a else e.get(a, f + c)
            g.append(a)
            c = a[0]
            e[o] = f + c
            o += 1
            f = a
        return "".join(g)

    async def connect(self) -> bool:
        """
        Connect to Blitzortung WebSocket server.
        Tries different hosts until one succeeds.

        Returns:
            bool: True if connection successful, False otherwise
        """
        for attempt in range(self.max_reconnect_attempts):
            try:
                # Random host selection for load balancing
                self.current_host = random.choice(self.hosts)
                uri = f"wss://{self.current_host}.blitzortung.org:443/"

                self.connection_attempts += 1
                self.logger.info(f"Connecting to {uri} (attempt {attempt + 1})")

                self.websocket = await websockets.connect(uri, ssl=self.ssl_context)

                # Send initialization message (required by Blitzortung)
                await self.websocket.send('{"a": 111}')

                self.logger.info(
                    f"Successfully connected to {self.current_host}.blitzortung.org"
                )
                return True

            except Exception as e:
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_reconnect_attempts - 1:
                    await asyncio.sleep(self.reconnect_delay)
                continue

        self.logger.error("Failed to connect to any Blitzortung server")
        return False

    async def listen(self):
        """Listen for lightning strike data from Blitzortung."""
        try:
            self.logger.info("Listening for lightning strikes...")

            async for message in self.websocket:
                try:
                    # Decode and parse the message
                    decoded = self.decode(message)
                    data = json.loads(decoded)

                    # Remove signal data (just get count)
                    sig = data.pop("sig", ())
                    data["sig_num"] = len(sig)

                    # Convert Blitzortung data to coordinate format
                    coordinate_data = self._convert_to_coordinate_format(data)

                    # Process the coordinate data
                    await self.process_data(coordinate_data)

                    self.strike_count += 1

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    self.logger.error(f"Message processing error: {e}")

        except ConnectionClosed as e:
            self.logger.warning(f"WebSocket connection closed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error in lightning listener: {e}")
            raise

    def _convert_to_coordinate_format(
        self, blitzortung_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert Blitzortung lightning data to standard coordinate format.

        Args:
            blitzortung_data: Raw data from Blitzortung

        Returns:
            Dict containing standardized coordinate data
        """
        lat = blitzortung_data.get("lat", 0.0)
        lon = blitzortung_data.get("lon", 0.0)
        timestamp = blitzortung_data.get("time", time.time() * 1000)

        # Convert timestamp from milliseconds to seconds
        timestamp_seconds = timestamp / 1000.0

        # Create standardized coordinate data
        coordinate_data = {
            "latitude": lat,
            "longitude": lon,
            "timestamp": timestamp_seconds,
            "source": "blitzortung_lightning",
            "type": "lightning_strike",
            "strike_id": self.strike_count + 1,
            # Additional lightning-specific data
            "lightning": {
                "status": blitzortung_data.get("status", "unknown"),
                "region": blitzortung_data.get("region", "unknown"),
                "signal_count": blitzortung_data.get("sig_num", 0),
                "raw_timestamp": timestamp,
            },
        }

        # Log the lightning strike
        readable_time = time.strftime(
            "%Y-%m-%d %H:%M:%S UTC", time.gmtime(timestamp_seconds)
        )

        self.logger.info(
            f"⚡ Lightning #{self.strike_count + 1}: "
            f"{lat:.6f}°, {lon:.6f}° at {readable_time}"
        )

        return coordinate_data

    async def disconnect(self):
        """Disconnect from Blitzortung WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.logger.info(f"Disconnected from {self.current_host}.blitzortung.org")
            self.logger.info(f"Total lightning strikes received: {self.strike_count}")

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "strike_count": self.strike_count,
            "connection_attempts": self.connection_attempts,
            "current_host": self.current_host,
            "is_running": self.is_running,
        }


# Example usage and demo
async def demo_blitzortung_client():
    """Demonstrate the Blitzortung coordinate client."""

    async def show_lightning_coordinate(data: Dict[str, Any]):
        """Callback to display lightning coordinates."""
        lat = data.get("latitude", 0)
        lon = data.get("longitude", 0)
        lightning_info = data.get("lightning", {})
        strike_id = data.get("strike_id", 0)

        print(f"🎵 Strike #{strike_id}: {lat:.6f}°, {lon:.6f}° → Music!")
        print(
            f"   Status: {lightning_info.get('status')}, Region: {lightning_info.get('region')}"
        )
        print(f"   Signals: {lightning_info.get('signal_count')}")
        print("-" * 60)

    print("⚡ Blitzortung Coordinate Client Demo")
    print("This demo shows real lightning strikes converted to coordinates")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Create Blitzortung coordinate client
    blitzortung_client = BlitzortungCoordinateClient(callback=show_lightning_coordinate)

    try:
        await blitzortung_client.run()
    except KeyboardInterrupt:
        print("\n⏹️  Demo stopped by user")
        stats = blitzortung_client.get_stats()
        print(f"📊 Total lightning strikes: {stats['strike_count']}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    asyncio.run(demo_blitzortung_client())
