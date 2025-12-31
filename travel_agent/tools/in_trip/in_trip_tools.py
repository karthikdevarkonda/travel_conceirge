import os
import requests
import datetime
from google.adk.tools.tool_context import ToolContext

SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"

def _fetch_live_data(query: str, label: str) -> str:
    """
    Helper to fetch live data with improved error handling, formatting, and source verification.
    """
    print(f"\n[TOOL LOG] 📡 Monitor Check ({label}): {query}")

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return f"SYSTEM NOTICE: API Key missing. Cannot verify {label} live status."

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "gl": "us", "hl": "en",
        "num": 4,             
        "time_period": "last_day" 
    }

    try:
        response = requests.get(SEARCHAPI_BASE_URL, params=params, timeout=10)
        
        if response.status_code != 200:
             return f"⚠️ Warning: external search unavailable ({response.status_code}). Please verify manually."

        data = response.json()
        
        snippets = []
        if "organic_results" in data:
            for r in data["organic_results"]:
                title = r.get("title", "Unknown Source")
                body = r.get("snippet", "No details")
                link = r.get("link", "")
                snippets.append(f"- **{title}**: {body} [Source: {link}]")

        if not snippets: 
            return f"No immediate alerts found for {label}. Likely operating normally."

        return (
            f"**🔎 Real-Time Findings for {label}:**\n" 
            + "\n".join(snippets) + 
            "\n\n*[SYSTEM ADVICE]: Analyze the timestamps in the snippets above. Prioritize the most recent status.*"
        )

    except Exception as e:
        print(f"❌ Error in {label}: {e}")
        return f"⚠️ Connection Error. Could not verify {label}."

def flight_status_check(tool_context: ToolContext, flight_number: str, date: str) -> str:
    """
    Checks official status including specific Departure and Arrival times.
    """
    query = (
        f"official flight status {flight_number} {date} "
        f"scheduled actual departure arrival time gate terminal live"
    )
    return _fetch_live_data(query, f"Flight {flight_number}")

def weather_impact_check(tool_context: ToolContext, location: str, date: str) -> str:
    """
    Checks specifically for disruptions (storms, severe warnings).
    """
    query = f"hourly weather forecast {location} {date} severe weather warning rain storm alert"
    return _fetch_live_data(query, f"Weather in {location}")

def event_booking_check(tool_context: ToolContext, event_name: str, location: str) -> str:
    """
    Checks internal booking memory AND external open/close status.
    """
    bookings = tool_context.state.get("event_bookings", [])
    booking_status = "❌ No internal booking record found."
    
    for b in bookings:
        if event_name.lower() in str(b).lower():
            booking_status = f"✅ Confirmed Booking ID: {b.get('id', 'Unknown')}"
            break

    query = f"is {event_name} {location} open today opening hours special closure news"
    external_status = _fetch_live_data(query, f"Venue Status ({event_name})")

    return f"{booking_status}\n\n{external_status}"
