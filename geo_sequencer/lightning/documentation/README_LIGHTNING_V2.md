# ⚡ Lightning MIDI Sequencer v2.0

Real-time MIDI sequencer that converts global lightning strikes into musical notes with rhythmic quantization.

## ✨ New Features

### 🎵 Rhythmic Quantization
- **Precise timing**: Notes are quantized to musical subdivisions
- **Configurable subdivisions**: 4th, 8th, 16th, 32nd, or 64th notes
- **Swing support**: Add groove with adjustable swing timing
- **Tempo control**: Set BPM (60-200)
- **Note queuing**: Advanced buffering system for smooth playback

### ⚙️ Configuration System
- **TOML configuration files**: Easy-to-edit settings
- **Auto-discovery**: Finds config files in multiple locations
- **Validation**: Built-in configuration validation
- **Defaults**: Works without configuration (uses sensible defaults)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install the required TOML library
pip install tomli
```

### 2. Create Configuration (Optional)
```bash
# Run the setup script to create a configuration file
python setup_config.py
```

### 3. Run the Sequencer
```bash
# Run with configuration
python geo_sequencer/lightning/blitzortung/geo_midi_sequencer_blitzortung_implementation.py
```

## ⚙️ Configuration

The sequencer looks for configuration files in these locations:
1. `config/lightning_sequencer.toml` (relative to project root)
2. `lightning_sequencer.toml` (current directory)
3. `~/.geo_sequencer/lightning_sequencer.toml` (home directory)

### Sample Configuration

```toml
[sequencer]
scale_type = "pentatonic"    # Musical scale: pentatonic, major, minor, blues, etc.
base_note = 48              # Base MIDI note (48=C3, 60=C4)
octave_range = 5            # Number of octaves to span
velocity_min = 80           # Minimum MIDI velocity
velocity_max = 127          # Maximum MIDI velocity
note_duration = 2.0         # Note duration in seconds
auto_create_port = true     # Create virtual MIDI port

[quantization]
enabled = true              # Enable rhythmic quantization
tempo_bpm = 120            # Tempo in beats per minute
subdivision = "16th"        # Note subdivision: 4th, 8th, 16th, 32nd, 64th
swing = 0.0                # Swing amount (0.0 = straight, 0.5 = max swing)
max_queue_size = 100       # Maximum queued notes

[midi]
port_name = ""             # MIDI port name (empty = auto-detect)
channel = 0                # MIDI channel (0-15)

[blitzortung]
reconnect_delay = 5.0      # Reconnection delay in seconds
max_reconnect_attempts = 10 # Maximum reconnection attempts

[logging]
level = "INFO"             # Log level: DEBUG, INFO, WARNING, ERROR
log_file = "lightning_music.log"  # Log file name
console_output = true      # Enable console output
```

## 🎵 Quantization Modes

### Note Subdivisions
- **4th notes**: Quarter note timing (slow, dramatic)
- **8th notes**: Eighth note timing (moderate pace)  
- **16th notes**: Sixteenth note timing (default, good balance)
- **32nd notes**: Thirty-second note timing (fast, rhythmic)
- **64th notes**: Sixty-fourth note timing (very fast, detailed)

### Swing Timing
- **0.0**: Straight timing (no swing)
- **0.1-0.3**: Subtle swing
- **0.4-0.5**: Heavy swing (maximum = 0.5)

### Tempo Guidelines
- **60-80 BPM**: Slow, ambient
- **90-110 BPM**: Moderate, relaxed
- **120-140 BPM**: Standard, energetic (default: 120)
- **150-200 BPM**: Fast, intense

## 🎹 Musical Mapping

### Coordinates → Music
- **Latitude (-90° to +90°)** → **Musical Pitch**
  - North Pole (+90°) = Highest notes
  - Equator (0°) = Middle notes  
  - South Pole (-90°) = Lowest notes

- **Longitude (-180° to +180°)** → **Note Velocity**
  - East (+180°) = Loudest notes
  - Prime Meridian (0°) = Medium volume
  - West (-180°) = Softest notes

### Musical Scales
- **pentatonic**: Traditional 5-note scale (default)
- **major**: Happy, bright 7-note scale
- **minor**: Sad, dark 7-note scale
- **blues**: Bluesy, soulful 6-note scale
- **chromatic**: All 12 semitones
- **dorian**: Modal, jazzy 7-note scale

## 🛠️ Advanced Features

### Configuration Management
```bash
# Validate configuration
python -m geo_sequencer.config_manager --validate config/lightning_sequencer.toml

# Print configuration
python -m geo_sequencer.config_manager --print config/lightning_sequencer.toml

# Create sample configuration
python -m geo_sequencer.config_manager --create-sample
```

### Setup Helper
```bash
# Interactive configuration setup
python setup_config.py
```

## 🎚️ MIDI Setup

### macOS
1. **Virtual MIDI Port**: The sequencer creates "Geo Sequencer" virtual port
2. **DAW Integration**: Connect to Logic Pro, Ableton Live, etc.
3. **Audio Units**: Use with synthesizers and samplers

### DAW Recommendations
- **Ableton Live**: Great for live performance and effects
- **Logic Pro**: Excellent built-in instruments
- **GarageBand**: Simple setup for beginners
- **Reaper**: Lightweight and flexible

## 🔧 Troubleshooting

### No MIDI Output
- Check MIDI port connections
- Verify virtual port creation
- Try different DAW/synthesizer

### Configuration Errors
- Run configuration validation
- Check TOML syntax
- Use setup script to recreate config

### Performance Issues
- Reduce `max_queue_size`
- Increase `subdivision` interval (use 8th instead of 32nd)
- Lower `tempo_bpm`

## 📊 Statistics

The sequencer provides real-time statistics:
- Lightning strikes processed
- Musical sequences played
- Queued notes (quantization buffer)
- Active notes currently playing
- Quantization settings

## 🌍 Data Source

Lightning data comes from **Blitzortung.org**:
- Real-time global lightning detection network
- Community-operated stations worldwide
- Sub-second accuracy
- Covers all continents

## 🎼 Examples

### Ambient Lightning (Slow)
```toml
[sequencer]
scale_type = "minor"
base_note = 36  # Lower octave
note_duration = 4.0

[quantization]
tempo_bpm = 80
subdivision = "4th"
```

### Rhythmic Lightning (Fast)
```toml
[sequencer]
scale_type = "pentatonic"
base_note = 60
note_duration = 0.5

[quantization]  
tempo_bpm = 140
subdivision = "32nd"
swing = 0.2
```

### Immediate Mode (No Quantization)
```toml
[quantization]
enabled = false
```

## 🚨 Known Limitations

- Requires internet connection for lightning data
- MIDI timing precision depends on system performance
- Maximum 100 queued notes (configurable)
- Lightning activity varies by time/season

---

*Convert the power of global lightning into music! ⚡🎵*
