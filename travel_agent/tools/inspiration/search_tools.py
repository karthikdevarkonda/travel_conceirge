import os
import googlemaps
from google.adk.tools.tool_context import ToolContext

try:
    api_key = os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if api_key:
        gmaps = googlemaps.Client(key=api_key)
    else:
        gmaps = None
        print("⚠️ Warning: Google Maps API Key missing in environment variables.")
except Exception as e:
    gmaps = None
    print(f"⚠️ Warning: Failed to initialize Google Maps client: {e}")

def search_places_tool(tool_context: ToolContext, query: str, page: int = 1) -> str:

    if not gmaps: 
        return "Error: Google Maps API key is not configured or client failed to load."
    
    print(f"\n[TOOL LOG] 🌍 Searching Places: '{query}' (Page {page})")
    cache_key = f"poi_search_{query.replace(' ', '_').lower()}"
    
    all_results = []
    
    if page == 1:
        try:
            if "tourist" not in query.lower() and "attraction" not in query.lower() and "visit" not in query.lower():
                search_query = f"Top rated tourist attractions in {query}"
            else:
                search_query = query
                
            response = gmaps.places(query=search_query)
            
            if not response or 'results' not in response: 
                return f"No places found for '{query}'."
            
            raw_results = response['results']
            
            valid_results = [p for p in raw_results if p.get('user_ratings_total', 0) > 500]
            
            valid_results.sort(key=lambda x: x.get('user_ratings_total', 0), reverse=True)
            
            all_results = valid_results if valid_results else raw_results
            
            tool_context.state[cache_key] = all_results
            
        except Exception as e: 
            return f"Error connecting to Google Maps API: {str(e)}"

    else:
        all_results = tool_context.state.get(cache_key, [])
        if not all_results:
            return search_places_tool(tool_context, query, page=1)

    RESULTS_PER_PAGE = 5
    start_index = (page - 1) * RESULTS_PER_PAGE
    end_index = start_index + RESULTS_PER_PAGE
    
    batch = all_results[start_index:end_index]
    
    if not batch:
        return "No more results to show. You have reached the end of the list."

    formatted_results = [f"**Found {len(all_results)} places. Showing {start_index+1}-{min(end_index, len(all_results))}:**\n"]
    
    for place in batch:
        name = place.get('name', 'Unknown')
        addr = place.get('formatted_address', 'Address unavailable')
        rating = place.get('rating', 'N/A')
        user_ratings = place.get('user_ratings_total', 0)
        
        raw_types = place.get('types', [])
        ignored_tags = {'point_of_interest', 'establishment', 'tourist_attraction'}
        clean_types = [t.replace('_', ' ').title() for t in raw_types if t not in ignored_tags][:2]
        type_str = ", ".join(clean_types) if clean_types else "Attraction"
        
        entry = (
            f"**{name}** (⭐ {rating} | {user_ratings} reviews)\n"
            f"   - *Type:* {type_str}\n"
            f"   - *Address:* {addr}"
        )
        formatted_results.append(entry)
        
    total_pages = int(len(all_results)/RESULTS_PER_PAGE) + (1 if len(all_results)%RESULTS_PER_PAGE else 0)
    formatted_results.append(f"\n*(Page {page} of {total_pages})*")
    
    return "\n\n".join(formatted_results)
