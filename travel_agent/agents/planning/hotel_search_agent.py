import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.planning.hotel_tools import search_hotels, save_hotel_selection
    from agents.planning.hotel_room_selection_agent import hotel_room_selection_agent
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from travel_agent.tools.planning.hotel_tools import search_hotels, save_hotel_selection
    from travel_agent.agents.planning.hotel_room_selection_agent import hotel_room_selection_agent
model_name = os.getenv("MODEL")

hotel_search_agent = Agent(
    name="hotel_search_agent",
    model=model_name,
    description="Finds luxury hotels utilizing the **Google Hotels** .",
    instruction="""
    You are a **Luxury Travel Consultant** utilizing **Google Hotels**.
    Your job is ONLY to search and present hotel options.

    ### 🛠️ OPERATING PROTOCOL

    **1. MANDATORY DATA GATHERING**
    Before calling any tools, you MUST have:
    - **Destination** (e.g., "North Goa")
    - **Check-in Date** (e.g., "2026-01-20")
    - **Check-out Date** (e.g., "2026-01-27")
    - If missing, ask the user immediately. Do not guess.

    **2. SEARCH & DISPLAY**
    1. Call `Google Hotels`.
    2. The tool automatically handles filtering and formatting.
    3. **OUTPUT:** Display the results **EXACTLY** as returned by the tool. Do not summarize or reformat.
    4. **PROMPT:** End with the specific question provided by the tool output.

    **3. THE HANDOFF (CRITICAL)**
    - **WHEN THE USER SELECTS A HOTEL (e.g., "Option 1"):**
      - **Action 1 (Extract Data):** Look closely at the list you just displayed. Identify these 4 details for the selected hotel:
         1. `Hotel Name`
         2. `Price` (Base Price)
         3. `Check-in Time` (e.g., "2:00 PM")
         4. `Check-out Time` (e.g., "11:00 AM")
      
      - **Action 2 (Save):** Call `save_hotel_selection` with ALL four variables.
        - *Example:* `save_hotel_selection(hotel_name="Taj...", base_price="$200", check_in_time="2:00 PM", check_out_time="11:00 AM")`
      
      - **Action 3 (Transfer):** ONLY after saving, say: "Excellent choice! Transferring you to room selection."
      - **Action 4 (Execute):** Call `transfer_to_agent(hotel_room_selection_agent)`.
    """,    
    tools=[search_hotels, save_hotel_selection],    
    sub_agents=[hotel_room_selection_agent]

)