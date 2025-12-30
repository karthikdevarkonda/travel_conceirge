import os
import requests
import datetime
from google.adk.tools.tool_context import ToolContext

SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"

def _fetch_official_data(query: str, context_label: str) -> str:
    print(f"\n[TOOL LOG] 🔍 Searching {context_label}: '{query}'")

    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return f"CRITICAL ERROR: API Key missing. Cannot fetch {context_label}."

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "gl": "us", "hl": "en",
        "num": 4  
    }

    try:
        response = requests.get(SEARCHAPI_BASE_URL, params=params, timeout=20)
        data = response.json()

        snippets = []
        if "organic_results" in data:
            for result in data["organic_results"]:
                title = result.get("title", "No Title")
                text = result.get("snippet", "No snippet")
                link = result.get("link", "No link")
                snippets.append(f"- **{title}**: {text} (Source: {link})")

        if not snippets:
            return f"Warning: No live data found for {context_label}. Please consult official sources manually."

        return (
            f"**ℹ️ {context_label} Search Findings:**\n"
            f"{chr(10).join(snippets)}\n\n"
            f"**[SYSTEM INSTRUCTION]:** Use the data above to answer the user's question. Cite the sources provided."
        )

    except Exception as e:
        print(f"❌ Network Error in {context_label}: {str(e)}")
        return f"Error fetching {context_label}: {str(e)}"


def check_visa_requirements(tool_context: ToolContext, destination_country: str) -> str:
    passengers = tool_context.state.get("passengers", [])
    if not passengers:
        return "Error: No passengers found. Please identify travelers and nationalities first."

    nationality_map = {}
    for p in passengers:
        nat = p.get("nationality", "Unknown")
        name = p.get("name", "Traveler")

        if not nat or nat == "Unknown":
            return f"Error: Nationality missing for {name}. Please ask the user."

        if nat not in nationality_map:
            nationality_map[nat] = []
        nationality_map[nat].append(name)

    reports = []
    for nationality, names in nationality_map.items():
        query = (
            f"official tourist visa requirements for {nationality} citizen to {destination_country} "
            f"government site validity application process multiple entry"
        )
        result_text = _fetch_official_data(query, f"Visa Rules ({nationality} -> {destination_country})")
        reports.append(f"### 🛂 Visa Check for {nationality} Citizens ({', '.join(names)})")
        reports.append(result_text)
        reports.append("-" * 40)

    return "\n".join(reports)

def check_medical_requirements(tool_context: ToolContext, destination_country: str) -> str:
    query = (
        f"CDC WHO travel health requirements {destination_country} "
        f"mandatory yellow fever vaccine malaria prophylaxis dengue outbreak"
    )
    return _fetch_official_data(query, f"Medical Requirements ({destination_country})")

def check_travel_advisory(tool_context: ToolContext, destination_country: str) -> str:
    query = (
        f"official travel advisory safety level {destination_country} "
        f"US State Department UK Foreign Office Canada Travel civil unrest crime terrorism"
    )
    return _fetch_official_data(query, f"Travel Advisory ({destination_country})")

def storm_monitor(tool_context: ToolContext, destination_country: str, travel_dates: str = "upcoming trip") -> str:
    current_month = datetime.datetime.now().strftime("%B %Y")
    query = (
        f"severe weather alerts warnings {destination_country} {travel_dates} "
        f"NOAA tropical storm hurricane typhoon cyclone forecast {current_month}"
    )
    return _fetch_official_data(query, f"Storm Monitor ({destination_country})")
 
