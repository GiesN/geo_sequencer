import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union


class EarthquakeCatalog:
    """
    Enhanced earthquake data fetcher using the USGS FDSN Event Web Service.
    This allows for much more flexible queries including historical data,
    geographic filtering, magnitude filtering, and more.
    """

    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1"

    def query_earthquakes(
        self,
        format: str = "geojson",
        starttime: Optional[str] = None,
        endtime: Optional[str] = None,
        minmagnitude: Optional[float] = None,
        maxmagnitude: Optional[float] = None,
        mindepth: Optional[float] = None,
        maxdepth: Optional[float] = None,
        minlatitude: Optional[float] = None,
        maxlatitude: Optional[float] = None,
        minlongitude: Optional[float] = None,
        maxlongitude: Optional[float] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        maxradius: Optional[float] = None,
        maxradiuskm: Optional[float] = None,
        orderby: str = "time",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        eventtype: Optional[str] = None,
        reviewstatus: str = "all",
        alertlevel: Optional[str] = None,
        **kwargs,
    ) -> Optional[Union[Dict[str, Any], str]]:
        """
        Query earthquake data using the USGS FDSN Event Web Service.

        Args:
            format: Output format (geojson, csv, xml, kml, text)
            starttime: Start time (ISO8601 format, e.g., '2024-01-01' or '2024-01-01T12:00:00')
            endtime: End time (ISO8601 format)
            minmagnitude: Minimum magnitude
            maxmagnitude: Maximum magnitude
            mindepth: Minimum depth in km
            maxdepth: Maximum depth in km
            minlatitude: Minimum latitude (-90 to 90)
            maxlatitude: Maximum latitude (-90 to 90)
            minlongitude: Minimum longitude (-360 to 360)
            maxlongitude: Maximum longitude (-360 to 360)
            latitude: Center latitude for radius search
            longitude: Center longitude for radius search
            maxradius: Maximum radius in degrees (requires lat/lon)
            maxradiuskm: Maximum radius in km (requires lat/lon)
            orderby: Sort order (time, time-asc, magnitude, magnitude-asc)
            limit: Maximum number of events (1-20000)
            offset: Starting offset for results
            eventtype: Event type filter (e.g., 'earthquake')
            reviewstatus: Review status (automatic, reviewed, all)
            alertlevel: PAGER alert level (green, yellow, orange, red)
            **kwargs: Additional parameters

        Returns:
            Parsed response data or None if error occurs
        """
        params = {"format": format, "orderby": orderby}

        # Only add reviewstatus if it's not 'all' (default)
        if reviewstatus != "all":
            params["reviewstatus"] = reviewstatus

        # Add all non-None parameters
        locals_dict = locals()
        for key, value in locals_dict.items():
            if (
                key not in ["self", "params", "locals_dict", "kwargs"]
                and value is not None
            ):
                if key != "format" and key != "orderby" and key != "reviewstatus":
                    params[key] = value

        # Add any additional parameters
        params.update(kwargs)

        try:
            response = requests.get(f"{self.base_url}/query", params=params, timeout=30)
            response.raise_for_status()

            if format == "geojson":
                return response.json()
            elif format == "csv":
                return response.text
            elif format in ["xml", "kml", "text"]:
                return response.text
            else:
                return response.json()

        except requests.RequestException as e:
            print(f"Error fetching earthquake data: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing earthquake data: {e}")
            return None

    def get_recent_earthquakes(
        self, days_back: int = 7, min_magnitude: float = 2.5
    ) -> Optional[Dict[str, Any]]:
        """
        Get earthquakes from the last N days above a certain magnitude.

        Args:
            days_back: Number of days to look back
            min_magnitude: Minimum magnitude to include

        Returns:
            GeoJSON data with earthquake information
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        return self.query_earthquakes(
            starttime=start_time.strftime("%Y-%m-%d"),
            endtime=end_time.strftime("%Y-%m-%d"),
            minmagnitude=min_magnitude,
            orderby="magnitude-asc",
        )

    def get_historical_earthquakes(
        self, start_year: int, end_year: int, min_magnitude: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """
        Get historical earthquakes for a specific year range.

        Args:
            start_year: Starting year
            end_year: Ending year
            min_magnitude: Minimum magnitude to include

        Returns:
            GeoJSON data with earthquake information
        """
        return self.query_earthquakes(
            starttime=f"{start_year}-01-01",
            endtime=f"{end_year}-12-31",
            minmagnitude=min_magnitude,
            orderby="magnitude-asc",
            limit=20000,  # Maximum allowed
        )

    def get_earthquakes_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        days_back: int = 30,
        min_magnitude: float = 2.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Get earthquakes near a specific location.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            days_back: Number of days to look back
            min_magnitude: Minimum magnitude to include

        Returns:
            GeoJSON data with earthquake information
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)

        return self.query_earthquakes(
            starttime=start_time.strftime("%Y-%m-%d"),
            endtime=end_time.strftime("%Y-%m-%d"),
            latitude=latitude,
            longitude=longitude,
            maxradiuskm=radius_km,
            minmagnitude=min_magnitude,
            orderby="time",
        )

    def get_major_earthquakes_by_region(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        min_magnitude: float = 6.0,
        start_date: str = "2000-01-01",
    ) -> Optional[Dict[str, Any]]:
        """
        Get major earthquakes in a rectangular region.

        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude
            max_lon: Maximum longitude
            min_magnitude: Minimum magnitude
            start_date: Start date (ISO format)

        Returns:
            GeoJSON data with earthquake information
        """
        return self.query_earthquakes(
            starttime=start_date,
            minlatitude=min_lat,
            maxlatitude=max_lat,
            minlongitude=min_lon,
            maxlongitude=max_lon,
            minmagnitude=min_magnitude,
            orderby="magnitude-asc",
        )

    def count_earthquakes(self, **kwargs) -> Optional[int]:
        """
        Count earthquakes matching the given criteria without fetching the full data.

        Args:
            **kwargs: Same parameters as query_earthquakes

        Returns:
            Number of matching earthquakes or None if error
        """
        try:
            response = requests.get(f"{self.base_url}/count", params=kwargs, timeout=10)
            response.raise_for_status()
            return int(response.text.strip())
        except (requests.RequestException, ValueError) as e:
            print(f"Error counting earthquakes: {e}")
            return None

    def test_api_connection(self) -> bool:
        """
        Test the API connection with a simple query.

        Returns:
            True if API is working, False otherwise
        """
        try:
            # Simple test query - just get a few recent earthquakes
            response = requests.get(
                f"{self.base_url}/query",
                params={"format": "geojson", "limit": 1},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return "features" in data
        except Exception as e:
            print(f"API test failed: {e}")
            return False

    def export_to_csv(self, **kwargs) -> Optional[str]:
        """
        Export earthquake data to CSV format.

        Args:
            **kwargs: Same parameters as query_earthquakes

        Returns:
            CSV data as string or None if error
        """
        return self.query_earthquakes(format="csv", **kwargs)

    def display_earthquake_summary(self, data: Dict[str, Any]) -> None:
        """
        Display a summary of earthquake data.

        Args:
            data: GeoJSON earthquake data
        """
        if not data or "features" not in data:
            print("No earthquake data to display")
            return

        earthquakes = data["features"]
        total_count = len(earthquakes)

        if total_count == 0:
            print("No earthquakes found matching the criteria")
            return

        print("\n=== Earthquake Summary ===")
        print(f"Total earthquakes: {total_count}")

        # Magnitude statistics
        magnitudes = [
            q["properties"]["mag"] for q in earthquakes if q["properties"]["mag"]
        ]
        if magnitudes:
            print(f"Magnitude range: {min(magnitudes):.1f} - {max(magnitudes):.1f}")
            avg_mag = sum(magnitudes) / len(magnitudes)
            print(f"Average magnitude: {avg_mag:.1f}")

        # Time range
        times = [
            q["properties"]["time"] for q in earthquakes if q["properties"]["time"]
        ]
        if times:
            min_time = datetime.fromtimestamp(min(times) / 1000)
            max_time = datetime.fromtimestamp(max(times) / 1000)
            print(f"Time range: {min_time} to {max_time}")

        print("\n=== Recent Earthquakes ===")
        # Show the 10 most recent earthquakes
        recent_earthquakes = sorted(
            earthquakes, key=lambda x: x["properties"]["time"], reverse=True
        )[:10]

        for quake in recent_earthquakes:
            props = quake["properties"]
            coords = quake["geometry"]["coordinates"]

            mag = props["mag"] or "N/A"
            place = props["place"] or "Unknown location"
            time_ms = props["time"]
            lon, lat, depth = coords

            if time_ms:
                quake_time = datetime.fromtimestamp(time_ms / 1000)
                print(f"M{mag} - {place}")
                print(f"  Location: {lat:.3f}, {lon:.3f} ({depth}km deep)")
                print(f"  Time: {quake_time}")
                print()


def main():
    """Demonstration of the earthquake catalog functionality."""
    catalog = EarthquakeCatalog()

    print("=== USGS Earthquake Catalog Demo ===\n")

    # Test API connection first
    print("Testing API connection...")
    if not catalog.test_api_connection():
        print("API connection failed. Please check your internet connection.")
        return
    print("API connection successful!\n")

    # Example 1: Recent significant earthquakes (simplified)
    print("1. Recent significant earthquakes (M4.5+, last 7 days):")
    try:
        recent_data = catalog.query_earthquakes(
            starttime=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            minmagnitude=4.5,
            orderby="time",
            limit=50,
        )
        if recent_data:
            catalog.display_earthquake_summary(recent_data)
        else:
            print("No data returned")
    except Exception as e:
        print(f"Error in example 1: {e}")

    # Example 2: Count earthquakes in a region
    print("\n2. Counting earthquakes in California (M3.0+, last 30 days):")
    try:
        ca_count = catalog.count_earthquakes(
            starttime=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            minlatitude=32.0,
            maxlatitude=42.0,
            minlongitude=-125.0,
            maxlongitude=-114.0,
            minmagnitude=3.0,
        )
        if ca_count is not None:
            print(f"Total earthquakes in California: {ca_count}")
    except Exception as e:
        print(f"Error in example 2: {e}")

    # Example 3: Simple radius search (simplified)
    print("\n3. Earthquakes near San Francisco (within 100km, last 7 days):")
    try:
        sf_data = catalog.query_earthquakes(
            starttime=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            latitude=37.7749,
            longitude=-122.4194,
            maxradiuskm=100,
            minmagnitude=2.0,
            limit=20,
        )
        if sf_data:
            catalog.display_earthquake_summary(sf_data)
        else:
            print("No data returned")
    except Exception as e:
        print(f"Error in example 3: {e}")

    # Example 4: Major historical earthquakes (simplified)
    print("\n4. Major earthquakes worldwide (M7.0+, last 2 years):")
    try:
        major_data = catalog.query_earthquakes(
            starttime="2023-01-01", minmagnitude=7.0, orderby="time", limit=50
        )
        if major_data:
            catalog.display_earthquake_summary(major_data)
        else:
            print("No data returned")
    except Exception as e:
        print(f"Error in example 4: {e}")

    # Example 5: Export data to CSV (simplified)
    print("\n5. Exporting recent M5.0+ earthquakes to CSV format...")
    try:
        csv_data = catalog.export_to_csv(
            starttime=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            minmagnitude=5.0,
            limit=10,
        )
        if csv_data and len(csv_data.strip()) > 0:
            lines = csv_data.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]
            print(f"CSV export successful! {len(non_empty_lines)} lines exported.")
            print("First few lines:")
            for line in lines[:5]:
                if line.strip():
                    print(line)
        else:
            print("No CSV data returned")
    except Exception as e:
        print(f"Error in example 5: {e}")


if __name__ == "__main__":
    main()
