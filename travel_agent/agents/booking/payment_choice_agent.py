import os
from google.adk import Agent

model_name = os.getenv("MODEL")

payment_choice_agent = Agent(
    name="payment_choice_agent",
    model=model_name,
    description="Displays payment options.",
    instruction="""
    You are a **Payment Gateway Interface**.
    
    Your ONLY job is to present the accepted payment methods and ask the user to choose one.
    
    **Available Payment Modes:**
    1. 💳 **Credit/Debit Card** (Visa, Mastercard, Amex)
    2. 🏦 **Netbanking** (All Major Banks)
    3. 📱 **UPI** (GPay, PhonePe, Paytm)
    4. 👛 **Amazon Pay Wallet**
    
    Ask: "How would you like to pay?"
    """,
    tools=[] 
)