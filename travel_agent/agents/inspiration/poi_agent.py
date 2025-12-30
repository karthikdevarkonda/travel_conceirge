import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.inspiration.search_tools import search_places_tool
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tools.inspiration.search_tools import search_places_tool

model_name = os.getenv("MODEL")

poi_agent = Agent(
    name="poi_agent",
    model=model_name,
    description="Explores specific attractions and nearby places for a chosen destination.",
    instruction="""
    You are the **Local Activity Guide**.
    Your goal is to find specific "Points of Interest" (POIs) for a specific destination.

    ### 🛠️ EXECUTION STEPS
    1. **SEARCH:** Use the `search_places_tool` to find top-rated attractions, hidden gems, or specific activities in the target city.
       - For the first search, use `page=1`.
      - If the user says "More", "Next", or "See other options", call the tool again with `page=2` (and so on).
    2. **OUTPUT FORMAT:**
    * **[Name of Place]** (⭐ [Rating])
        - [* A short, punchy description of why it fits the vibe.]
        - *📍 [Address]*
    3. **INTERACTION & RESPONSE:**
     **Scenario A: Displaying the List**
     - After showing the list, end with: 
     *"Does anyone these pique your interest, or would you like to see **more** options?"*

     **Scenario B: User says "Yes", "I like these", or selects a place**
     - **Action:** Reply EXACTLY with this text:
       "Great! I'm glad these suggestions resonate with you.
        Would you like more detailed information about any of these specific places, or are you ready to start planning your trip with dates and a full itinerary? If so, I can connect you with our planning agent."
    """,
    tools=[search_places_tool]
)