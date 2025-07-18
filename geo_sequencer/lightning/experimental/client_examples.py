#!/usr/bin/env python3
"""
Additional Coordinate Client Examples
Examples of how to create clients for different coordinate sources.
"""

import asyncio
import random
import time
from typing import Dict, Any
from coordinate_client import CoordinateClient


class RandomCoordinateClient(CoordinateClient):
    """
    A client that generates random coordinates for testing.
    """

    def __init__(self, interval: float = 2.0, callback=None):
        super().__init__(callback)
        self.interval = interval

    async def connect(self) -> bool:
        self.logger.info("Random coordinate generator ready")
        return True

    async def listen(self):
        """Generate random coordinates at specified intervals."""
        while self.is_running:
            # Generate random coordinates
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)

            data = {
                "latitude": lat,
                "longitude": lon,
                "timestamp": time.time(),
                "source": "random_generator",
            }

            await self.process_data(data)
            await asyncio.sleep(self.interval)

    async def disconnect(self):
        self.logger.info("Random coordinate generator stopped")


class CircularPathClient(CoordinateClient):
    """
    A client that generates coordinates along a circular path.
    Creates smooth, predictable musical patterns.
    """

    def __init__(
        self,
        center_lat: float = 0.0,
        center_lon: float = 0.0,
        radius: float = 10.0,
        speed: float = 0.1,
        callback=None,
    ):
        super().__init__(callback)
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius = radius
        self.speed = speed  # radians per second
        self.angle = 0.0

    async def connect(self) -> bool:
        self.logger.info(
            f"Circular path generator ready - Center: ({self.center_lat}, {self.center_lon}), Radius: {self.radius}"
        )
        return True

    async def listen(self):
        """Generate coordinates along a circular path."""
        import math

        while self.is_running:
            # Calculate position on circle
            lat = self.center_lat + (self.radius * math.cos(self.angle))
            lon = self.center_lon + (self.radius * math.sin(self.angle))

            # Clamp to valid coordinate ranges
            lat = max(-90, min(90, lat))
            lon = max(-180, min(180, lon))

            data = {
                "latitude": lat,
                "longitude": lon,
                "timestamp": time.time(),
                "angle": self.angle,
                "source": "circular_path",
            }

            await self.process_data(data)

            # Update angle for next position
            self.angle += self.speed
            if self.angle >= 2 * math.pi:
                self.angle = 0.0

            await asyncio.sleep(0.5)  # 2 updates per second

    async def disconnect(self):
        self.logger.info("Circular path generator stopped")


class LinearPathClient(CoordinateClient):
    """
    A client that generates coordinates along a linear path.
    Good for creating ascending or descending musical scales.
    """

    def __init__(
        self,
        start_lat: float = -45.0,
        end_lat: float = 45.0,
        start_lon: float = -90.0,
        end_lon: float = 90.0,
        duration: float = 20.0,
        callback=None,
    ):
        super().__init__(callback)
        self.start_lat = start_lat
        self.end_lat = end_lat
        self.start_lon = start_lon
        self.end_lon = end_lon
        self.duration = duration  # seconds to complete path
        self.start_time = None

    async def connect(self) -> bool:
        self.logger.info(
            f"Linear path generator ready - ({self.start_lat}, {self.start_lon}) to ({self.end_lat}, {self.end_lon})"
        )
        return True

    async def listen(self):
        """Generate coordinates along a linear path."""
        self.start_time = time.time()

        while self.is_running:
            current_time = time.time()
            elapsed = current_time - self.start_time

            # Calculate progress (0.0 to 1.0)
            progress = (elapsed % self.duration) / self.duration

            # Linear interpolation
            lat = self.start_lat + (self.end_lat - self.start_lat) * progress
            lon = self.start_lon + (self.end_lon - self.start_lon) * progress

            data = {
                "latitude": lat,
                "longitude": lon,
                "timestamp": current_time,
                "progress": progress,
                "source": "linear_path",
            }

            await self.process_data(data)
            await asyncio.sleep(0.2)  # 5 updates per second

    async def disconnect(self):
        self.logger.info("Linear path generator stopped")


async def demo_different_clients():
    """Demonstrate different coordinate client types."""
    print("🎵 Coordinate Client Examples Demo")
    print("This demo shows different types of coordinate patterns")
    print("Each would create different musical patterns in the sequencer")
    print()

    clients = [
        ("Random Coordinates", RandomCoordinateClient(interval=1.0)),
        (
            "Circular Path",
            CircularPathClient(center_lat=0, center_lon=0, radius=30, speed=0.2),
        ),
        ("Linear Path", LinearPathClient(start_lat=-60, end_lat=60, duration=10)),
    ]

    for name, client in clients:
        print(f"=== {name} ===")

        # Set up a simple callback to show the coordinates
        async def show_coordinates(data: Dict[str, Any]):
            lat = data.get("latitude", 0)
            lon = data.get("longitude", 0)
            source = data.get("source", "unknown")
            print(f"  {source}: Lat={lat:6.2f}, Lon={lon:7.2f}")

        client.callback = show_coordinates

        # Run each client for a few seconds
        print("Running for 5 seconds...")
        try:
            task = asyncio.create_task(client.run())
            await asyncio.sleep(5)
            client.is_running = False
            await task
        except Exception as e:
            print(f"Error: {e}")

        print()


if __name__ == "__main__":
    asyncio.run(demo_different_clients())
