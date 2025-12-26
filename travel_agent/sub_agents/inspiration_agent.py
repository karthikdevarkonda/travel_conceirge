import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from place_agent import place_agent
from poi_agent import poi_agent

model_name = os.getenv("MODEL")

inspiration_agent = Agent(
    name="inspiration_agent",
    model=model_name,
    description="Helps the user dream up a trip. Manages destination and attraction search.",
    instruction="""
    You are the Head of Inspiration. Your job is to route the user to the right specialist.

    RULES FOR ROUTING:
    1. If the user mentions a specific CITY or COUNTRY (e.g. "What to do in Paris?"), delegate to 'poi_agent'.
    2. If the user mentions an ACTIVITY or VIBE but NO LOCATION (e.g. "Trekking places", "Beach vacation", "Where should I go?"), delegate to 'place_agent'.
    
    Do not transfer back and forth. Make a decision.
    """,
    sub_agents=[place_agent, poi_agent] 
)