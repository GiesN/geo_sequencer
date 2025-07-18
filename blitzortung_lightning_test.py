#!/usr/bin/env python3
"""
Blitzortung Lightning Data Stream Test
A simple test to verify real-time lightning data from Blitzortung servers.
"""

import asyncio
import json
import logging
import random
import ssl
import time
from typing import Dict, Any

import websockets


class BlitzortungLightningTest:
    """Test client for Blitzortung real-time lightning data."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strike_count = 0
        self.start_time = time.time()

        # SSL context for Blitzortung servers
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def decode(self, b: bytes) -> str:
        """
        Decode Blitzortung compressed message format.
        This is the same decoder used in the existing client.
        """
        e = {}
        d = list(b)
        c = d[0]
        f = c
        g = [c]
        h = 256
        o = h
        for b in range(1, len(d)):
            a = ord(d[b])
            a = d[b] if h > a else e.get(a, f + c)
            g.append(a)
            c = a[0]
            e[o] = f + c
            o += 1
            f = a
        return "".join(g)

    def process_lightning_strike(self, data: Dict[str, Any]):
        """Process and display lightning strike data."""
        self.strike_count += 1

        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)
        timestamp = data.get("time", 0)
        status = data.get("status", "unknown")
        region = data.get("region", "unknown")
        sig_num = data.get("sig_num", 0)

        # Convert timestamp to readable format
        readable_time = time.strftime(
            "%Y-%m-%d %H:%M:%S UTC",
            time.gmtime(timestamp / 1000),  # Blitzortung uses milliseconds
        )

        print(f"\n⚡ Lightning Strike #{self.strike_count}")
        print(f"   📍 Location: {lat:.6f}°, {lon:.6f}°")
        print(f"   🕐 Time: {readable_time}")
        print(f"   📊 Status: {status}")
        print(f"   🌍 Region: {region}")
        print(f"   📡 Signals: {sig_num}")
        print("-" * 50)

    async def connect_and_stream(self, duration_seconds: int = 60):
        """Connect to Blitzortung and stream lightning data."""
        # Available Blitzortung WebSocket servers
        hosts = ["ws1", "ws3", "ws7", "ws8"]

        print("⚡ Blitzortung Real-Time Lightning Test")
        print("=" * 60)
        print(f"Duration: {duration_seconds} seconds")
        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        print("=" * 60)

        while True:
            try:
                # Random host selection for load balancing
                host = random.choice(hosts)
                uri = f"wss://{host}.blitzortung.org:443/"

                self.logger.info(f"Connecting to {uri}")
                print(f"🔌 Connecting to {host}.blitzortung.org...")

                async with websockets.connect(uri, ssl=self.ssl_context) as websocket:
                    print(f"✅ Connected to {host}.blitzortung.org")

                    # Send initialization message (required by Blitzortung)
                    await websocket.send('{"a": 111}')
                    print("📡 Listening for lightning strikes...")
                    print("   (Press Ctrl+C to stop)")
                    print("-" * 50)

                    # Stream lightning data
                    end_time = time.time() + duration_seconds

                    while time.time() < end_time:
                        try:
                            # Receive message with timeout
                            msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)

                            # Decode and parse the message
                            decoded = self.decode(msg)
                            data = json.loads(decoded)

                            # Remove signal data (just get count)
                            sig = data.pop("sig", ())
                            data["sig_num"] = len(sig)

                            # Process the lightning strike
                            self.process_lightning_strike(data)

                        except asyncio.TimeoutError:
                            # No message received, continue
                            continue
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON decode error: {e}")
                        except Exception as e:
                            self.logger.error(f"Message processing error: {e}")

                    break  # Exit loop after successful run

            except websockets.ConnectionClosed:
                self.logger.warning("Connection closed, retrying...")
                await asyncio.sleep(5)
                continue
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                await asyncio.sleep(5)
                continue

        # Print summary
        elapsed = time.time() - self.start_time
        print("\n📊 Test Summary:")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Lightning strikes received: {self.strike_count}")
        print(
            f"   Average strikes per minute: {self.strike_count / (elapsed / 60):.1f}"
        )

        if self.strike_count > 0:
            print("✅ SUCCESS: Real-time lightning data is working!")
        else:
            print("⚠️  No lightning strikes detected during test period")
            print("   This is normal - lightning is not constant worldwide")


async def main():
    """Run the lightning test."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create and run test
    test = BlitzortungLightningTest()

    try:
        await test.connect_and_stream(duration_seconds=60)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        elapsed = time.time() - test.start_time
        print("📊 Partial results:")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Lightning strikes: {test.strike_count}")


if __name__ == "__main__":
    asyncio.run(main())
