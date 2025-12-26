import os
import googlemaps
from google.adk.tools.tool_context import ToolContext

try:
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
except ValueError:
    gmaps = None
    print("⚠️ Warning: GOOGLE_MAPS_API_KEY not found in .env")

def search_places(tool_context: ToolContext, query: str) -> str:
    """
    Searches for places using the Google Places API.
    Returns a list of top results with names, addresses, and ratings.
    """
    if not gmaps:
        return "Error: Google Maps API key is not configured."

    try:
        results = gmaps.places(query=query)

        if not results or 'results' not in results:
            return f"No places found for '{query}'."

        formatted_results = []
        for place in results['results'][:5]:
            name = place.get('name', 'Unknown')
            address = place.get('formatted_address', 'No address')
            rating = place.get('rating', 'N/A')
            user_ratings = place.get('user_ratings_total', 0)
            
            formatted_results.append(
                f"📍 {name} ({rating}⭐ from {user_ratings} reviews)\n"
                f"   Address: {address}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Google Maps API Error: {str(e)}"