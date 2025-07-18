#!/usr/bin/env python3
"""
Demonstration of different quantization settings
Shows how different subdivisions and tempos affect the timing.
"""

import asyncio
import time


async def demo_quantization_settings():
    """Demonstrate different quantization settings."""
    print("🎵 Quantization Settings Demo")
    print("=" * 50)

    from geo_sequencer.quantized_geo_midi_sequencer import QuantizedGeoMidiSequencer

    class MockClient:
        def __init__(self):
            self.callback = None

        async def run(self):
            # Send a test coordinate
            if self.callback:
                await self.callback(
                    {"latitude": 52.5, "longitude": 13.4, "timestamp": time.time()}
                )
            await asyncio.sleep(2)

    class MockMidi:
        def __init__(self, name):
            self.name = name

        def send(self, msg):
            elapsed = time.time() - start_time
            print(f"  {elapsed:.3f}s: {self.name} - {msg}")

        def close(self):
            pass

    # Test different settings
    test_configs = [
        {"tempo_bpm": 120, "subdivision": "4th", "name": "Slow (4th notes)"},
        {"tempo_bpm": 120, "subdivision": "8th", "name": "Medium (8th notes)"},
        {"tempo_bpm": 120, "subdivision": "16th", "name": "Fast (16th notes)"},
        {
            "tempo_bpm": 160,
            "subdivision": "16th",
            "name": "Very Fast (16th at 160 BPM)",
        },
    ]

    for config in test_configs:
        print(f"\n🎼 Testing: {config['name']}")
        print(
            f"   Tempo: {config['tempo_bpm']} BPM, Subdivision: {config['subdivision']}"
        )

        client = MockClient()
        sequencer = QuantizedGeoMidiSequencer(
            coordinate_client=client,
            auto_create_port=False,
            quantization_enabled=True,
            tempo_bpm=config["tempo_bpm"],
            subdivision=config["subdivision"],
            note_duration=0.5,
        )

        # Mock MIDI setup
        sequencer.setup_midi = lambda: True
        sequencer.midi_port = MockMidi(config["name"])

        start_time = time.time()
        print("   Sending coordinate...")

        try:
            await asyncio.wait_for(sequencer.run(), timeout=2.5)
        except asyncio.TimeoutError:
            pass

        await sequencer.cleanup()


async def demo_config_variations():
    """Show how to modify configuration for different musical styles."""
    print("\n\n🎨 Musical Style Configurations")
    print("=" * 50)

    styles = {
        "Ambient Lightning": {
            "scale_type": "minor",
            "base_note": 36,  # Very low
            "tempo_bpm": 60,
            "subdivision": "4th",
            "note_duration": 8.0,
            "swing": 0.0,
        },
        "Rhythmic Storm": {
            "scale_type": "pentatonic",
            "base_note": 60,
            "tempo_bpm": 140,
            "subdivision": "32nd",
            "note_duration": 0.25,
            "swing": 0.3,
        },
        "Jazz Lightning": {
            "scale_type": "dorian",
            "base_note": 48,
            "tempo_bpm": 120,
            "subdivision": "8th",
            "note_duration": 1.5,
            "swing": 0.4,
        },
        "Electronic Storm": {
            "scale_type": "chromatic",
            "base_note": 72,  # High
            "tempo_bpm": 160,
            "subdivision": "64th",
            "note_duration": 0.1,
            "swing": 0.0,
        },
    }

    for style_name, config in styles.items():
        print(f"\n🎵 {style_name}:")
        print(f"   Scale: {config['scale_type']}")
        print(f"   Base Note: {config['base_note']} (MIDI)")
        print(f"   Timing: {config['tempo_bpm']} BPM, {config['subdivision']} notes")
        print(f"   Note Duration: {config['note_duration']}s")
        print(f"   Swing: {config['swing']}")

        # Calculate timing
        beat_duration = 60.0 / config["tempo_bpm"]
        subdivision_map = {
            "4th": 1.0,
            "8th": 0.5,
            "16th": 0.25,
            "32nd": 0.125,
            "64th": 0.0625,
        }
        interval = beat_duration * subdivision_map.get(config["subdivision"], 0.25)
        print(f"   → Note every {interval:.3f} seconds")


if __name__ == "__main__":

    async def main():
        await demo_quantization_settings()
        await demo_config_variations()

        print("\n\n📝 Next Steps:")
        print("1. Edit config/lightning_sequencer.toml to try different settings")
        print("2. Run: python setup_config.py (for interactive configuration)")
        print("3. Run the lightning sequencer with your settings!")

    asyncio.run(main())
