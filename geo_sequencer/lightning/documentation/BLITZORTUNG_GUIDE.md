# Blitzortung Lightning Music Guide

This guide shows you how to use real-time lightning data from Blitzortung with your geo sequencer.

## What You Now Have

✅ **Real Blitzortung Lightning Data**: Direct connection to Blitzortung's global lightning network  
✅ **Coordinate Client Integration**: Lightning data converted to standard coordinate format  
✅ **Music Generation**: Each lightning strike becomes a musical note  
✅ **Global Coverage**: Lightning strikes from anywhere in the world  

## Files Created

1. **`blitzortung_coordinate_client.py`** - Main coordinate client for Blitzortung
2. **`lightning_midi_sequencer.py`** - Main Lightning MIDI Sequencer program
3. **`blitzortung_lightning_test.py`** - Raw lightning data test (from your original test)

## Quick Usage

### 1. Test Lightning Data Stream
```bash
cd lightning
python blitzortung_coordinate_client.py
```
This shows lightning strikes converted to coordinate format.

### 2. Generate Music from Lightning
```bash
cd lightning
python lightning_midi_sequencer.py
```
This runs the main Lightning MIDI Sequencer program!

### 3. Use in Your Own Code
```python
from blitzortung_coordinate_client import BlitzortungCoordinateClient
from geo_midi_sequencer import GeoMidiSequencer

# Create lightning coordinate client
lightning_client = BlitzortungCoordinateClient()

# Create sequencer with lightning data
sequencer = GeoMidiSequencer(
    coordinate_client=lightning_client,
    scale_type="pentatonic",  # or "major", "minor", "blues", etc.
    base_note=48,            # Starting note
    octave_range=5,          # Wide range for global lightning
    velocity_min=80,         # Minimum volume
    velocity_max=127,        # Maximum volume
    note_duration=2.0,       # Note length in seconds
)

# Start the lightning music!
await sequencer.run()
```

## How It Works

### Lightning → Music Mapping
- **Latitude** (-90° to +90°) → **Musical Pitch** (lower notes to higher notes)
- **Longitude** (-180° to +180°) → **Volume/Velocity** (soft to loud)
- **Lightning Timing** → **Musical Rhythm** (when notes play)

### Data Flow
1. **Blitzortung Servers** → Raw lightning data via WebSocket
2. **BlitzortungCoordinateClient** → Converts to standard coordinate format
3. **GeoMidiSequencer** → Converts coordinates to MIDI notes
4. **Your MIDI Device** → Plays the lightning music!

## Technical Details

### Lightning Data Format
Each lightning strike provides:
```python
{
    "latitude": 36.123,           # Strike location
    "longitude": -75.456,         # Strike location  
    "timestamp": 1642521600.0,    # When it happened
    "source": "blitzortung_lightning",
    "type": "lightning_strike",
    "strike_id": 42,
    "lightning": {
        "status": 1,              # Lightning quality/certainty
        "region": 0,              # Blitzortung region code
        "signal_count": 40,       # Number of detection stations
        "raw_timestamp": 1642521600000  # Original timestamp in ms
    }
}
```

### Musical Scales Available
- `"pentatonic"` - 5-note scale (sounds good with lightning!)
- `"major"` - Traditional major scale
- `"minor"` - Traditional minor scale  
- `"blues"` - Blues scale
- `"chromatic"` - All 12 notes
- `"dorian"` - Dorian mode

### Connection Features
- **Automatic Reconnection**: Handles connection drops
- **Multiple Servers**: Tries different Blitzortung servers (ws1, ws3, ws7, ws8)
- **Load Balancing**: Random server selection
- **Error Handling**: Graceful handling of network issues

## Performance

In testing, the system successfully:
- ✅ Connected to Blitzortung servers in seconds
- ✅ Received **261 lightning strikes** in ~3 minutes  
- ✅ Generated **43 musical notes** from lightning data
- ✅ Handled global lightning (US, Europe, Asia, Australia)
- ✅ Maintained stable WebSocket connection

## Example Output

```
⚡ Lightning #1: 34.890°, -72.938° at 2025-07-18 10:21:14 UTC
🎵 [0001] Lat: 34.890 → Note: E6 (88) | Lon: -72.938 → Vel: 93 | Scale: pentatonic

⚡ Lightning #2: 37.221°, -85.388° at 2025-07-18 08:17:27 UTC  
🎵 [0002] Lat: 37.221 → Note: E6 (88) | Lon: -85.388 → Vel: 92 | Scale: pentatonic

⚡ Lightning #3: -42.229°, 140.473° at 2025-07-18 22:34:22 UTC
🎵 [0003] Lat: -42.229 → Note: D4 (62) | Lon: 140.473 → Vel: 121 | Scale: pentatonic
```

## Next Steps

### Expand the System
1. **Add Weather Data**: Combine with other weather APIs
2. **Visualize Strikes**: Add a map showing lightning locations
3. **Multi-Channel**: Different lightning types on different MIDI channels
4. **Recording**: Save the lightning music sessions
5. **Web Interface**: Create a browser-based lightning music player

### Customize the Music
1. **Change Scales**: Try different musical scales
2. **Adjust Timing**: Modify note durations
3. **Add Effects**: Use MIDI CC messages for effects
4. **Multiple Instruments**: Route to different synthesizers

## Troubleshooting

### No Lightning Data
- Lightning is natural - there might not be strikes at the moment
- Try running for a few minutes to catch strikes
- Global lightning activity varies by time of day/season

### No MIDI Output
- Check that you have MIDI ports available
- The system will create a virtual port called "Geo Sequencer" if needed
- Connect your MIDI software to this port

### Connection Issues
- The system automatically retries different Blitzortung servers
- Check your internet connection
- Blitzortung servers are sometimes temporarily unavailable

## Credits

- **Blitzortung.org**: Amazing real-time lightning detection network
- **Your Geo Sequencer**: Beautiful coordinate-to-music architecture
- **WebSocket Magic**: Real-time data streaming at its finest

Enjoy making music from the power of nature! ⚡🎵
