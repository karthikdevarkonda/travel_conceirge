import os
import googlemaps
from google.adk.tools.tool_context import ToolContext

try:
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
except (ValueError, Exception):
    gmaps = None
    print("⚠️ Warning: Google Maps API Key missing.")

def search_places_tool(tool_context: ToolContext, query: str, page: int = 1) -> str:
    if not gmaps: 
        return "Error: Google Maps API key is not configured."
    
    print(f"DEBUG: Searching Places for: '{query}' (Page {page})")
    
    cache_key = f"poi_search_{query.replace(' ', '_')}"
    
    all_results = []
    
    if page == 1:
        try:
            if "tourist" not in query.lower() and "attraction" not in query.lower():
                search_query = f"Top rated tourist attractions in {query}"
            else:
                search_query = query
                
            response = gmaps.places(query=search_query)
            if not response or 'results' not in response: 
                return f"No places found for '{query}'."
            
            raw_results = response['results']
            
            valid_results = [p for p in raw_results if p.get('user_ratings_total', 0) > 1000]
            
            valid_results.sort(key=lambda x: x.get('user_ratings_total', 0), reverse=True)
            
            all_results = valid_results if valid_results else raw_results
            
            tool_context.state[cache_key] = all_results
            
        except Exception as e: 
            return f"Error connecting to Maps: {str(e)}"
    else:
        all_results = tool_context.state.get(cache_key, [])
        if not all_results:
            return "No search results in memory. Please start a new search."

    start_index = (page - 1) * 5
    end_index = start_index + 5
    
    batch = all_results[start_index:end_index]
    
    if not batch:
        return "No more results to show."

    formatted_results = [f"Found {len(all_results)} iconic places. Showing {start_index+1}-{min(end_index, len(all_results))}:\n"]
    
    for place in batch:
        name = place.get('name', 'Unknown')
        addr = place.get('formatted_address', 'Unknown Address')
        rating = place.get('rating', 'N/A')
        user_ratings_total = place.get('user_ratings_total', 0)
        types = ", ".join(place.get('types', [])[:3]) 
        
        entry = f"Name: {name}\n   Address: {addr}\n   Rating: {rating} ({user_ratings_total} reviews)\n   Tags: {types}"
        formatted_results.append(entry)
        
    formatted_results.append(f"\n(Page {page} of {int(len(all_results)/5) + (1 if len(all_results)%5 else 0)})")
    
    return "\n---\n".join(formatted_results)