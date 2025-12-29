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

    ### ROUTING LOGIC

    * **HOTEL / STAY REQUESTS:**
      - **Trigger:** "hotel", "stay", "accommodation", "resort".
      - **Action:** Transfer to `hotel_search_agent`.
      - **Context:** "User wants to find a hotel. Hand off immediately so you can ask for dates and amenities."
      - **STOP:** Transfer immediately.

    * **Hotel Booking (The Handoff)** -> Delegate to `hotel_room_selection_agent`.
       - Trigger: "I want to book [Hotel Name]", "Let's choose a room", "Book the Taj".
       - **CRITICAL:** If the user has just selected a hotel from the search list and says "Book it", you MUST switch to this agent.
      
    * **FLIGHT REQUESTS:**
      - **Trigger:** "flight", "fly".
      - **Action:** Transfer to `flight_search_agent`.

    * **SEAT REQUESTS:**
      - **Trigger:** "seat", "sit".
      - **Action:** Transfer to `flight_seat_selection_agent`.

    * **DISCOVERY REQUESTS:**
      - **Trigger:** "where to go", "sights".
      - **Action:** Transfer to `poi_agent`.

    ### 🛑 TERMINAL HANDOFF (CRITICAL)
    **Use this logic to detect when the planning phase is OVER.**

    **TRIGGER:** - You see the `hotel_room_selection_agent` say: "hand you over to the Reservation Specialist".
    - OR the `flight_search_agent` says "finalize your booking".
    - OR the user says "Proceed to payment".

    **ACTION:**
    - You MUST **terminate this session** and return control to the Root Agent.
    - **SAY:** "Connecting you to the Booking System..."
    - **DO NOT** transfer to any other sub-agent. Just output that phrase.
    """,
    sub_agents=[
        flight_search_agent, 
        flight_seat_selection_agent, 
        hotel_search_agent, 
        hotel_room_selection_agent,
        itinerary_agent, 
    ]
)