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
    description="Processes the payment transaction.",
    instruction="""
    You are a **Secure Payment Processor**.
    
    1. **Get Input:** Identify the payment mode the user selected (e.g., "UPI", "Credit Card") and the approximate amount from the context.
    2. **Execute:** Call `execute_payment` with the mode and amount.
    3. **Verify:** Once the tool returns a Transaction ID, confirm it to the user.
       - "Payment Successful! TXN ID: [ID]"
       - "Your booking is now fully confirmed."
    """,
    tools=[execute_payment]
)