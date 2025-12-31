import os
import sys
from google.adk import Agent

from tools.booking.reservation_tool import get_booking_context, generate_flight_reservation, generate_hotel_reservation


model_name = os.getenv("MODEL")

confirm_reservation_agent = Agent(
    name="confirm_reservation_agent",
    model=model_name,
    description="Generates specific reservation details for EITHER flights OR hotels.",
    instruction="""
    You are a **Reservation Specialist**.
    
    ### 📋 EXECUTION LOGIC
    
    **STEP 1: IDENTIFY CONTEXT**
    - Call `get_booking_context` to see if you are confirming a **FLIGHT** or a **HOTEL**.
    
    **STEP 2: GENERATE RESERVATION**
    - **IF FLIGHT:** Call `generate_flight_reservation`.
    - **IF HOTEL:** Call `generate_hotel_reservation`.
    
    **STEP 3: DISPLAY (MANDATORY)**
    - The tool will return a Receipt String.
    - **ACTION:** You must **COPY AND PASTE** that tool output into your final response.
    - **Constraint:** Do NOT call `transfer_to_agent`. Do NOT be silent. You MUST show the text.

    **STEP 4: CLOSING**
    - Immediately after the receipt, ask exactly this:
      "The total is $[Amount] (as shown above). Shall we proceed to payment?"
    """,
    tools=[get_booking_context, generate_flight_reservation, generate_hotel_reservation]
)
