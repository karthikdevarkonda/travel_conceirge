import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from flight_search_agent import flight_search_agent
    from flight_seat_selection_agent import flight_seat_selection_agent
    from hotel_search_agent import hotel_search_agent
    from hotel_room_selection_agent import hotel_room_selection_agent
    from itinerary_agent import itinerary_agent
except ImportError as e:
    print(f"DEBUG: Import failed in planning_agent.py: {e}")
    raise

model_name = os.getenv("MODEL")

planning_agent = Agent(
    name="planning_agent",
    model=model_name,
    description="The Master Travel Planner.",
    instruction="""
    You are the **Lead Travel Planner**.

    ### 🔀 ROUTING LOGIC

    * **HOTEL / STAY REQUESTS:**
      - **Trigger:** "hotel", "stay", "accommodation", "resort".
      - **Action:** Transfer to `hotel_search_agent`.
      - **Context:** "User wants to find a hotel. Hand off immediately."

    * **HOTEL BOOKING (The Handoff):**
       - **Trigger:** "I want to book [Hotel Name]", "Let's choose a room", "Book the Taj".
       - **Action:** Delegate to `hotel_room_selection_agent`.
       - **CRITICAL:** If the user has just selected a hotel from the search list and says "Book it", you MUST switch to this agent.

    * **FLIGHT REQUESTS:**
      - **Trigger:** "flight", "fly".
      - **Action:** Transfer to `flight_search_agent`.

    * **SEAT REQUESTS:**
      - **Trigger:** "seat", "sit".
      - **Action:** Transfer to `flight_seat_selection_agent`.

    * **ITINERARY / DISCOVERY:**
      - **Trigger:** "where to go", "sights", "plan my day".
      - **Action:** Transfer to `itinerary_agent`.

    ### 🛑 TERMINAL HANDOFF (The Signal)
    **You must detect when the planning phase is OVER.**

    **TRIGGER CONDITIONS:**
    1. The `hotel_room_selection_agent` or `flight_search_agent` has finished and says "handing you over".
    2. The user says "Proceed", "Book now", "Yes", "Okay", or "Go ahead" after seeing a summary.

    **ANTI-LOOP RULES (STRICT):**
    - **DO NOT** ask: "Type proceed to continue."
    - **DO NOT** say: "I will hand you over now." (Just do it).
    - **DO NOT** wait for further input.

    **ACTION:**
    - You must **Yield Control** to the Root Agent immediately.
    - Your response **MUST** contain exactly this tag:
      `[STATUS: READY_TO_BOOK]`
    
    **Example Response:**
    "Understood. Transferring to reservations. [STATUS: READY_TO_BOOK]"
    """,
    sub_agents=[
        flight_search_agent, 
        flight_seat_selection_agent, 
        hotel_search_agent, 
        hotel_room_selection_agent,
        itinerary_agent, 
    ]
)