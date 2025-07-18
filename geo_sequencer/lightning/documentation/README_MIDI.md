# Geo MIDI Sequencer

A musical sequencer that converts streaming Earth coordinates from a WebSocket into MIDI notes, creating a real-time sonification of geographic data.

## Features

🎵 **Musical Mapping**
- Converts latitude to musical pitch using configurable scales
- Maps longitude to MIDI velocity (note intensity)
- Supports multiple musical scales: pentatonic, major, minor, blues, chromatic, dorian

🎹 **MIDI Output**
- Connects to hardware/software synthesizers via MIDI
- Auto-detects available MIDI ports
- Can create virtual MIDI ports automatically
- Configurable note duration and velocity ranges

🌍 **Real-time Coordination**
- Streams coordinates from WebSocket server
- Rounds coordinates to reduce jitter
- Provides detailed logging of coordinate-to-music mapping

## Installation

### 1. Install Dependencies

```bash
# Install MIDI and WebSocket dependencies
pip install mido python-rtmidi websockets

# Or use the provided requirements file
pip install -r midi_requirements.txt

# Or run the setup script
python setup_midi.py
```

### 2. System Requirements

**macOS:**
- No additional setup required for virtual MIDI ports

**Linux:**
- Install ALSA development headers: `sudo apt-get install libasound2-dev`
- Install PortMidi: `sudo apt-get install libportmidi-dev`

**Windows:**
- Windows MIDI should work out of the box
- Consider installing loopMIDI for virtual MIDI ports

## Usage

### Basic Usage

1. **Start the coordinate server:**
   ```bash
   python dummy_websocket.py
   ```

2. **Run the MIDI sequencer:**
   ```bash
   python geo_midi_sequencer.py
   ```

### Advanced Configuration

```bash
python geo_midi_sequencer.py \
  --scale blues \
  --base-note 48 \
  --octave-range 3 \
  --note-duration 2.0 \
  --velocity-min 80 \
  --velocity-max 127 \
  --verbose
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url` | `ws://localhost:8000/ws` | WebSocket server URL |
| `--midi-port` | Auto-detect | Specific MIDI port name |
| `--scale` | `pentatonic` | Musical scale (pentatonic, major, minor, blues, chromatic, dorian) |
| `--base-note` | `60` | Base MIDI note (60 = Middle C) |
| `--octave-range` | `4` | Number of octaves to span |
| `--note-duration` | `1.0` | Duration of each note in seconds |
| `--velocity-min` | `64` | Minimum MIDI velocity |
| `--velocity-max` | `127` | Maximum MIDI velocity |
| `--verbose` | `False` | Enable detailed logging |

## Musical Mapping

### Coordinate to Music Translation

**Latitude → Pitch:**
- Latitude range (-90° to 90°) maps to musical notes across specified octaves
- Uses configurable musical scales for harmonic results
- Northern latitudes = higher pitches, Southern latitudes = lower pitches

**Longitude → Velocity:**
- Longitude range (-180° to 180°) maps to MIDI velocity (note intensity)
- Eastern longitudes = louder notes, Western longitudes = softer notes

### Musical Scales

- **Pentatonic:** C-D-E-G-A (5 notes, very harmonic)
- **Major:** C-D-E-F-G-A-B (7 notes, bright sound)
- **Minor:** C-D-Eb-F-G-Ab-Bb (7 notes, darker sound)
- **Blues:** C-Eb-F-Gb-G-Bb (6 notes, bluesy feel)
- **Chromatic:** All 12 semitones (full range)
- **Dorian:** C-D-Eb-F-G-A-Bb (modal sound)

## Examples

### Ambient Soundscape
```bash
python geo_midi_sequencer.py --scale pentatonic --base-note 36 --note-duration 3.0
```

### Rhythmic Sequence
```bash
python geo_midi_sequencer.py --scale blues --note-duration 0.5 --velocity-min 100
```

### High-pitched Melody
```bash
python geo_midi_sequencer.py --scale major --base-note 72 --octave-range 2
```

## MIDI Setup

### Connect to Hardware Synthesizer
1. Connect MIDI interface to computer
2. Run sequencer with specific port: `--midi-port "Your MIDI Device"`

### Connect to Software Synthesizer
1. Install software like GarageBand, Logic, Ableton Live, or free options like FluidSynth
2. Create virtual MIDI connection or use available MIDI ports
3. Route sequencer output to your software

### Virtual MIDI Ports
The sequencer can automatically create a virtual MIDI port called "Geo Sequencer" that other software can connect to.

## Output Format

The sequencer logs musical events in this format:
```
[0001] Lat:  45.123 → Note: C4 (60) | Lon: -122.456 → Vel: 89 | Scale: pentatonic
```

Log files are saved to `geo_midi.log` for analysis.

## Integration Examples

### With DAW Software
1. Set up virtual MIDI routing
2. Create a software instrument track
3. Set input to "Geo Sequencer" MIDI port
4. Record the live performance

### With Hardware Modular Synths
1. Connect MIDI-to-CV converter
2. Route pitch CV to oscillator
3. Route velocity CV to VCA or filter
4. Enjoy the geographic soundscape!

## Troubleshooting

**No MIDI ports found:**
- Run `python -c "import mido; print(mido.get_output_names())"` to check available ports
- Install virtual MIDI software like loopMIDI (Windows) or IAC Driver (macOS)

**Connection refused:**
- Ensure the WebSocket server is running: `python dummy_websocket.py`
- Check that port 8000 is not blocked by firewall

**No sound:**
- Verify MIDI connections to synthesizer
- Check that synthesizer is receiving on correct MIDI channel (default: channel 0)
- Ensure synthesizer volume is up

## Files

- `geo_midi_sequencer.py` - Main MIDI sequencer application
- `midi_requirements.txt` - Python dependencies
- `setup_midi.py` - Automated setup script
- `geo_midi.log` - Runtime log file (created automatically)

## Contributing

Feel free to extend the musical mapping algorithms, add new scales, or implement additional MIDI features like:
- Chord generation
- Multiple MIDI channels
- Program change messages
- Control change messages for filter sweeps
- Tempo synchronization
