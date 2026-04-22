"""
Google Maps API integration module
Handles secure API key management and place searches using new Places API
"""
import requests
import math
from typing import Optional, Dict, List, Any
from .config import settings


class GoogleMapsHandler:
    """Securely handle Google Maps API requests using new Places API"""

    def __init__(self):
        """Initialize Google Maps handler with API key"""
        self.api_key = settings.google_maps_api_key
        self.places_api_url = "https://places.googleapis.com/v1/places:searchText"
        self.places_detail_url = "https://places.googleapis.com/v1/places"

    @staticmethod
    def _calculate_bounds(latitude: float, longitude: float, radius_meters: int) -> Dict[str, Dict[str, float]]:
        """
        Calculate rectangular bounds from center point and radius

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Radius in meters

        Returns:
            Dict with low and high bounds for rectangular_bounds
        """
        # Earth's radius in meters
        earth_radius = 6371000

        # Calculate angular distance
        angular_distance = radius_meters / earth_radius

        # Calculate latitude bounds (simpler)
        lat_offset = math.degrees(angular_distance)

        # Calculate longitude bounds (adjusted for latitude)
        lon_offset = math.degrees(angular_distance / math.cos(math.radians(latitude)))

        return {
            "low": {
                "latitude": latitude - lat_offset,
                "longitude": longitude - lon_offset
            },
            "high": {
                "latitude": latitude + lat_offset,
                "longitude": longitude + lon_offset
            }
        }

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in meters using Haversine formula

        Args:
            lat1, lon1: First coordinate (center)
            lat2, lon2: Second coordinate (place)

        Returns:
            Distance in meters
        """
        R = 6371000  # Earth's radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _filter_by_distance(self, places: List[Dict], location: tuple, radius: int) -> List[Dict]:
        """
        Filter places by distance from center location

        Args:
            places: List of place results from API
            location: (latitude, longitude) tuple
            radius: Maximum distance in meters

        Returns:
            Filtered list of places within radius
        """
        filtered = []
        for place in places:
            place_location = place.get("location", {})
            if place_location:
                distance = self._calculate_distance(
                    location[0], location[1],
                    place_location.get("latitude", 0),
                    place_location.get("longitude", 0)
                )
                if distance <= radius:
                    filtered.append(place)
        return filtered

    def search_place(
        self,
        query: str,
        location: Optional[tuple] = None,
        radius: int = 15000
    ) -> Dict[str, Any]:
        """
        Search for a place using Google Maps Places API (New)

        Args:
            query: Place name or type (e.g., "Italian restaurants")
            location: Optional (latitude, longitude) tuple
            radius: Search radius in meters (default 15km)

        Returns:
            Dictionary with place information
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.rating,places.types,places.internationalPhoneNumber,places.websiteUri,places.id"
            }

            payload = {
                "textQuery": query,
                "pageSize": 20
            }

            if location:
                payload["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": location[0],
                            "longitude": location[1]
                        },
                        "radius": radius
                    }
                }

            response = requests.post(
                self.places_api_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code != 200:
                error_detail = response.json().get("error", {}).get("message", response.text)
                return {"error": f"Google Places API error: {error_detail}", "places": []}

            data = response.json()
            places_list = data.get("places", [])

            # Filter results to be within the radius if location provided
            if location:
                places_list = self._filter_by_distance(places_list, location, radius)

            return self._format_results(places_list)

        except requests.exceptions.Timeout:
            return {"error": "Google Places API request timed out", "places": []}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "places": []}

    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a place (not used with new API)

        Args:
            place_id: Google Place ID

        Returns:
            Empty dict as details are included in search results
        """
        return {}

    def get_place_url(self, latitude: float, longitude: float) -> str:
        """
        Generate a Google Maps URL for a location

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Google Maps URL
        """
        return f"https://www.google.com/maps?q={latitude},{longitude}"

    @staticmethod
    def _format_results(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Format Google Places API (New) results for API response"""
        places = []

        for result in results[:5]:  # Limit to top 5
            location = result.get("location", {})
            place = {
                "name": result.get("displayName", {}).get("text", "Unknown"),
                "place_id": result.get("id", ""),
                "address": result.get("formattedAddress", ""),
                "latitude": location.get("latitude", 0),
                "longitude": location.get("longitude", 0),
                "rating": result.get("rating"),
                "types": result.get("types", []),
                "phone": result.get("internationalPhoneNumber"),
                "website": result.get("websiteUri"),
            }
            places.append(place)

        return {"places": places}


# Global instance
maps_handler = GoogleMapsHandler()
