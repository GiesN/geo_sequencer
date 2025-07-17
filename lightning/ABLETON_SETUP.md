# Connecting Geo MIDI Sequencer to Ableton Live

## Step-by-Step Setup Guide

### 1. Enable Virtual MIDI on macOS

Since you're on macOS, you need to enable the built-in virtual MIDI driver:

1. **Open Audio MIDI Setup:**
   - Press `Cmd + Space` and search for "Audio MIDI Setup"
   - Or go to Applications → Utilities → Audio MIDI Setup

2. **Enable IAC Driver:**
   - In Audio MIDI Setup, go to `Window` → `Show MIDI Studio`
   - Double-click on "IAC Driver"
   - Check "Device is online"
   - You can rename the port to "Geo Sequencer" if you want
   - Click "Apply"

### 2. Configure Ableton Live

1. **Open Ableton Live Preferences:**
   - Go to `Live` → `Preferences` (or press `Cmd + ,`)

2. **MIDI Settings:**
   - Click on "MIDI" tab
   - Under "Control Surface" section, you should see "IAC Driver" or your custom name
   - Set the Input to "IAC Driver Bus 1" (or your custom name)
   - Make sure "Track" and "Remote" are enabled for the Input
   - Click "OK"

3. **Create a MIDI Track:**
   - Create a new MIDI track (`Cmd + Shift + T`)
   - Set the MIDI track's input to "IAC Driver Bus 1" or "All Ins"
   - Arm the track for recording (click the record button on the track)

4. **Add an Instrument:**
   - Drag an instrument from the Browser to the MIDI track (e.g., Wavetable, Simpler, Drum Rack)
   - Or use the built-in instruments

### 3. Run the Geo MIDI Sequencer System

Open **3 separate terminals** and run these commands:

**Terminal 1 - Start the coordinate server:**
```bash
cd /Users/nilsgies/Documents/Projects/Other/geo_sequencer/lightning
python dummy_websocket.py
```

**Terminal 2 - Start the MIDI sequencer:**
```bash
cd /Users/nilsgies/Documents/Projects/Other/geo_sequencer/lightning
python geo_midi_sequencer.py --midi-port "IAC Driver Bus 1" --scale pentatonic --verbose
```

**Terminal 3 - (Optional) Monitor the data stream:**
```bash
cd /Users/nilsgies/Documents/Projects/Other/geo_sequencer/lightning
python websocket_client.py
```

### 4. Alternative: Auto-Detection Method

If you want the sequencer to automatically find the MIDI port:

```bash
python geo_midi_sequencer.py --scale pentatonic --verbose
```

The sequencer will automatically detect available MIDI ports and use the first one it finds.

### 5. Troubleshooting

**If you don't hear sound:**
1. Check that the MIDI track in Ableton is armed (red record button)
2. Verify the track has an instrument loaded
3. Check that the track's input is set to your MIDI source
4. Make sure Ableton's master volume is up
5. Check that your speakers/headphones are connected

**If MIDI connection fails:**
1. Verify IAC Driver is enabled in Audio MIDI Setup
2. Check available MIDI ports by running:
   ```bash
   python -c "import mido; print('Available MIDI ports:', mido.get_output_names())"
   ```

**Check MIDI activity:**
- In Ableton Live, you should see MIDI activity indicators lighting up on the track when notes are received

### 6. Musical Recommendations for Ableton Live

**Good Instruments for Geographic Data:**
- **Wavetable:** Great for ambient, evolving sounds
- **Simpler:** Load ambient pads or nature sounds
- **Operator:** FM synthesis for complex textures
- **Impulse:** Use for percussive geographic rhythms

**Effects to try:**
- **Reverb:** Add space and atmosphere
- **Delay:** Create echoing effects
- **Auto Filter:** Let longitude control filter sweeps
- **Chorus:** Widen the sound

**Scale Recommendations:**
- `--scale pentatonic` → Harmonic, ambient
- `--scale blues` → Moody, emotional
- `--scale major` → Bright, uplifting
- `--scale minor` → Dark, mysterious

### 7. Advanced Setup: Multiple Tracks

You can route different aspects to different tracks:

1. **Track 1:** Main melody (use the geo sequencer)
2. **Track 2:** Percussion (trigger manually or use a different MIDI source)
3. **Track 3:** Ambient pads (use long note durations)

### 8. Recording Your Performance

1. **Arm multiple tracks** for recording
2. **Press the main record button** in Ableton
3. **Let the geo sequencer play** while coordinates stream
4. **Stop recording** when you have enough material
5. **Edit and arrange** the recorded MIDI data

## Quick Start Command

For immediate Ableton Live connection:

```bash
# Start the server
python dummy_websocket.py &

# Start the MIDI sequencer with Ableton-friendly settings
python geo_midi_sequencer.py --midi-port "IAC Driver Bus 1" --scale pentatonic --base-note 60 --note-duration 2.0 --verbose
```

Now your geographic coordinates will play as music in Ableton Live in real-time! 🌍🎵
