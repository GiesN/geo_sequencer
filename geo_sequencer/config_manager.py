#!/usr/bin/env python3
"""
Configuration Manager for Geo MIDI Sequencer
Handles loading and managing configuration settings from TOML files.
"""

from pathlib import Path
from typing import Dict, Any, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        tomllib = None


class SequencerConfig:
    """Configuration manager for the Geo MIDI Sequencer."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file. If None, searches for default locations.
        """
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}
        self._load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find the configuration file in default locations."""
        # Possible configuration file locations
        search_paths = [
            # User-specified path
            self.config_path,
            # Current directory
            "lightning_sequencer.toml",
            "config.toml",
            # Config directory relative to current working directory
            "config/lightning_sequencer.toml",
            # Config directory relative to script location
            Path(__file__).parent.parent.parent / "config" / "lightning_sequencer.toml",
            # Home directory
            Path.home() / ".geo_sequencer" / "lightning_sequencer.toml",
        ]

        for path in search_paths:
            if path and Path(path).exists():
                return str(path)

        return None

    def _load_config(self):
        """Load configuration from TOML file."""
        if tomllib is None:
            print("⚠️  TOML library not available, using default settings")
            print("Install tomli with: pip install tomli")
            self._load_defaults()
            return

        config_file = self._find_config_file()

        if not config_file:
            print("⚠️  No configuration file found, using default settings")
            self._load_defaults()
            return

        try:
            with open(config_file, "rb") as f:
                self.config_data = tomllib.load(f)
            print(f"✅ Loaded configuration from: {config_file}")
        except Exception as e:
            print(f"❌ Error loading config file {config_file}: {e}")
            print("Using default settings...")
            self._load_defaults()

    def _load_defaults(self):
        """Load default configuration values."""
        self.config_data = {
            "sequencer": {
                "scale_type": "pentatonic",
                "base_note": 48,
                "octave_range": 5,
                "velocity_min": 80,
                "velocity_max": 127,
                "note_duration": 2.0,
                "auto_create_port": True,
            },
            "quantization": {
                "enabled": True,
                "tempo_bpm": 120,
                "subdivision": "16th",
                "swing": 0.0,
                "max_queue_size": 100,
            },
            "midi": {
                "port_name": "",
                "channel": 0,
            },
            "blitzortung": {
                "reconnect_delay": 5.0,
                "max_reconnect_attempts": 10,
            },
            "logging": {
                "level": "INFO",
                "log_file": "lightning_music.log",
                "console_output": True,
            },
        }

    def get(self, section: str, key: str, default=None):
        """
        Get a configuration value.

        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config_data.get(section, {}).get(key, default)

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.

        Args:
            section: Configuration section name

        Returns:
            Dictionary containing all keys in the section
        """
        return self.config_data.get(section, {})

    def get_sequencer_config(self) -> Dict[str, Any]:
        """Get sequencer-specific configuration."""
        return self.get_section("sequencer")

    def get_quantization_config(self) -> Dict[str, Any]:
        """Get quantization-specific configuration."""
        return self.get_section("quantization")

    def get_midi_config(self) -> Dict[str, Any]:
        """Get MIDI-specific configuration."""
        return self.get_section("midi")

    def get_blitzortung_config(self) -> Dict[str, Any]:
        """Get Blitzortung client configuration."""
        return self.get_section("blitzortung")

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get_section("logging")

    def save_config(self, output_path: Optional[str] = None):
        """
        Save current configuration to a TOML file.
        Note: This requires the 'tomli-w' package for writing TOML files.

        Args:
            output_path: Path to save the configuration file
        """
        try:
            import tomli_w

            if not output_path:
                output_path = self.config_path or "lightning_sequencer.toml"

            with open(output_path, "wb") as f:
                tomli_w.dump(self.config_data, f)

            print(f"✅ Configuration saved to: {output_path}")
        except ImportError:
            print("❌ Cannot save config: 'tomli-w' package not installed")
            print("Install with: pip install tomli-w")
        except Exception as e:
            print(f"❌ Error saving config: {e}")

    def validate_config(self) -> bool:
        """
        Validate the configuration values.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        errors = []

        # Validate sequencer settings
        sequencer = self.get_section("sequencer")
        if not 0 <= sequencer.get("base_note", 60) <= 127:
            errors.append("base_note must be between 0 and 127")

        if not 1 <= sequencer.get("velocity_min", 64) <= 127:
            errors.append("velocity_min must be between 1 and 127")

        if not 1 <= sequencer.get("velocity_max", 127) <= 127:
            errors.append("velocity_max must be between 1 and 127")

        if sequencer.get("velocity_min", 64) > sequencer.get("velocity_max", 127):
            errors.append("velocity_min cannot be greater than velocity_max")

        # Validate quantization settings
        quantization = self.get_section("quantization")
        valid_subdivisions = ["4th", "8th", "16th", "32nd", "64th"]
        if quantization.get("subdivision") not in valid_subdivisions:
            errors.append(f"subdivision must be one of: {valid_subdivisions}")

        if not 60 <= quantization.get("tempo_bpm", 120) <= 200:
            errors.append("tempo_bpm should be between 60 and 200")

        # Validate MIDI settings
        midi = self.get_section("midi")
        if not 0 <= midi.get("channel", 0) <= 15:
            errors.append("MIDI channel must be between 0 and 15")

        if errors:
            print("❌ Configuration validation errors:")
            for error in errors:
                print(f"   • {error}")
            return False

        print("✅ Configuration validation passed")
        return True

    def print_config(self):
        """Print the current configuration in a readable format."""
        print("\n📋 Current Configuration:")
        print("=" * 50)

        for section_name, section_data in self.config_data.items():
            print(f"\n[{section_name}]")
            for key, value in section_data.items():
                print(f"  {key} = {value}")

        print("=" * 50)


def create_sample_config(output_path: str = "lightning_sequencer.toml"):
    """
    Create a sample configuration file with all available options.

    Args:
        output_path: Path where to save the sample configuration
    """
    config = SequencerConfig()
    config.save_config(output_path)
    print(f"📝 Sample configuration created at: {output_path}")


if __name__ == "__main__":
    # Command-line interface for configuration management
    import argparse

    parser = argparse.ArgumentParser(description="Geo MIDI Sequencer Configuration")
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create a sample configuration file",
    )
    parser.add_argument(
        "--validate", metavar="CONFIG_FILE", help="Validate a configuration file"
    )
    parser.add_argument(
        "--print", metavar="CONFIG_FILE", help="Print configuration contents"
    )

    args = parser.parse_args()

    if args.create_sample:
        create_sample_config()
    elif args.validate:
        config = SequencerConfig(args.validate)
        config.validate_config()
    elif args.print:
        config = SequencerConfig(args.print)
        config.print_config()
    else:
        parser.print_help()
