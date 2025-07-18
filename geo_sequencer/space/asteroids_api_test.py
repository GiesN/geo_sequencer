import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json


class AsteroidCatalog:
    """
    NASA NeoWs (Near Earth Object Web Service) API client for asteroid data.
    Provides methods to fetch asteroid information based on different criteria.
    """

    def __init__(self, api_key: str = "DEMO_KEY"):
        """
        Initialize the asteroid catalog with NASA API key.

        Args:
            api_key: NASA API key (defaults to DEMO_KEY for testing)
        """
        self.base_url = "https://api.nasa.gov/neo/rest/v1"
        self.api_key = api_key

    def get_asteroid_feed(
        self, start_date: str, end_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve asteroids based on their closest approach date to Earth.

        Args:
            start_date: Starting date for asteroid search (YYYY-MM-DD)
            end_date: Ending date for asteroid search (YYYY-MM-DD)
                     If None, defaults to 7 days after start_date

        Returns:
            Dictionary containing asteroid feed data or None if error occurs
        """
        endpoint = f"{self.base_url}/feed"

        params = {"start_date": start_date, "api_key": self.api_key}

        if end_date:
            params["end_date"] = end_date

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error fetching asteroid feed: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing asteroid feed data: {e}")
            return None

    def lookup_asteroid(self, asteroid_id: int) -> Optional[Dict[str, Any]]:
        """
        Lookup a specific asteroid based on its NASA JPL small body ID.

        Args:
            asteroid_id: Asteroid SPK-ID (NASA JPL small body ID)

        Returns:
            Dictionary containing asteroid data or None if error occurs
        """
        endpoint = f"{self.base_url}/neo/{asteroid_id}"

        params = {"api_key": self.api_key}

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error looking up asteroid {asteroid_id}: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing asteroid lookup data: {e}")
            return None

    def browse_asteroids(
        self, page: int = 0, size: int = 20
    ) -> Optional[Dict[str, Any]]:
        """
        Browse the overall asteroid dataset.

        Args:
            page: Page number for pagination (default: 0)
            size: Number of asteroids per page (default: 20)

        Returns:
            Dictionary containing asteroid browse data or None if error occurs
        """
        endpoint = f"{self.base_url}/neo/browse"

        params = {"api_key": self.api_key, "page": page, "size": size}

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Error browsing asteroids: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing asteroid browse data: {e}")
            return None

    def display_asteroid_summary(self, data: Dict[str, Any], data_type: str) -> None:
        """
        Display a summary of asteroid data in a readable format.

        Args:
            data: Asteroid data dictionary
            data_type: Type of data ('feed', 'lookup', 'browse')
        """
        print(f"\n=== {data_type.upper()} RESULTS ===")

        if data_type == "feed":
            self._display_feed_summary(data)
        elif data_type == "lookup":
            self._display_lookup_summary(data)
        elif data_type == "browse":
            self._display_browse_summary(data)

    def _display_feed_summary(self, data: Dict[str, Any]) -> None:
        """Display summary for asteroid feed data."""
        if "near_earth_objects" in data:
            total_count = data.get("element_count", 0)
            print(f"Total asteroids found: {total_count}")

            for date, asteroids in data["near_earth_objects"].items():
                print(f"\nDate: {date} ({len(asteroids)} asteroids)")
                for asteroid in asteroids[:3]:  # Show first 3 per date
                    name = asteroid.get("name", "Unknown")
                    diameter = asteroid.get("estimated_diameter", {}).get(
                        "kilometers", {}
                    )
                    min_dia = diameter.get("estimated_diameter_min", 0)
                    max_dia = diameter.get("estimated_diameter_max", 0)
                    hazardous = asteroid.get("is_potentially_hazardous_asteroid", False)

                    print(f"  - {name}")
                    print(f"    Diameter: {min_dia:.3f} - {max_dia:.3f} km")
                    print(f"    Potentially hazardous: {hazardous}")

    def _display_lookup_summary(self, data: Dict[str, Any]) -> None:
        """Display summary for asteroid lookup data."""
        name = data.get("name", "Unknown")
        nasa_jpl_url = data.get("nasa_jpl_url", "N/A")
        hazardous = data.get("is_potentially_hazardous_asteroid", False)

        print(f"Name: {name}")
        print(f"NASA JPL URL: {nasa_jpl_url}")
        print(f"Potentially hazardous: {hazardous}")

        if "estimated_diameter" in data:
            diameter = data["estimated_diameter"].get("kilometers", {})
            min_dia = diameter.get("estimated_diameter_min", 0)
            max_dia = diameter.get("estimated_diameter_max", 0)
            print(f"Estimated diameter: {min_dia:.3f} - {max_dia:.3f} km")

    def _display_browse_summary(self, data: Dict[str, Any]) -> None:
        """Display summary for asteroid browse data."""
        if "near_earth_objects" in data:
            asteroids = data["near_earth_objects"]
            page_info = data.get("page", {})

            print(
                f"Page: {page_info.get('number', 0)} of {page_info.get('total_pages', 0)}"
            )
            print(f"Total elements: {page_info.get('total_elements', 0)}")
            print(f"Showing {len(asteroids)} asteroids:")

            for asteroid in asteroids[:5]:  # Show first 5
                name = asteroid.get("name", "Unknown")
                nasa_jpl_url = asteroid.get("nasa_jpl_url", "N/A")
                hazardous = asteroid.get("is_potentially_hazardous_asteroid", False)

                print(f"  - {name}")
                print(f"    NASA JPL URL: {nasa_jpl_url}")
                print(f"    Potentially hazardous: {hazardous}")

    def test_api_connection(self) -> bool:
        """
        Test if the API is accessible by making a simple browse request.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.browse_asteroids(size=1)
            return response is not None
        except Exception:
            return False


def main():
    """Demonstration of the asteroid catalog functionality."""
    # Initialize with DEMO_KEY (you can replace with your own NASA API key)
    catalog = AsteroidCatalog(api_key="DEMO_KEY")

    print("=== NASA NeoWs Asteroid API Demo ===\n")

    # Test API connection
    print("Testing API connection...")
    if not catalog.test_api_connection():
        print("Failed to connect to NASA API!")
        return
    print("API connection successful!\n")

    # Example 1: Get asteroid feed for recent dates
    print("1. Asteroid Feed (last 3 days):")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)

        feed_data = catalog.get_asteroid_feed(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        if feed_data:
            catalog.display_asteroid_summary(feed_data, "feed")
            print("\nRaw feed data sample:")
            print(json.dumps(feed_data, indent=2)[:500] + "...")
        else:
            print("Failed to fetch asteroid feed data")

    except Exception as e:
        print(f"Error in asteroid feed example: {e}")

    # Example 2: Lookup specific asteroid
    print("\n" + "=" * 50)
    print("2. Asteroid Lookup (Asteroid ID: 3542519):")
    try:
        lookup_data = catalog.lookup_asteroid(3542519)

        if lookup_data:
            catalog.display_asteroid_summary(lookup_data, "lookup")
            print("\nRaw lookup data sample:")
            print(json.dumps(lookup_data, indent=2)[:500] + "...")
        else:
            print("Failed to lookup asteroid data")

    except Exception as e:
        print(f"Error in asteroid lookup example: {e}")

    # Example 3: Browse asteroid dataset
    print("\n" + "=" * 50)
    print("3. Browse Asteroids (first page):")
    try:
        browse_data = catalog.browse_asteroids(page=0, size=10)

        if browse_data:
            catalog.display_asteroid_summary(browse_data, "browse")
            print("\nRaw browse data sample:")
            print(json.dumps(browse_data, indent=2)[:500] + "...")
        else:
            print("Failed to browse asteroid data")

    except Exception as e:
        print(f"Error in asteroid browse example: {e}")


if __name__ == "__main__":
    main()
