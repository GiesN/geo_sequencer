#!/usr/bin/env python3
"""
Test script for the quantized geo MIDI sequencer
Tests the quantization logic without requiring MIDI or internet connection.
"""

import asyncio
import time


# Mock coordinate client for testing
class MockCoordinateClient:
    """Mock coordinate client that generates test data."""

    def __init__(self):
        self.callback = None
        self.is_running = False

    async def run(self):
        """Generate some test coordinates."""
        self.is_running = True
        test_coordinates = [
            {"latitude": 52.5, "longitude": 13.4, "timestamp": time.time()},  # Berlin
            {
                "latitude": 40.7,
                "longitude": -74.0,
                "timestamp": time.time(),
            },  # New York
            {"latitude": -33.9, "longitude": 151.2, "timestamp": time.time()},  # Sydney
            {"latitude": 35.7, "longitude": 139.7, "timestamp": time.time()},  # Tokyo
        ]

        for coord in test_coordinates:
            if self.callback and self.is_running:
                await self.callback(coord)
                await asyncio.sleep(0.5)  # Spread out the coordinates

        # Keep running briefly to test quantization
        await asyncio.sleep(3)


class TestMidiOutput:
    """Mock MIDI output for testing."""

    def __init__(self):
        self.sent_messages = []

    def send(self, msg):
        self.sent_messages.append(msg)
        print(f"🎵 MIDI: {msg}")

    def close(self):
        print("📴 MIDI port closed")


async def test_quantized_sequencer():
    """Test the quantized sequencer with mock components."""
    print("🧪 Testing Quantized Geo MIDI Sequencer")
    print("=" * 50)

    # Import the modules
    from geo_sequencer.quantized_geo_midi_sequencer import QuantizedGeoMidiSequencer
    from geo_sequencer.config_manager import SequencerConfig

    # Load configuration
    config = SequencerConfig()
    quantization_config = config.get_quantization_config()

    print(
        f"📐 Quantization: {quantization_config.get('tempo_bpm')} BPM, {quantization_config.get('subdivision')} notes"
    )

    # Create mock coordinate client
    mock_client = MockCoordinateClient()

    # Create sequencer with fast settings for testing
    sequencer = QuantizedGeoMidiSequencer(
        coordinate_client=mock_client,
        scale_type="pentatonic",
        base_note=60,
        octave_range=2,
        velocity_min=64,
        velocity_max=100,
        note_duration=0.5,
        auto_create_port=False,  # Don't try to create real MIDI port
        quantization_enabled=True,
        tempo_bpm=160,  # Fast for testing
        subdivision="16th",
        swing=0.1,
        max_queue_size=10,
    )

    # Replace MIDI setup with mock
    def mock_setup_midi():
        sequencer.midi_port = TestMidiOutput()
        return True

    sequencer.setup_midi = mock_setup_midi

    try:
        print("🚀 Starting test...")
        start_time = time.time()

        # Run for a short time
        await asyncio.wait_for(sequencer.run(), timeout=5.0)

    except asyncio.TimeoutError:
        print("⏰ Test completed (timeout)")
    except KeyboardInterrupt:
        print("⏹️  Test interrupted")
    finally:
        await sequencer.cleanup()

        # Print test results
        end_time = time.time()
        duration = end_time - start_time

        print("\n📊 Test Results:")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Coordinates processed: {sequencer.sequence_count}")
        print(
            f"   Notes in queue: {len([n for n in sequencer.note_queue if not n.played])}"
        )
        print(f"   MIDI messages sent: {len(sequencer.midi_port.sent_messages)}")

        if sequencer.midi_port.sent_messages:
            print("   Sample MIDI messages:")
            for msg in sequencer.midi_port.sent_messages[:5]:
                print(f"     {msg}")


async def test_config_loading():
    """Test configuration loading."""
    print("\n⚙️ Testing Configuration Loading")
    print("-" * 30)

    from geo_sequencer.config_manager import SequencerConfig

    config = SequencerConfig()

    print("✅ Configuration loaded successfully")
    print(f"   Scale: {config.get('sequencer', 'scale_type')}")
    print(f"   Tempo: {config.get('quantization', 'tempo_bpm')} BPM")
    print(f"   Subdivision: {config.get('quantization', 'subdivision')}")
    print(f"   Quantization enabled: {config.get('quantization', 'enabled')}")


if __name__ == "__main__":

    async def main():
        await test_config_loading()
        await test_quantized_sequencer()

    asyncio.run(main())
