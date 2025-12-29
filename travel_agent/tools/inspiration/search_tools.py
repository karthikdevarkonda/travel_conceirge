import os
import random
import googlemaps
from google.adk.tools.tool_context import ToolContext

try:
    from googlesearch import search 
    HAS_GOOGLE_LIB = True
except ImportError:
    HAS_GOOGLE_LIB = False
    print("⚠️ Warning: 'googlesearch-python' library not found. Using simulation.")

try:
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
except (ValueError, Exception):
    gmaps = None

def google_search_tool(tool_context: ToolContext, query: str) -> str:
    print(f"DEBUG: Searching Google for: '{query}'")

    if HAS_GOOGLE_LIB:
        try:
            results = []
            search_results = search(query, num_results=20, advanced=True)
            for i, result in enumerate(search_results, 1):
                results.append(f"{i}. {result.title}\n   Description: {result.description}\n   URL: {result.url}")
            if results: return "\n\n".join(results)
        except Exception as e:
            print(f"DEBUG: Real search failed ({e}). Switching to Simulation.")
    
    return "Simulated Result: 1. Option A... 2. Option B..."

def search_places(tool_context: ToolContext, query: str) -> str:
 
    if not gmaps: return "Error: Google Maps API key is not configured."
    
    print(f"DEBUG: Searching Places for: '{query}'")
    try:
        results = gmaps.places(query=query)
        if not results or 'results' not in results: return f"No places found for '{query}'."
        
        place_names = []
        for place in results['results'][:5]:
            name = place.get('name', 'Unknown')
            place_names.append(name)
            
        return ", ".join(place_names)

    except Exception as e: return f"Error: {str(e)}"