#!/usr/bin/env python3
"""
Geo MIDI Sequencer
A MIDI sequencer that converts streaming Earth coordinates from the WebSocket client
into MIDI notes for synthesizer control. Coordinates are mapped to musical scales
and sent as MIDI note on/off messages.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, Optional
import mido
from mido import Message
import websockets
from websockets.exceptions import ConnectionClosed


class GeoMidiSequencer:
    """
    A MIDI sequencer that converts geographic coordinates to musical notes.
    Maps latitude to pitch and longitude to timing/velocity parameters.
    """

    def __init__(
        self,
        server_url: str = "ws://localhost:8000/ws",
        midi_port_name: Optional[str] = None,
        scale_type: str = "pentatonic",
        base_note: int = 60,  # Middle C
        octave_range: int = 4,
        velocity_min: int = 64,
        velocity_max: int = 127,
        note_duration: float = 1.0,
        auto_create_port: bool = True,
    ):
        """
        Initialize the Geo MIDI Sequencer.

        Args:
            server_url: WebSocket server URL for coordinate stream
            midi_port_name: Name of MIDI output port (None for auto-detect)
            scale_type: Musical scale ('pentatonic', 'major', 'minor', 'chromatic')
            base_note: Base MIDI note number (60 = Middle C)
            octave_range: Number of octaves to span
            velocity_min: Minimum MIDI velocity
            velocity_max: Maximum MIDI velocity
            note_duration: Duration of each note in seconds
            auto_create_port: Create virtual MIDI port if none found
        """
        self.server_url = server_url
        self.midi_port_name = midi_port_name
        self.scale_type = scale_type
        self.base_note = base_note
        self.octave_range = octave_range
        self.velocity_min = velocity_min
        self.velocity_max = velocity_max
        self.note_duration = note_duration
        self.auto_create_port = auto_create_port

        # MIDI and WebSocket connections
        self.midi_port: Optional[mido.ports.BaseOutput] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None

        # State tracking
        self.is_running = False
        self.current_note: Optional[int] = None
        self.last_coordinate: Optional[Dict[str, float]] = None
        self.sequence_count = 0

        # Musical scales (intervals from root note)
        self.scales = {
            "pentatonic": [0, 2, 4, 7, 9],  # C, D, E, G, A
            "major": [0, 2, 4, 5, 7, 9, 11],  # Major scale
            "minor": [0, 2, 3, 5, 7, 8, 10],  # Natural minor
            "chromatic": list(range(12)),  # All 12 semitones
            "blues": [0, 3, 5, 6, 7, 10],  # Blues scale
            "dorian": [0, 2, 3, 5, 7, 9, 10],  # Dorian mode
        }

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for the sequencer."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("geo_midi.log"),
            ],
        )

    def setup_midi(self) -> bool:
        """
        Setup MIDI output port.

        Returns:
            bool: True if MIDI setup successful, False otherwise
        """
        try:
            # List available MIDI ports
            available_ports = mido.get_output_names()
            self.logger.info(f"Available MIDI ports: {available_ports}")

            if self.midi_port_name and self.midi_port_name in available_ports:
                # Use specified port
                self.midi_port = mido.open_output(self.midi_port_name)
                self.logger.info(f"Connected to MIDI port: {self.midi_port_name}")
            elif available_ports:
                # Use first available port
                self.midi_port = mido.open_output(available_ports[0])
                self.logger.info(f"Connected to MIDI port: {available_ports[0]}")
            elif self.auto_create_port:
                # Create virtual MIDI port
                try:
                    self.midi_port = mido.open_output("Geo Sequencer", virtual=True)
                    self.logger.info("Created virtual MIDI port: 'Geo Sequencer'")
                except Exception as e:
                    self.logger.warning(f"Could not create virtual port: {e}")
                    return False
            else:
                self.logger.error("No MIDI ports available and auto-create disabled")
                return False

            return True

        except Exception as e:
            self.logger.error(f"MIDI setup failed: {e}")
            return False

    def coordinate_to_note(self, latitude: float, longitude: float) -> tuple[int, int]:
        """
        Convert geographic coordinates to MIDI note and velocity.

        Args:
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)

        Returns:
            tuple: (midi_note, velocity)
        """
        # Normalize latitude to 0-1 range
        lat_normalized = (latitude + 90) / 180

        # Normalize longitude to 0-1 range
        lon_normalized = (longitude + 180) / 360

        # Get scale intervals
        scale_intervals = self.scales.get(self.scale_type, self.scales["pentatonic"])
        total_notes = len(scale_intervals) * self.octave_range

        # Map latitude to note index in scale
        note_index = int(lat_normalized * total_notes)
        note_index = min(note_index, total_notes - 1)  # Clamp to valid range

        # Calculate octave and scale degree
        octave = note_index // len(scale_intervals)
        scale_degree = note_index % len(scale_intervals)

        # Calculate final MIDI note
        midi_note = self.base_note + (octave * 12) + scale_intervals[scale_degree]
        midi_note = max(0, min(127, midi_note))  # Clamp to valid MIDI range

        # Map longitude to velocity
        velocity = int(
            self.velocity_min
            + (lon_normalized * (self.velocity_max - self.velocity_min))
        )
        velocity = max(1, min(127, velocity))  # Clamp to valid MIDI range

        return midi_note, velocity

    def send_note_off(self, note: int, channel: int = 0):
        """Send MIDI note off message."""
        if self.midi_port:
            msg = Message("note_off", channel=channel, note=note, velocity=0)
            self.midi_port.send(msg)
            self.logger.debug(f"MIDI Note OFF: {note}")

    def send_note_on(self, note: int, velocity: int, channel: int = 0):
        """Send MIDI note on message."""
        if self.midi_port:
            msg = Message("note_on", channel=channel, note=note, velocity=velocity)
            self.midi_port.send(msg)
            self.logger.debug(f"MIDI Note ON: {note}, Velocity: {velocity}")

    def process_coordinate_data(self, data: Dict[str, Any]):
        """
        Process incoming coordinate data and generate MIDI.

        Args:
            data: Dictionary containing coordinate information
        """
        try:
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            timestamp = data.get("timestamp")

            if latitude is None or longitude is None:
                self.logger.warning("Invalid coordinate data received")
                return

            # Round coordinates to reduce jitter
            latitude = round(latitude, 3)
            longitude = round(longitude, 3)

            self.sequence_count += 1

            # Convert coordinates to MIDI note and velocity
            midi_note, velocity = self.coordinate_to_note(latitude, longitude)

            # Turn off previous note if it exists
            if self.current_note is not None:
                self.send_note_off(self.current_note)

            # Turn on new note
            self.send_note_on(midi_note, velocity)
            self.current_note = midi_note

            # Log the musical mapping
            note_names = [
                "C",
                "C#",
                "D",
                "D#",
                "E",
                "F",
                "F#",
                "G",
                "G#",
                "A",
                "A#",
                "B",
            ]
            note_name = note_names[midi_note % 12]
            octave = midi_note // 12 - 1

            self.logger.info(
                f"[{self.sequence_count:04d}] "
                f"Lat: {latitude:7.3f} → Note: {note_name}{octave} ({midi_note}) | "
                f"Lon: {longitude:8.3f} → Vel: {velocity:3d} | "
                f"Scale: {self.scale_type}"
            )

            # Store current coordinate
            self.last_coordinate = {
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp,
                "midi_note": midi_note,
                "velocity": velocity,
                "note_name": f"{note_name}{octave}",
            }

            # Schedule note off after duration
            asyncio.create_task(self._schedule_note_off(midi_note, self.note_duration))

        except Exception as e:
            self.logger.error(f"Error processing coordinate data: {e}")

    async def _schedule_note_off(self, note: int, delay: float):
        """Schedule a note off message after a delay."""
        await asyncio.sleep(delay)
        if self.current_note == note:  # Only turn off if it's still the current note
            self.send_note_off(note)
            self.current_note = None

    async def connect_websocket(self) -> bool:
        """
        Connect to the WebSocket server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to WebSocket: {self.server_url}")

            self.websocket = await websockets.connect(
                self.server_url, ping_interval=20.0, ping_timeout=10.0
            )

            self.logger.info("Successfully connected to coordinate stream")
            return True

        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            return False

    async def listen_for_coordinates(self):
        """Listen for coordinate data from WebSocket."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    self.process_coordinate_data(data)
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

    async def run(self):
        """Main run loop for the sequencer."""
        self.logger.info("Starting Geo MIDI Sequencer...")

        # Setup MIDI
        if not self.setup_midi():
            self.logger.error("Failed to setup MIDI, exiting")
            return

        # Connect to WebSocket
        if not await self.connect_websocket():
            self.logger.error("Failed to connect to WebSocket, exiting")
            return

        self.is_running = True

        try:
            # Start listening for coordinates
            await self.listen_for_coordinates()
        except KeyboardInterrupt:
            self.logger.info("Sequencer interrupted by user")
        except Exception as e:
            self.logger.error(f"Sequencer error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        self.is_running = False

        # Turn off any remaining notes
        if self.current_note is not None:
            self.send_note_off(self.current_note)

        # Close MIDI port
        if self.midi_port:
            self.midi_port.close()
            self.logger.info("MIDI port closed")

        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.logger.info("WebSocket connection closed")

        self.logger.info(
            f"Sequencer stopped. Total sequences played: {self.sequence_count}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get sequencer statistics."""
        return {
            "sequence_count": self.sequence_count,
            "current_note": self.current_note,
            "last_coordinate": self.last_coordinate,
            "scale_type": self.scale_type,
            "base_note": self.base_note,
            "is_running": self.is_running,
        }


def main():
    """Main function to run the Geo MIDI Sequencer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Geo MIDI Sequencer - Convert coordinates to music"
    )
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws",
        help="WebSocket server URL (default: ws://localhost:8000/ws)",
    )
    parser.add_argument(
        "--midi-port", help="MIDI output port name (auto-detect if not specified)"
    )
    parser.add_argument(
        "--scale",
        default="pentatonic",
        choices=["pentatonic", "major", "minor", "chromatic", "blues", "dorian"],
        help="Musical scale to use (default: pentatonic)",
    )
    parser.add_argument(
        "--base-note",
        type=int,
        default=60,
        help="Base MIDI note number (default: 60 = Middle C)",
    )
    parser.add_argument(
        "--octave-range",
        type=int,
        default=4,
        help="Number of octaves to span (default: 4)",
    )
    parser.add_argument(
        "--note-duration",
        type=float,
        default=1.0,
        help="Duration of each note in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--velocity-min",
        type=int,
        default=64,
        help="Minimum MIDI velocity (default: 64)",
    )
    parser.add_argument(
        "--velocity-max",
        type=int,
        default=127,
        help="Maximum MIDI velocity (default: 127)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create sequencer
    sequencer = GeoMidiSequencer(
        server_url=args.url,
        midi_port_name=args.midi_port,
        scale_type=args.scale,
        base_note=args.base_note,
        octave_range=args.octave_range,
        velocity_min=args.velocity_min,
        velocity_max=args.velocity_max,
        note_duration=args.note_duration,
    )

    try:
        asyncio.run(sequencer.run())
    except Exception as e:
        print(f"Error running sequencer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
