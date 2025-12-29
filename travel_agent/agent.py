import os
import sys
from dotenv import load_dotenv
from google.adk import Agent
from google.genai import types

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from agents.inspiration.inspiration_agent import inspiration_agent
from agents.planning.planning_agent import planning_agent
from agents.booking.booking_agent import booking_agent


load_dotenv()
model_name = os.getenv("MODEL")

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
   
    **5. BOOKING PHASE (The Final Handoff):**
       - **TRIGGER:** If the `planning_agent` (or any sub-agent) says: **"Connecting you to the Booking System..."**
       - **ACTION:** Immediately transfer to `booking_agent`.
       - **SAY:** "Transferring you to the Booking Desk."
       - **Call:** `transfer_to_agent(booking_agent)`.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    sub_agents=[inspiration_agent, planning_agent, booking_agent]
)