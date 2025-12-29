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
    
    **STEP 3: PRESENTATION**
    - Display the formatted reservation details returned by the tool.
    - Ask: "The total for this reservation is $[Amount]. Shall we proceed to payment?"
    """,
    tools=[get_booking_context, generate_flight_reservation, generate_hotel_reservation]
)