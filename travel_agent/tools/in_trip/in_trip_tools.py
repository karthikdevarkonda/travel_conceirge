import os
import requests
import datetime
from google.adk.tools.tool_context import ToolContext

# Reuse your working Search API setup
SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"

def _fetch_live_data(query: str, label: str) -> str:
    """Helper to fetch real-time data from the web."""
    print(f"\n[TOOL LOG] 📡 Monitor Check ({label}): {query}")

    api_key = os.getenv("SEARCHAPI_API_KEY") or os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return f"Error: API Key missing for {label}."

    params = {
        "engine": "google", "q": query, "api_key": api_key,
        "gl": "us", "hl": "en", "num": 3
    }
    try:
        response = requests.get(SEARCHAPI_BASE_URL, params=params, timeout=15)
        data = response.json()
        snippets = [r.get("snippet", "") for r in data.get("organic_results", [])]

        if not snippets: return f"No live data found for {label}."
        return f"**{label} Status:**\n" + "\n".join(snippets)
    except Exception as e:
        return f"Error checking {label}: {str(e)}"

# --- 1. FLIGHT STATUS CHECK ---
def flight_status_check(tool_context: ToolContext, flight_number: str, date: str) -> str:
    """Checks real-time status (On Time, Delayed, Cancelled) of a specific flight."""
    query = f"flight status {flight_number} {date} live tracker"
    return _fetch_live_data(query, f"Flight {flight_number}")

# --- 2. WEATHER IMPACT CHECK ---
def weather_impact_check(tool_context: ToolContext, location: str, date: str) -> str:
    """Checks for specific weather conditions that might disrupt travel."""
    query = f"weather forecast {location} {date} rain storm disruption"
    return _fetch_live_data(query, f"Weather in {location}")

# --- 3. EVENT BOOKING CHECK (Internal + External) ---
def event_booking_check(tool_context: ToolContext, event_name: str, location: str) -> str:
    """
    Checks if an event is still scheduled/open (External) and confirms booking exists (Internal).
    """
    # A. Check Internal Memory first
    bookings = tool_context.state.get("event_bookings", [])
    booking_status = "❌ No internal booking record found."
    for b in bookings:
        if event_name.lower() in str(b).lower():
            booking_status = f"✅ Confirmed Booking ID: {b.get('id', 'Unknown')}"
            break

    # B. Check External Status (Is the venue open?)
    query = f"is {event_name} in {location} open today news cancellation"
    external_status = _fetch_live_data(query, "Event Status")

    return f"{booking_status}\n\n{external_status}"
 