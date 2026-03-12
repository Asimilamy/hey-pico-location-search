"""
Google Maps API integration module
Handles secure API key management and place searches using new Places API
"""
import requests
from typing import Optional, Dict, List, Any
from .config import settings


class GoogleMapsHandler:
    """Securely handle Google Maps API requests using new Places API"""

    def __init__(self):
        """Initialize Google Maps handler with API key"""
        self.api_key = settings.google_maps_api_key
        self.places_api_url = "https://places.googleapis.com/v1/places:searchText"
        self.places_detail_url = "https://places.googleapis.com/v1/places"

    def search_place(
        self,
        query: str,
        location: Optional[tuple] = None,
        radius: int = 5000
    ) -> Dict[str, Any]:
        """
        Search for a place using Google Maps Places API (New)

        Args:
            query: Place name or type (e.g., "Italian restaurants")
            location: Optional (latitude, longitude) tuple
            radius: Search radius in meters

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
                "pageSize": 5
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
            return self._format_results(data.get("places", []))

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
