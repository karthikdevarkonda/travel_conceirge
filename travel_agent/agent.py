import os
import sys
from dotenv import load_dotenv
from google.adk import Agent
from google.genai import types

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from sub_agents.flight_search_agent import flight_search_agent
from sub_agents.inspiration_agent import inspiration_agent

load_dotenv()
model_name = os.getenv("MODEL")


itinerary_agent = Agent(
    name="itinerary_agent",
    model=model_name,
    description="Builds day-by-day itineraries.",
    instruction="Create detailed daily plans."
)

hotel_search_agent = Agent(
    name="hotel_search_agent",
    model=model_name,
    description="Searches for hotel options.",
    instruction="Find hotels that match the user's budget and location preferences."
)

planning_agent = Agent(
    name="planning_agent",
    model=model_name,
    description="Plans the logistics (flights, hotels, itinerary).",
    instruction="Once a destination is picked, use your sub-agents to build the trip components.",
    sub_agents=[flight_search_agent, hotel_search_agent, itinerary_agent] 
)

booking_agent = Agent(
    name="booking_agent",
    model=model_name,
    description="Handles reservations and payments.",
    instruction="Finalize the booking and take payment.",
)


root_agent = Agent(
    name="root_agent",
    model=model_name,
    description="The main travel concierge interface.",
    instruction="""
    You are the Travel Concierge.
    
    ### YOUR ROLE
    You are the first point of contact. Your job is to understand the user's needs *before* routing them.

    ### CONVERSATION FLOW (Strictly follow this):
    
    1. **IF User says "Hi" or general greeting:**
       - Welcome them warmly and ask how you can help plan their dream vacation.
       
    2. **IF User says "Plan a trip to [City/Country]":**
       - **DO NOT TRANSFER YET.**
       - Acknowledge the destination enthusiastically.
       - **ASK:** "To help me tailor the perfect vacation for you, could you tell me what kind of experience you're looking for? (e.g., Adventure, Relaxing, Cultural, Tourist Attractions)"
       
    3. **IF User provides the "Vibe/Experience":**
       - **SILENTLY TRANSFER** to the 'inspiration_agent'.

    4. **IF User asks for specific logistics (Flights/Hotels):**
       - Transfer directly to 'planning_agent'.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    sub_agents=[inspiration_agent, planning_agent, booking_agent]
)