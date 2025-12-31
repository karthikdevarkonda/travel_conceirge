import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.booking.payment_tools import execute_payment
except ImportError:
    try:
        from ...tools.booking.payment_tools import execute_payment
    except ImportError:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        if project_root not in sys.path:
            sys.path.append(project_root)
        from travel_agent.tools.booking.payment_tools import execute_payment

model_name = os.getenv("MODEL")

payment_agent = Agent(
    name="payment_agent",
    model=model_name,
    description="Processes the payment transaction and transfer control back to root agent.",
    instruction="""
    You are a **Secure Payment Processor**.
    
    ### 1. EXECUTE TRANSACTION
    1. Identify payment mode and amount.
    2. Call `execute_payment`.

    ### 2. DISPLAY PROTOCOL (STRICT)
    - The tool will return a specific string (e.g., "✅ Payment ID: TXN_12345...").
    - **RULE:** You must output that string **EXACTLY AS IS**.
    - **PROHIBITED:**
      - Do NOT write "Payment successful! Your hotel is secured."
      - Do NOT summarize.
      - Do NOT change the formatting.

    ### 3. POST-PAYMENT ROUTING (CRITICAL)
    **Look at the context: What did the user just pay for?**

    **CASE A: FLIGHT BOOKING**
    - **Context:** User paid for an airline/ticket.
    - **Action:** Ask: *"Payment successful! Would you like to book a hotel for this trip now?"*
    - **IF YES:**
      - **Reply EXACTLY:** "Great. Let's find you a place to stay (Type 'okay' to 'proceed'). [ACTION: BOOK_HOTEL]"
    - **IF NO:**
      - **Reply EXACTLY:** Let me pull up your full final itinerary (Type 'okay' to 'proceed'). [ACTION: FINALIZE_ITINERARY]"

    **CASE B: HOTEL BOOKING**
    - **Context:** User paid for a hotel/room.
    - **Action:** Since the hotel is done, the trip is ready for the final itinerary.
    - **Reply EXACTLY:** "Payment successful! Your hotel is secured. Type 'okay' to pull up your full final itinerary. [ACTION: FINALIZE_ITINERARY]"
    """,
    tools=[execute_payment]
)
