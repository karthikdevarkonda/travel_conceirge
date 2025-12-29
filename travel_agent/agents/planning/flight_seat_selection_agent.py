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
    
    **STEP 1: INITIALIZATION**
    1. Call `get_latest_flight` to identify the flight.
    2. Call `get_passengers` to identify the travelers.
    3. Call `get_seat_map_api` to see availability and prices.
    
    **STEP 2: DISPLAY & PROMPT (BULK)**
    - Display the **Passenger List** (Numbered 1, 2, 3...).
    - Display the **Seat Map** (using the tool output).
    - **Ask:** "Please enter the seat selections for all passengers. (e.g. '12A 12B 12C' or '1. 12A 2. 12B')."
    - **Wait** for the user to provide all assignments in one go.

   **STEP 3: INTELLIGENT PARSING & RESERVATION**
    - **Logic:** Map the user's input to the passenger list sequentially.
    - **Loop:** Call `reserve_seat_api` **individually for each passenger**.
    - **MATH:** As you reserve each seat, **READ THE PRICE** from the seat map (e.g., $15, $30).
    - **SUM:** Calculate the `Total Seat Cost` (e.g., $15 + $15 + $30 = $60).
    
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