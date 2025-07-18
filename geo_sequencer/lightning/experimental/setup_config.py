#!/usr/bin/env python3
"""
Configuration Setup Script for Lightning MIDI Sequencer
Helper script to create and manage configuration files.
"""

import sys
from pathlib import Path

# Add the geo_sequencer package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from geo_sequencer.config_manager import SequencerConfig


def main():
    """Main configuration setup interface."""
    print("⚙️  Lightning MIDI Sequencer Configuration Setup")
    print("=" * 60)

    while True:
        print("\nWhat would you like to do?")
        print("1. Create sample configuration file")
        print("2. Validate existing configuration")
        print("3. Print current configuration")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            create_config()
        elif choice == "2":
            validate_config()
        elif choice == "3":
            print_config()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


def create_config():
    """Create a new configuration file."""
    print("\n📝 Creating Configuration File")
    print("-" * 30)

    default_path = "config/lightning_sequencer.toml"
    custom_path = input(
        f"Enter path for config file (default: {default_path}): "
    ).strip()

    if not custom_path:
        custom_path = default_path

    # Create directory if it doesn't exist
    config_dir = Path(custom_path).parent
    config_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Create configuration with defaults and save
        config = SequencerConfig()
        config.save_config(custom_path)
        print(f"✅ Configuration file created: {custom_path}")

        # Ask if user wants to customize settings
        customize = (
            input("\nWould you like to customize the settings now? (y/n): ")
            .strip()
            .lower()
        )
        if customize in ["y", "yes"]:
            customize_settings(custom_path)

    except Exception as e:
        print(f"❌ Error creating config file: {e}")


def validate_config():
    """Validate an existing configuration file."""
    print("\n🔍 Validating Configuration")
    print("-" * 30)

    config_path = input("Enter path to configuration file: ").strip()

    if not config_path:
        print("❌ No path provided")
        return

    if not Path(config_path).exists():
        print(f"❌ File not found: {config_path}")
        return

    try:
        config = SequencerConfig(config_path)
        if config.validate_config():
            print("✅ Configuration is valid!")
        else:
            print("❌ Configuration has errors (see above)")
    except Exception as e:
        print(f"❌ Error validating config: {e}")


def print_config():
    """Print current configuration."""
    print("\n📋 Current Configuration")
    print("-" * 30)

    config_path = input(
        "Enter path to configuration file (or press Enter for default): "
    ).strip()

    try:
        if config_path:
            config = SequencerConfig(config_path)
        else:
            config = SequencerConfig()  # Will search default locations

        config.print_config()
    except Exception as e:
        print(f"❌ Error reading config: {e}")


def customize_settings(config_path: str):
    """Interactive settings customization."""
    print("\n🎛️  Customize Settings")
    print("-" * 30)
    print("Note: For now, please edit the configuration file manually.")
    print(f"Config file location: {config_path}")
    print("\nKey settings you might want to adjust:")
    print("  • [sequencer] scale_type: 'pentatonic', 'major', 'minor', 'blues'")
    print("  • [sequencer] base_note: MIDI note number (48=C3, 60=C4)")
    print("  • [quantization] enabled: true/false")
    print("  • [quantization] tempo_bpm: 60-200 BPM")
    print("  • [quantization] subdivision: '16th', '32nd', '64th'")
    print("  • [midi] channel: 0-15")


if __name__ == "__main__":
    main()
