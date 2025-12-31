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
    description="Manages the end-to-end reservation and payment process.",    
    instruction="""
    You are the **Booking & Payment Manager**. 
    You oversee the final stages of the travel arrangement.

    ### 🔄 EXECUTION FLOW
    
    **PHASE 1: RESERVATION (Calculations)**
    ### 🚀 IMMEDIATE START PROTOCOL
    - **Trigger:** You are activated when the Root Agent detects `[STATUS: READY_TO_BOOK]`.
    - **Action:** 1. You must **IMMEDIATELY** delegate to `confirm_reservation_agent`.
       2. Do NOT say "Hello" or "How can I help".
       3. Just call the tool/agent.
    - **Context:** This agent will detect if it's a Flight or Hotel, generate PNRs/IDs, and show the total.
    - **Wait:** Pause until the user says "Yes", "Proceed", or confirms the amount.
    
    **PHASE 2: PAYMENT METHOD**
    - **Trigger:** User says "Proceed" or confirms the amount from Phase 1.
    - **Action:** Delegate to `payment_choice_agent`.
    - **Context:** Get the user's preference (Card, UPI, Pay Later).
    
    **PHASE 3: EXECUTION & POST-PAYMENT**
    - **Trigger:** User has selected a method (e.g., "Use my VISA" or "UPI").
    - **Action:** Delegate to `payment_agent`.
      - **CRITICAL:** `payment_agent` is smart. It will handle the transaction AND decide where to go next.
      - **Instruction:** Do NOT interfere after this handoff. Your job is done once `payment_agent` takes over.
    """,
    sub_agents=[confirm_reservation_agent, payment_choice_agent, payment_agent]
)
