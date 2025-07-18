#!/usr/bin/env python3
"""
Quantized Geo MIDI Sequencer
Enhanced version of the Geo MIDI Sequencer with rhythmic quantization support.
Notes are queued and played at precise musical timing intervals.
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any, Optional, List, Tuple
import mido
from mido import Message
from geo_sequencer.coordinate_client import CoordinateClient


class QuantizedNote:
    """Represents a note scheduled for quantized playback."""

    def __init__(
        self,
        midi_note: int,
        velocity: int,
        duration: float,
        original_timestamp: float,
        latitude: float,
        longitude: float,
    ):
        self.midi_note = midi_note
        self.velocity = velocity
        self.duration = duration
        self.original_timestamp = original_timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.scheduled_time: Optional[float] = None
        self.played = False


class QuantizedGeoMidiSequencer:
    """
    A quantized MIDI sequencer that converts geographic coordinates to musical notes
    with precise rhythmic timing based on musical subdivisions.
    """

    def __init__(
        self,
        coordinate_client: CoordinateClient,
        midi_port_name: Optional[str] = None,
        scale_type: str = "pentatonic",
        base_note: int = 60,
        octave_range: int = 4,
        velocity_min: int = 64,
        velocity_max: int = 127,
        note_duration: float = 1.0,
        auto_create_port: bool = True,
        # Quantization parameters
        quantization_enabled: bool = True,
        tempo_bpm: int = 120,
        subdivision: str = "16th",
        swing: float = 0.0,
        max_queue_size: int = 100,
        midi_channel: int = 0,
    ):
        """
        Initialize the Quantized Geo MIDI Sequencer.

        Args:
            coordinate_client: CoordinateClient instance for streaming coordinates
            midi_port_name: Name of MIDI output port (None for auto-detect)
            scale_type: Musical scale ('pentatonic', 'major', 'minor', 'chromatic')
            base_note: Base MIDI note number (60 = Middle C)
            octave_range: Number of octaves to span
            velocity_min: Minimum MIDI velocity
            velocity_max: Maximum MIDI velocity
            note_duration: Duration of each note in seconds
            auto_create_port: Create virtual MIDI port if none found
            quantization_enabled: Enable rhythmic quantization
            tempo_bpm: Tempo in beats per minute
            subdivision: Note subdivision ('4th', '8th', '16th', '32nd', '64th')
            swing: Swing timing (0.0 = straight, 0.5 = maximum swing)
            max_queue_size: Maximum notes in quantization queue
            midi_channel: MIDI channel (0-15)
        """
        # Basic sequencer parameters
        self.coordinate_client = coordinate_client
        self.midi_port_name = midi_port_name
        self.scale_type = scale_type
        self.base_note = base_note
        self.octave_range = octave_range
        self.velocity_min = velocity_min
        self.velocity_max = velocity_max
        self.note_duration = note_duration
        self.auto_create_port = auto_create_port
        self.midi_channel = midi_channel

        # Quantization parameters
        self.quantization_enabled = quantization_enabled
        self.tempo_bpm = tempo_bpm
        self.subdivision = subdivision
        self.swing = swing
        self.max_queue_size = max_queue_size

        # Setup logging first
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

        # Calculate timing intervals
        self._calculate_timing()

        # MIDI connection
        self.midi_port: Optional[mido.ports.BaseOutput] = None

        # State tracking
        self.is_running = False
        self.sequence_count = 0
        self.last_coordinate: Optional[Dict[str, float]] = None

        # Quantization state
        self.note_queue: List[QuantizedNote] = []
        self.active_notes: List[Tuple[int, float]] = []  # (note, end_time)
        self.sequencer_start_time = 0.0
        self.last_quantized_time = 0.0

        # Musical scales
        self.scales = {
            "pentatonic": [0, 2, 4, 7, 9],
            "major": [0, 2, 4, 5, 7, 9, 11],
            "minor": [0, 2, 3, 5, 7, 8, 10],
            "chromatic": list(range(12)),
            "blues": [0, 3, 5, 6, 7, 10],
            "dorian": [0, 2, 3, 5, 7, 9, 10],
        }

    def _calculate_timing(self):
        """Calculate timing intervals based on tempo and subdivision."""
        # Beat duration in seconds
        self.beat_duration = 60.0 / self.tempo_bpm

        # Subdivision multipliers
        subdivision_map = {
            "4th": 1.0,  # Quarter note
            "8th": 0.5,  # Eighth note
            "16th": 0.25,  # Sixteenth note
            "32nd": 0.125,  # Thirty-second note
            "64th": 0.0625,  # Sixty-fourth note
        }

        multiplier = subdivision_map.get(self.subdivision, 0.25)
        self.quantize_interval = self.beat_duration * multiplier

        self.logger.info(
            f"Quantization: {self.tempo_bpm} BPM, {self.subdivision} notes, "
            f"interval: {self.quantize_interval:.3f}s"
        )

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
        """Setup MIDI output port."""
        try:
            available_ports = mido.get_output_names()
            self.logger.info(f"Available MIDI ports: {available_ports}")

            if self.midi_port_name and self.midi_port_name in available_ports:
                self.midi_port = mido.open_output(self.midi_port_name)
                self.logger.info(f"Connected to MIDI port: {self.midi_port_name}")
            elif available_ports:
                self.midi_port = mido.open_output(available_ports[0])
                self.logger.info(f"Connected to MIDI port: {available_ports[0]}")
            elif self.auto_create_port:
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
        """Convert geographic coordinates to MIDI note and velocity."""
        # Normalize latitude to 0-1 range
        lat_normalized = (latitude + 90) / 180

        # Normalize longitude to 0-1 range
        lon_normalized = (longitude + 180) / 360

        # Get scale intervals
        scale_intervals = self.scales.get(self.scale_type, self.scales["pentatonic"])
        total_notes = len(scale_intervals) * self.octave_range

        # Map latitude to note index in scale
        note_index = int(lat_normalized * total_notes)
        note_index = min(note_index, total_notes - 1)

        # Calculate octave and scale degree
        octave = note_index // len(scale_intervals)
        scale_degree = note_index % len(scale_intervals)

        # Calculate final MIDI note
        midi_note = self.base_note + (octave * 12) + scale_intervals[scale_degree]
        midi_note = max(0, min(127, midi_note))

        # Map longitude to velocity
        velocity = int(
            self.velocity_min
            + (lon_normalized * (self.velocity_max - self.velocity_min))
        )
        velocity = max(1, min(127, velocity))

        return midi_note, velocity

    def _get_next_quantized_time(self, current_time: float) -> float:
        """Calculate the next quantized beat time."""
        elapsed = current_time - self.sequencer_start_time
        beat_number = int(elapsed / self.quantize_interval) + 1
        next_beat_time = self.sequencer_start_time + (
            beat_number * self.quantize_interval
        )

        # Apply swing if enabled
        if self.swing > 0 and beat_number % 2 == 0:  # Apply swing to off-beats
            swing_offset = self.quantize_interval * self.swing * 0.5
            next_beat_time += swing_offset

        return next_beat_time

    def _add_note_to_queue(self, note: QuantizedNote):
        """Add a note to the quantization queue."""
        if len(self.note_queue) >= self.max_queue_size:
            # Remove oldest note if queue is full
            removed = self.note_queue.pop(0)
            self.logger.debug(f"Queue full, removed note: {removed.midi_note}")

        # Schedule the note for the next quantized time
        current_time = time.time()
        note.scheduled_time = self._get_next_quantized_time(current_time)
        self.note_queue.append(note)

        self.logger.debug(
            f"Queued note {note.midi_note} for {note.scheduled_time:.3f} "
            f"(delay: {note.scheduled_time - current_time:.3f}s)"
        )

    def send_note_off(self, note: int):
        """Send MIDI note off message."""
        if self.midi_port:
            msg = Message("note_off", channel=self.midi_channel, note=note, velocity=0)
            self.midi_port.send(msg)
            self.logger.debug(f"MIDI Note OFF: {note}")

    def send_note_on(self, note: int, velocity: int):
        """Send MIDI note on message."""
        if self.midi_port:
            msg = Message(
                "note_on", channel=self.midi_channel, note=note, velocity=velocity
            )
            self.midi_port.send(msg)
            self.logger.debug(f"MIDI Note ON: {note}, Velocity: {velocity}")

    async def _play_scheduled_notes(self):
        """Play notes that are scheduled for the current time."""
        current_time = time.time()
        notes_to_play = []

        # Find notes ready to play
        for note in self.note_queue:
            if (
                not note.played
                and note.scheduled_time
                and current_time >= note.scheduled_time
            ):
                notes_to_play.append(note)

        # Play the notes
        for note in notes_to_play:
            self.send_note_on(note.midi_note, note.velocity)
            note.played = True

            # Schedule note off
            note_off_time = current_time + note.duration
            self.active_notes.append((note.midi_note, note_off_time))

            # Log the played note
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
            note_name = note_names[note.midi_note % 12]
            octave = note.midi_note // 12 - 1

            self.logger.info(
                f"🎵 [{self.sequence_count:04d}] Quantized: "
                f"Lat: {note.latitude:7.3f} → {note_name}{octave} ({note.midi_note}) | "
                f"Lon: {note.longitude:8.3f} → Vel: {note.velocity:3d} | "
                f"Delay: {current_time - note.original_timestamp:.3f}s"
            )

        # Remove played notes from queue
        self.note_queue = [note for note in self.note_queue if not note.played]

    async def _stop_finished_notes(self):
        """Stop notes that have reached their duration."""
        current_time = time.time()
        notes_to_stop = []

        for note, end_time in self.active_notes:
            if current_time >= end_time:
                self.send_note_off(note)
                notes_to_stop.append((note, end_time))

        # Remove stopped notes
        for note_info in notes_to_stop:
            self.active_notes.remove(note_info)

    async def process_coordinate_data(self, data: Dict[str, Any]):
        """Process incoming coordinate data and queue for quantized playback."""
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

            # Note names for display
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

            if self.quantization_enabled:
                # Create quantized note
                quantized_note = QuantizedNote(
                    midi_note=midi_note,
                    velocity=velocity,
                    duration=self.note_duration,
                    original_timestamp=time.time(),
                    latitude=latitude,
                    longitude=longitude,
                )

                # Add to quantization queue
                self._add_note_to_queue(quantized_note)
            else:
                # Play immediately (original behavior)
                self.send_note_on(midi_note, velocity)

                note_name = note_names[midi_note % 12]
                octave = midi_note // 12 - 1

                self.logger.info(
                    f"🎵 [{self.sequence_count:04d}] Immediate: "
                    f"Lat: {latitude:7.3f} → {note_name}{octave} ({midi_note}) | "
                    f"Lon: {longitude:8.3f} → Vel: {velocity:3d}"
                )

                # Schedule note off
                asyncio.create_task(
                    self._schedule_note_off(midi_note, self.note_duration)
                )

            # Store current coordinate
            self.last_coordinate = {
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp,
                "midi_note": midi_note,
                "velocity": velocity,
                "note_name": f"{note_names[midi_note % 12]}{midi_note // 12 - 1}",
            }

        except Exception as e:
            self.logger.error(f"Error processing coordinate data: {e}")

    async def _schedule_note_off(self, note: int, delay: float):
        """Schedule a note off message after a delay (for immediate mode)."""
        await asyncio.sleep(delay)
        self.send_note_off(note)

    async def _quantization_loop(self):
        """Main quantization loop that handles scheduled note playback."""
        while self.is_running:
            try:
                await self._play_scheduled_notes()
                await self._stop_finished_notes()

                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.01)  # 10ms precision

            except Exception as e:
                self.logger.error(f"Error in quantization loop: {e}")

    async def run(self):
        """Main run loop for the sequencer."""
        self.logger.info("Starting Quantized Geo MIDI Sequencer...")

        if self.quantization_enabled:
            self.logger.info(
                f"Quantization enabled: {self.tempo_bpm} BPM, {self.subdivision} notes"
            )
        else:
            self.logger.info("Quantization disabled: immediate playback")

        # Setup MIDI
        if not self.setup_midi():
            self.logger.error("Failed to setup MIDI, exiting")
            return

        # Set this sequencer as the callback for coordinate data
        self.coordinate_client.callback = self.process_coordinate_data

        self.is_running = True
        self.sequencer_start_time = time.time()

        try:
            # Start quantization loop if enabled
            quantization_task = None
            if self.quantization_enabled:
                quantization_task = asyncio.create_task(self._quantization_loop())

            # Start the coordinate client
            await self.coordinate_client.run()

        except KeyboardInterrupt:
            self.logger.info("Sequencer interrupted by user")
        except Exception as e:
            self.logger.error(f"Sequencer error: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        self.is_running = False

        # Turn off all active notes
        for note, _ in self.active_notes:
            self.send_note_off(note)

        # Close MIDI port
        if self.midi_port:
            self.midi_port.close()
            self.logger.info("MIDI port closed")

        queued_notes = len([n for n in self.note_queue if not n.played])
        self.logger.info(
            f"Sequencer stopped. Sequences: {self.sequence_count}, "
            f"Queued notes: {queued_notes}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get sequencer statistics."""
        queued_notes = len([n for n in self.note_queue if not n.played])
        return {
            "sequence_count": self.sequence_count,
            "queued_notes": queued_notes,
            "active_notes": len(self.active_notes),
            "last_coordinate": self.last_coordinate,
            "scale_type": self.scale_type,
            "base_note": self.base_note,
            "quantization_enabled": self.quantization_enabled,
            "tempo_bpm": self.tempo_bpm,
            "subdivision": self.subdivision,
            "is_running": self.is_running,
        }
