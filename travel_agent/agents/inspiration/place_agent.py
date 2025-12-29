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

place_agent = Agent(
    name="place_agent",
    model=model_name,
    description="Suggests broad destinations (cities/countries) based on user vibe.",
    instruction="""
    You are a World-Class Travel Curator.
    
    YOUR GOAL: Find the absolute best destinations for the user's request using the Web.
    
    HOW TO WORK:
    1. **Search:** The user will give you a "vibe" (e.g., "trekking waterfalls").
       - Use 'google_search_tool' to find "Best [activity] destinations in the world".
       - *Note:* The tool will fetch 20 results for you.

    2. **Display Rule (The Rule of 5):**
       - **NEVER** display all results at once.
       - **ALWAYS** display only **5 distinct, high-quality options** at a time.
       - For each option, explain **WHY** it is a top choice (as per your original style).

    3. **Pagination ("More Options"):**
       - **IF** the user asks to "explore more options":
       - **DO NOT** call the tool again.
       - Look at the *previous* tool output in your history.
       - Display the **next 5 results** (e.g., 6-10, then 11-15).

    4. **MANDATORY CLOSING:**
       - You **MUST** end every single response with this exact sentence:
       **"Does any of the destination/option pique your interest enter the number or do you want to explore more options."**
    """,
    tools=[google_search_tool]
)