import requests
import time
import threading
from datetime import datetime
from typing import Optional, Dict, List, Any


class EarthquakeMonitor:
    def __init__(self):
        self.last_update = 0
        self.update_interval = 60  # 1 minute in seconds
        self.monitoring_thread = None
        self.stop_monitoring_flag = False

    def fetch_earthquakes(
        self,
        feed_url: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson",
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch earthquake data from the USGS feed.

        Args:
            feed_url: URL of the earthquake feed

        Returns:
            Dictionary containing earthquake data or None if error occurs
        """
        try:
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Filter for new earthquakes since last update
            new_earthquakes = [
                quake
                for quake in data["features"]
                if quake["properties"]["time"] > self.last_update
            ]

            if new_earthquakes:
                # Update last_update to the most recent earthquake time
                self.last_update = max(q["properties"]["time"] for q in new_earthquakes)
                self.process_new_earthquakes(new_earthquakes)

            return data

        except requests.RequestException as e:
            print(f"Error fetching earthquake data: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Error parsing earthquake data: {e}")
            return None

    def process_new_earthquakes(self, earthquakes: List[Dict[str, Any]]) -> None:
        """
        Process and display information about new earthquakes.

        Args:
            earthquakes: List of earthquake feature dictionaries
        """
        for quake in earthquakes:
            properties = quake["properties"]
            coordinates = quake["geometry"]["coordinates"]

            mag = properties["mag"]
            place = properties["place"]
            time_ms = properties["time"]

            lon, lat, depth = coordinates

            # Convert timestamp from milliseconds to datetime
            earthquake_time = datetime.fromtimestamp(time_ms / 1000)

            print(f"New earthquake: M{mag} - {place}")
            print(f"Location: {lat}, {lon} ({depth}km deep)")
            print(f"Time: {earthquake_time}")
            print("---")

    def _monitoring_loop(self) -> None:
        """Internal method for the monitoring loop running in a separate thread."""
        while not self.stop_monitoring_flag:
            self.fetch_earthquakes()
            time.sleep(self.update_interval)

    def start_monitoring(self) -> None:
        """Start monitoring earthquakes in a separate thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            print("Monitoring is already running!")
            return

        self.stop_monitoring_flag = False

        # Initial fetch
        print("Starting earthquake monitoring...")
        self.fetch_earthquakes()

        # Start monitoring in a separate thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()
        print(
            f"Monitoring started. Checking for new earthquakes every {self.update_interval} seconds."
        )

    def stop_monitoring(self) -> None:
        """Stop the earthquake monitoring."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            print("Stopping earthquake monitoring...")
            self.stop_monitoring_flag = True
            self.monitoring_thread.join(timeout=5)
            print("Monitoring stopped.")
        else:
            print("Monitoring is not currently running.")


def main():
    """Main function to demonstrate usage."""
    monitor = EarthquakeMonitor()

    try:
        monitor.start_monitoring()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()
