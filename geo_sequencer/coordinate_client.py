#!/usr/bin/env python3
"""
Coordinate Client Base Classes
Abstract base class and implementations for streaming coordinate data from various sources.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
import websockets
from websockets.exceptions import ConnectionClosed


class CoordinateClient(ABC):
    """
    Abstract base class for coordinate streaming clients.
    """

    def __init__(
        self, callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ):
        """
        Initialize the coordinate client.

        Args:
            callback: Async callback function to handle coordinate data
        """
        self.callback = callback
        self.is_running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the coordinate data source.

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def listen(self):
        """
        Listen for coordinate data and call the callback when data is received.
        """
        pass

    @abstractmethod
    async def disconnect(self):
        """
        Disconnect from the coordinate data source and clean up resources.
        """
        pass

    async def process_data(self, data: Dict[str, Any]):
        """
        Process incoming coordinate data by calling the callback.

        Args:
            data: Dictionary containing coordinate information
        """
        if self.callback:
            await self.callback(data)

    async def run(self):
        """
        Main run loop for the client.
        """
        self.logger.info(f"Starting {self.__class__.__name__}...")

        if not await self.connect():
            self.logger.error("Failed to connect, exiting")
            return

        self.is_running = True

        try:
            await self.listen()
        except KeyboardInterrupt:
            self.logger.info("Client interrupted by user")
        except Exception as e:
            self.logger.error(f"Client error: {e}")
        finally:
            await self.disconnect()
            self.is_running = False


class DummyWebSocketClient(CoordinateClient):
    """
    WebSocket client for connecting to the dummy coordinate server.
    """

    def __init__(
        self,
        server_url: str = "ws://localhost:8000/ws",
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        ping_interval: float = 20.0,
        ping_timeout: float = 10.0,
    ):
        """
        Initialize the dummy WebSocket client.

        Args:
            server_url: WebSocket server URL for coordinate stream
            callback: Async callback function to handle coordinate data
            ping_interval: WebSocket ping interval in seconds
            ping_timeout: WebSocket ping timeout in seconds
        """
        super().__init__(callback)
        self.server_url = server_url
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None

    async def connect(self) -> bool:
        """
        Connect to the WebSocket server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to WebSocket: {self.server_url}")

            self.websocket = await websockets.connect(
                self.server_url,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
            )

            self.logger.info("Successfully connected to coordinate stream")
            return True

        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            return False

    async def listen(self):
        """Listen for coordinate data from WebSocket."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.process_data(data)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse coordinate data: {e}")
                except Exception as e:
                    self.logger.error(f"Error processing coordinate message: {e}")

        except ConnectionClosed as e:
            self.logger.warning(f"WebSocket connection closed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error in coordinate listener: {e}")
            raise

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.logger.info("WebSocket connection closed")


# Example of how to extend for other coordinate sources
class FileCoordinateClient(CoordinateClient):
    """
    Example client that reads coordinates from a file (for future use).
    """

    def __init__(
        self,
        file_path: str,
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        update_interval: float = 1.0,
    ):
        """
        Initialize the file coordinate client.

        Args:
            file_path: Path to the coordinate data file
            callback: Async callback function to handle coordinate data
            update_interval: How often to read the file in seconds
        """
        super().__init__(callback)
        self.file_path = file_path
        self.update_interval = update_interval

    async def connect(self) -> bool:
        """Check if file exists and is readable."""
        import os

        if os.path.exists(self.file_path) and os.access(self.file_path, os.R_OK):
            self.logger.info(f"File coordinate source ready: {self.file_path}")
            return True
        else:
            self.logger.error(f"Cannot read file: {self.file_path}")
            return False

    async def listen(self):
        """Read coordinates from file periodically."""
        # This is just a placeholder implementation
        # In a real scenario, you would implement file reading logic
        while self.is_running:
            # Example: read coordinates from file and call process_data
            await asyncio.sleep(self.update_interval)

    async def disconnect(self):
        """Clean up file resources."""
        self.logger.info("File coordinate client disconnected")


class APICoordinateClient(CoordinateClient):
    """
    Example client that fetches coordinates from a REST API (for future use).
    """

    def __init__(
        self,
        api_url: str,
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        poll_interval: float = 5.0,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the API coordinate client.

        Args:
            api_url: API endpoint URL for coordinate data
            callback: Async callback function to handle coordinate data
            poll_interval: How often to poll the API in seconds
            api_key: Optional API key for authentication
        """
        super().__init__(callback)
        self.api_url = api_url
        self.poll_interval = poll_interval
        self.api_key = api_key

    async def connect(self) -> bool:
        """Test API connection."""
        # Placeholder for API connection test
        self.logger.info(f"API coordinate client ready: {self.api_url}")
        return True

    async def listen(self):
        """Poll API for coordinate data."""
        # This is just a placeholder implementation
        # In a real scenario, you would implement HTTP requests
        while self.is_running:
            # Example: fetch coordinates from API and call process_data
            await asyncio.sleep(self.poll_interval)

    async def disconnect(self):
        """Clean up API client resources."""
        self.logger.info("API coordinate client disconnected")
