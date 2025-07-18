#!/usr/bin/env python3
"""
Lightning MIDI Sequencer
Real-time MIDI sequencer that converts global lightning strikes from Blitzortung
into musical notes. Each lightning strike worldwide becomes a musical note based
on its geographic coordinates.
"""

import asyncio
import logging
import sys
from geo_sequencer.lightning.blitzortung.coordinate_client_blitzortung_implementation import (
    BlitzortungCoordinateClient,
)
from geo_sequencer.geo_midi_sequencer import GeoMidiSequencer


async def main():
    """Run the Lightning MIDI Sequencer."""
    print("⚡🎵 Lightning MIDI Sequencer 🎵⚡")
    print("=" * 60)
    print("Converting real-time global lightning strikes into music!")
    print("Each lightning strike worldwide becomes a musical note:")
    print("  • Latitude → Musical pitch (note)")
    print("  • Longitude → Volume/velocity")
    print("  • Lightning timing → Musical rhythm")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                "/Users/nilsgies/Documents/Projects/Other/geo_sequencer/lightning_music.log"
            ),
        ],
    )

    # Create Blitzortung coordinate client
    blitzortung_client = BlitzortungCoordinateClient()

    # Create the geo MIDI sequencer with Blitzortung as the coordinate source
    sequencer = GeoMidiSequencer(
        coordinate_client=blitzortung_client,
        scale_type="pentatonic",  # Pentatonic sounds nice for lightning
        base_note=48,  # Lower octave for dramatic effect
        octave_range=5,  # Wide range for global lightning
        velocity_min=80,  # Lightning should be audible!
        velocity_max=127,  # Maximum impact
        note_duration=2.0,  # Longer notes for lightning strikes
        auto_create_port=True,
    )

    try:
        print("🎼 Starting Lightning MIDI Sequencer...")
        print("🔌 Connecting to Blitzortung servers...")
        print("🎹 Setting up MIDI...")
        print()

        await sequencer.run()

    except KeyboardInterrupt:
        print("\n\n⏹️  Lightning MIDI Sequencer stopped by user")

        # Show final statistics
        stats = sequencer.get_stats()
        client_stats = blitzortung_client.get_stats()

        print("\n📊 Final Statistics:")
        print(f"   Lightning strikes processed: {client_stats['strike_count']}")
        print(f"   Musical sequences played: {stats['sequence_count']}")
        print(f"   Scale used: {stats['scale_type']}")
        print(f"   Connected to: {client_stats['current_host']}.blitzortung.org")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Lightning MIDI Sequencer error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start Lightning MIDI Sequencer: {e}")
        sys.exit(1)
