#!/usr/bin/env python3
"""
Example Usage of the Refactored Geo MIDI Sequencer
This script demonstrates how to use the new modular architecture with different coordinate clients.
"""

import asyncio
import logging
from geo_midi_sequencer import GeoMidiSequencer
from coordinate_client import DummyWebSocketClient, CoordinateClient


async def example_dummy_websocket():
    """Example using the DummyWebSocketClient."""
    print("=== Example 1: Using DummyWebSocketClient ===")

    # Create the coordinate client
    dummy_client = DummyWebSocketClient(
        server_url="ws://localhost:8000/ws", ping_interval=20.0, ping_timeout=10.0
    )

    # Create the MIDI sequencer with the client
    sequencer = GeoMidiSequencer(
        coordinate_client=dummy_client,
        scale_type="pentatonic",
        base_note=60,  # Middle C
        octave_range=3,
        note_duration=2.0,
        velocity_min=64,
        velocity_max=100,
    )

    print("Starting sequencer with DummyWebSocketClient...")
    print("Make sure the dummy websocket server is running on localhost:8000")
    print("Press Ctrl+C to stop")

    try:
        await sequencer.run()
    except KeyboardInterrupt:
        print("\nStopping sequencer...")


async def example_custom_client():
    """Example creating a custom coordinate client."""
    print("\n=== Example 2: Using Custom Client ===")

    class TestCoordinateClient(CoordinateClient):
        """A simple test client that generates coordinates."""

        async def connect(self) -> bool:
            self.logger.info("Test client connected")
            return True

        async def listen(self):
            """Generate test coordinates every 3 seconds."""
            import random

            count = 0
            while self.is_running and count < 10:  # Run for 10 iterations
                # Generate random coordinates
                lat = random.uniform(-90, 90)
                lon = random.uniform(-180, 180)

                data = {
                    "latitude": lat,
                    "longitude": lon,
                    "timestamp": asyncio.get_event_loop().time(),
                }

                await self.process_data(data)
                await asyncio.sleep(3)
                count += 1

        async def disconnect(self):
            self.logger.info("Test client disconnected")

    # Create the test client
    test_client = TestCoordinateClient()

    # Create the MIDI sequencer with the test client
    sequencer = GeoMidiSequencer(
        coordinate_client=test_client,
        scale_type="major",
        base_note=48,  # C3
        octave_range=4,
        note_duration=1.5,
        velocity_min=80,
        velocity_max=127,
    )

    print("Starting sequencer with custom test client...")
    print("This will generate 10 random coordinates and then stop")

    try:
        await sequencer.run()
    except KeyboardInterrupt:
        print("\nStopping sequencer...")


def main():
    """Main function to run examples."""
    import argparse

    parser = argparse.ArgumentParser(description="Geo MIDI Sequencer Examples")
    parser.add_argument(
        "--example",
        choices=["dummy", "custom"],
        default="dummy",
        help="Which example to run (default: dummy)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Run the selected example
    if args.example == "dummy":
        asyncio.run(example_dummy_websocket())
    elif args.example == "custom":
        asyncio.run(example_custom_client())


if __name__ == "__main__":
    main()
