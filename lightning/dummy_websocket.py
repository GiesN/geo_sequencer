import asyncio
import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(
    title="Coordinates Dummy WebSocket",
    description="Random Earth coordinates streaming via WebSocket",
)

# Store active connections
active_connections: list[WebSocket] = []


async def connect_websocket(websocket: WebSocket):
    """Accept and store WebSocket connection"""
    await websocket.accept()
    active_connections.append(websocket)


def disconnect_websocket(websocket: WebSocket):
    """Remove WebSocket connection"""
    if websocket in active_connections:
        active_connections.remove(websocket)


def generate_random_coordinates():
    """Generate random latitude and longitude coordinates on Earth"""
    # Latitude: -90 to 90 degrees
    latitude = random.uniform(-90, 90)
    # Longitude: -180 to 180 degrees
    longitude = random.uniform(-180, 180)

    return {
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "timestamp": asyncio.get_event_loop().time(),
    }


@app.get("/")
async def get_homepage():
    """Simple HTML page to test the WebSocket"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coordinates Dummy WebSocket - Random Earth Coordinates</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            #coordinates { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            .coordinate { margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>Random Earth Coordinates Stream</h1>
        <div id="coordinates"></div>
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");
            const coordinatesDiv = document.getElementById("coordinates");
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const div = document.createElement("div");
                div.className = "coordinate";
                div.innerHTML = `<strong>Lat:</strong> ${data.latitude}, <strong>Lng:</strong> ${data.longitude} <em>(${new Date(data.timestamp * 1000).toLocaleTimeString()})</em>`;
                coordinatesDiv.insertBefore(div, coordinatesDiv.firstChild);
                
                // Keep only last 20 coordinates
                while (coordinatesDiv.children.length > 20) {
                    coordinatesDiv.removeChild(coordinatesDiv.lastChild);
                }
            };
            
            ws.onopen = function(event) {
                console.log("Connected to WebSocket");
            };
            
            ws.onclose = function(event) {
                console.log("WebSocket connection closed");
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint that streams random Earth coordinates"""
    await connect_websocket(websocket)
    try:
        while True:
            # Generate random coordinates
            coordinates = generate_random_coordinates()

            # Send coordinates as JSON
            await websocket.send_text(json.dumps(coordinates))

            # Wait for 5 seconds before sending next coordinates
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        disconnect_websocket(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        disconnect_websocket(websocket)


def main():
    """Run the FastAPI server"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
