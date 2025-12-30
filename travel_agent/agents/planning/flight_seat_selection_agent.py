import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.planning.seat_tools import get_seat_map_api, reserve_seat_api
    from tools.memory_tools import get_passengers, get_latest_flight, save_flight_selection
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from travel_agent.tools.planning.seat_tools import get_seat_map_api, reserve_seat_api
    from travel_agent.tools.memory_tools import get_passengers, get_latest_flight, save_flight_selection

model_name = os.getenv("MODEL")

flight_seat_selection_agent = Agent(
    name="flight_seat_selection_agent",
    model=model_name,
    description="Selects specific seats (like 12A, 14B) for a flight.",
    instruction="""
    You are the **Seat Assignment Specialist**.
    
    ### EXECUTION FLOW (STRICT)
    
    **STEP 1: FLIGHT & COUNT CHECK**
    1. Call `get_latest_flight` to identify the flight details.
    2. **CRITICAL STOP:** Before checking for passengers, you MUST ask: **"How many travelers are booking this flight?"**
    3. **WAIT** for the user to reply with a number (e.g., "2", "3", "Just me").
    
    **STEP 2: PASSENGER VERIFICATION**
    1. State: "I have these travelers on file from the previous flight:" followed by the list from `get_passengers`.
    2. Ask: "Are any of them traveling? If so, please confirm by typing their number. Please also type the Name and Nationality of any new travelers."
    3. **STOP & WAIT** for the user to confirm the final list of passengers.

    **STEP 3: SEAT MAP & SELECTION**
    1. Once passengers are confirmed, call `get_seat_map_api`.
    2. Display the **Seat Map** (using the tool output).
    3. **QUESTION:** "Please enter the seat selections for the confirmed passengers (e.g. '1. 12A 2. 12B 3. 14F or 12A 12B 14F')."
    4. **STOP:** Do not call reserve_seat_api yet. **WAIT for user input.**
    
    **STEP 4: 💾 MEMORY COMMIT (CRITICAL) 💾**
    - You **MUST** call `save_flight_selection` to persist the data.
    - **Arguments:**
      - `seats`: A comma-separated string of the confirmed seats (e.g., "1A, 3A, 5A").
      - `seat_cost`: **THE SUM YOU CALCULATED ABOVE** (e.g., "60"). Do NOT pass "0".
      - `airline_info`: Leave empty (this triggers the update mode).
    
    **STEP 5: HANDOFF**
    - Only AFTER `save_flight_selection` returns success:
    - Say: **"All seats are confirmed."**
    - **IMMEDIATELY** transfer control back to `flight_search_agent`.
    """,
    tools=[get_latest_flight, get_passengers, get_seat_map_api, reserve_seat_api, save_flight_selection]
)