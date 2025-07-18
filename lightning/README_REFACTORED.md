# Geo MIDI Sequencer - Refactored Architecture

This project has been refactored to provide a more modular and generic architecture for streaming coordinates from various sources and converting them to MIDI sequences.

## Architecture Overview

The refactored system consists of two main components:

### 1. Coordinate Clients (`coordinate_client.py`)
- **`CoordinateClient`** - Abstract base class for all coordinate streaming clients
- **`DummyWebSocketClient`** - WebSocket client for the dummy coordinate server
- **`FileCoordinateClient`** - Example client for reading coordinates from files (placeholder)
- **`APICoordinateClient`** - Example client for fetching coordinates from REST APIs (placeholder)

### 2. MIDI Sequencer (`geo_midi_sequencer.py`)
- **`GeoMidiSequencer`** - The main MIDI sequencer that converts coordinates to music
- Takes any `CoordinateClient` as input, making it source-agnostic
- Handles all MIDI processing, musical scales, and note generation

## Key Benefits

1. **Separation of Concerns**: Coordinate streaming is separate from MIDI processing
2. **Modularity**: Easy to add new coordinate sources without modifying the sequencer
3. **Reusability**: The same sequencer can work with any coordinate client
4. **Testability**: Each component can be tested independently

## Usage Examples

### Basic Usage with Dummy WebSocket

```python
from geo_midi_sequencer import GeoMidiSequencer
from coordinate_client import DummyWebSocketClient

# Create coordinate client
client = DummyWebSocketClient("ws://localhost:8000/ws")

# Create sequencer with the client
sequencer = GeoMidiSequencer(
    coordinate_client=client,
    scale_type="pentatonic",
    base_note=60,
    octave_range=4
)

# Run the sequencer
await sequencer.run()
```

### Command Line Usage

```bash
# Run with dummy websocket (default)
python geo_midi_sequencer.py --url ws://localhost:8000/ws --scale pentatonic

# Run with different musical settings
python geo_midi_sequencer.py --scale major --base-note 48 --octave-range 3 --note-duration 2.0
```

### Running Examples

```bash
# Example with dummy websocket
python example_usage.py --example dummy

# Example with custom test client
python example_usage.py --example custom --verbose
```

## Creating Custom Coordinate Clients

To create a new coordinate client, inherit from `CoordinateClient` and implement the abstract methods:

```python
from coordinate_client import CoordinateClient

class MyCustomClient(CoordinateClient):
    async def connect(self) -> bool:
        # Implement connection logic
        return True
    
    async def listen(self):
        # Implement coordinate streaming logic
        while self.is_running:
            # Get coordinates from your source
            data = {"latitude": lat, "longitude": lon, "timestamp": time}
            await self.process_data(data)
            await asyncio.sleep(1)
    
    async def disconnect(self):
        # Implement cleanup logic
        pass
```

## File Structure

```
lightning/
├── coordinate_client.py      # Base client classes and implementations
├── geo_midi_sequencer.py     # Main MIDI sequencer
├── dummy_websocket.py        # Dummy coordinate server
├── example_usage.py          # Usage examples
├── README_REFACTORED.md      # This file
└── ABLETON_SETUP.md         # Original Ableton setup guide
```

## Dependencies

- `mido` - MIDI processing
- `websockets` - WebSocket client support
- `fastapi` - For the dummy websocket server
- `uvicorn` - ASGI server for FastAPI

## Running the Complete System

1. **Start the dummy coordinate server:**
   ```bash
   python dummy_websocket.py
   ```

2. **In another terminal, run the sequencer:**
   ```bash
   python geo_midi_sequencer.py
   ```

3. **Or run the examples:**
   ```bash
   python example_usage.py --example dummy
   ```

## Future Extensions

The modular architecture makes it easy to add new coordinate sources:

- **Real earthquake data** from USGS APIs
- **Live GPS tracking** from mobile devices
- **Social media geolocation** from Twitter/Instagram APIs
- **Weather station data** with geographic coordinates
- **Vehicle tracking** systems
- **Maritime AIS data** for ship positions

Each new source just needs to implement the `CoordinateClient` interface, and it will work seamlessly with the existing MIDI sequencer.
