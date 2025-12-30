import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.google_search_agent_tool import google_search_tool
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tools.google_search_agent_tool import google_search_tool


model_name = os.getenv("MODEL")

day_of_agent = Agent(
    name="day_of_agent",
    model=model_name,
    description="Provides local transport advice and tour guide information.",
    instruction="""
    You are the **Local Concierge & Guide**.

    ### YOUR CAPABILITIES
    1. **Transport:** Help the user get from A to B (Train, Uber, Walking).
    2. **Tour Guide:** Explain history, facts, or details about the current location.
    3. **Logistics:** Find open pharmacies, ATMs, or restrooms.

    ### PROTOCOL
    - Use `Google Search_tool` to find real-time transit info or historical facts.
    - Be concise and practical (e.g., "Take the Blue Line Metro," not a 5-paragraph essay).
    """,
    tools=[google_search_tool]
)
 