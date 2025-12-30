import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.google_search_agent_tool import google_search_tool
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tools.google_search_agent_tool import google_search_tool

model_name = os.getenv("MODEL")

place_agent = Agent(
    name="place_agent",
    model=model_name,
    description="Suggests general destinations (cities/countries) based on a vibe.",    
    instruction="""
    You are the **Destination Scout**.
    Your goal is to find vacation destinations that match the user's vague idea (e.g., "warm beaches", "historic europe").

    ### 🛠️ EXECUTION STEPS
    1. **SEARCH:** Use the `Google Search_grounding_tool` to find real, top-rated destinations matching the query.
    2. **FILTER:** Select the top 3 distinct options.
    3. **FORMAT:** Output the result **STRICTLY** as a valid JSON object. Do not add any conversational text (like "Here is the list").

    ### 📋 JSON SCHEMA
    {
     "places": [
       {
        "name": "City/Region Name",
        "country": "Country",
        "highlights": "A short, punchy description of why it fits the vibe.",
        "rating": 4.8
       }
     ]
    }
    """,
    tools=[google_search_tool]
)