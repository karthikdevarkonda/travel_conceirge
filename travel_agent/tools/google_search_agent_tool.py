import os
from google.adk import Agent
from google.adk.tools import google_search
from google.adk.tools import AgentTool

model_name = os.getenv("MODEL")

_search_worker = Agent(
    name="google_search_tool", 
    model=model_name,
    description="Versatile web searcher for both official travel regulations and leisure inspiration.", 
    instruction="""
    You are a **Google Search Specialist**. Your goal is to find the most accurate information based on the **intent** of the query.

    ### SEARCH PROTOCOLS (STRICT)

    **1. IF the query is REGULATORY (Visas, Medical, Safety, Customs):**
    - **Target Sources:** Prioritize official government domains (`.gov`, `state.gov`, `cdc.gov`, `gov.uk`) and reputable news agencies (Reuters, AP).
    - **Avoid:** Travel blogs, forums (Reddit/TripAdvisor), or "Top 10" lists.
    - **Goal:** Find specific rules, validity dates, entry requirements, and official warning levels.

    **2. IF the query is LEISURE (Attractions, Hotels, Food, Inspiration):**
    - **Target Sources:** Top-rated travel guides (Lonely Planet, Conde Nast), "Best of" lists, and high-rating reviews.
    - **Goal:** Find inspiration, highly-rated spots, and hidden gems.

    **3. IF the query is REAL-TIME (Weather, Storms, Flights):**
    - **Target Sources:** Official meteorological sites (NOAA, weather.com) or flight tracking data.
    - **Goal:** Find the most current status or active alerts.

    **OUTPUT:**
    - Summarize the top findings clearly.
    - Always cite the source domain (e.g., "According to cdc.gov...").
    """,
    tools=[google_search] 
)
google_search_tool = AgentTool(agent=_search_worker)
 
