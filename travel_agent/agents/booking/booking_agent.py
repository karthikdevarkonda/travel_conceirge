import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from agents.booking.confirm_reservation_agent import confirm_reservation_agent
    from agents.booking.payment_choice_agent import payment_choice_agent
    from agents.booking.payment_agent import payment_agent
except ImportError:
    try:
        from .confirm_reservation_agent import confirm_reservation_agent
        from .payment_choice_agent import payment_choice_agent
        from .payment_agent import payment_agent
    except ImportError:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
        from travel_agent.agents.booking.confirm_reservation_agent import confirm_reservation_agent
        from travel_agent.agents.booking.payment_choice_agent import payment_choice_agent
        from travel_agent.agents.booking.payment_agent import payment_agent

model_name = os.getenv("MODEL")

booking_agent = Agent(
    name="booking_agent",
    model=model_name,
    description="Manages the end-to-end booking and payment flow.",
    instruction="""
    You are the **Booking & Payment Manager**. 
    You oversee the final stages of the travel arrangement.

    ### 🔄 EXECUTION FLOW
    
    **PHASE 1: RESERVATION (Calculations)**
    ### 🚀 IMMEDIATE START PROTOCOL
    -  **As soon as you receive control:**
    1. You must **IMMEDIATELY** delegate to `confirm_reservation_agent`.
    2. Do NOT say "Hello" or "How can I help".
    - This agent will detect if it's a Flight or Hotel, generate PNRs for flights and if it's a Hotel it will generate a reservation ID, and show the total.
    - Wait until the user says "Yes" or "Proceed".
    
    **PHASE 2: PAYMENT METHOD**
    - Delegate to `payment_choice_agent` to get the user's preference (Card, UPI, etc.).
    
    **PHASE 3: EXECUTION**
    - Once a method is chosen, Delegate to `payment_agent` to finalize the transaction.
    - After payment is successful, thank the user.
    """,
    sub_agents=[confirm_reservation_agent, payment_choice_agent, payment_agent]
)