#!/usr/bin/env python3
"""
Lightning MIDI Sequencer
Real-time MIDI sequencer that converts global lightning strikes from Blitzortung
into musical notes. Each lightning strike worldwide becomes a musical note based
on its geographic coordinates.

Features:
- Configurable via TOML file
- Rhythmic quantization (16th, 32nd, 64th notes)
- Musical scales and velocity mapping
- Real-time lightning data from Blitzortung
"""

import asyncio
import logging
import sys
from pathlib import Path
from geo_sequencer.lightning.blitzortung.coordinate_client_blitzortung_implementation import (
    BlitzortungCoordinateClient,
)
from geo_sequencer.quantized_geo_midi_sequencer import QuantizedGeoMidiSequencer
from geo_sequencer.config_manager import SequencerConfig


async def main():
    """Run the Lightning MIDI Sequencer."""
    print("⚡🎵 Lightning MIDI Sequencer v2.0 🎵⚡")
    print("=" * 60)
    print("Converting real-time global lightning strikes into music!")
    print("Features:")
    print("  • Lightning strikes → Musical notes")
    print("  • Latitude → Musical pitch")
    print("  • Longitude → Volume/velocity")
    print("  • Rhythmic quantization (16th/32nd/64th notes)")
    print("  • Configurable via TOML file")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Load configuration
    config = SequencerConfig()

    # Validate configuration
    if not config.validate_config():
        print("❌ Configuration validation failed")
        return

    # Print current configuration
    config.print_config()

    # Get configuration sections
    sequencer_config = config.get_sequencer_config()
    quantization_config = config.get_quantization_config()
    midi_config = config.get_midi_config()
    blitzortung_config = config.get_blitzortung_config()
    logging_config = config.get_logging_config()

    # Setup logging with configuration
    log_level = getattr(logging, logging_config.get("level", "INFO").upper())
    log_file = logging_config.get("log_file", "lightning_music.log")

    # Make log file path absolute if not already
    if not Path(log_file).is_absolute():
        log_file = str(Path.cwd() / log_file)

    handlers = []
    if logging_config.get("console_output", True):
        handlers.append(logging.StreamHandler(sys.stdout))
    handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    # Create Blitzortung coordinate client with configuration
    blitzortung_client = BlitzortungCoordinateClient(
        reconnect_delay=blitzortung_config.get("reconnect_delay", 5.0),
        max_reconnect_attempts=blitzortung_config.get("max_reconnect_attempts", 10),
    )

    # Create the quantized geo MIDI sequencer with configuration
    sequencer = QuantizedGeoMidiSequencer(
        coordinate_client=blitzortung_client,
        midi_port_name=midi_config.get("port_name") or None,
        scale_type=sequencer_config.get("scale_type", "pentatonic"),
        base_note=sequencer_config.get("base_note", 48),
        octave_range=sequencer_config.get("octave_range", 5),
        velocity_min=sequencer_config.get("velocity_min", 80),
        velocity_max=sequencer_config.get("velocity_max", 127),
        note_duration=sequencer_config.get("note_duration", 2.0),
        auto_create_port=sequencer_config.get("auto_create_port", True),
        # Quantization settings
        quantization_enabled=quantization_config.get("enabled", True),
        tempo_bpm=quantization_config.get("tempo_bpm", 120),
        subdivision=quantization_config.get("subdivision", "16th"),
        swing=quantization_config.get("swing", 0.0),
        max_queue_size=quantization_config.get("max_queue_size", 100),
        midi_channel=midi_config.get("channel", 0),
    )

    try:
        print("🎼 Starting Lightning MIDI Sequencer...")
        print("🔌 Connecting to Blitzortung servers...")
        print("🎹 Setting up MIDI...")

        if quantization_config.get("enabled", True):
            print(
                f"🎵 Quantization: {quantization_config.get('tempo_bpm', 120)} BPM, "
                f"{quantization_config.get('subdivision', '16th')} notes"
            )
        else:
            print("🎵 Playing notes immediately (no quantization)")

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
        print(f"   Queued notes: {stats['queued_notes']}")
        print(f"   Active notes: {stats['active_notes']}")
        print(f"   Scale used: {stats['scale_type']}")
        print(f"   Quantization: {stats['quantization_enabled']}")
        if stats["quantization_enabled"]:
            print(f"   Tempo: {stats['tempo_bpm']} BPM ({stats['subdivision']} notes)")
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
