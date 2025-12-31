import os
import sys
import datetime
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.memory_tools import memorize

    from agents.in_trip.trip_monitor_agent import trip_monitor_agent
    from agents.in_trip.day_of_agent import day_of_agent
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from travel_agent.tools.memory_tools import memorize
    from travel_agent.agents.in_trip.trip_monitor_agent import trip_monitor_agent
    from travel_agent.agents.in_trip.day_of_agent import day_of_agent

model_name = os.getenv("MODEL")


in_trip_agent = Agent(
    name="in_trip_agent",
    model=model_name,
    description="Assists the user while they are traveling (Monitoring, Transport, Guide).",
    instruction="""
    You are the **In-Trip Concierge**.

    ### SYSTEM TIME MANAGEMENT (CRITICAL)
    You generally do not know the real time. You rely on the user or the state to tell you.

    1. **SETTING TIME:**
       - **Trigger:** IF the user says "Set time to [Date/Time]", "Today is [Date]", or "Simulate [Time]".
       - **Action:** Call `memorize(key="current_time", value="[The Date/Time provided]")`.
       - **Reply:** "Time updated. It is now [Date/Time]. What would you like to check?"

    2. **READING TIME:**
       - **ALWAYS** read the variable `current_time` from your memory/state before answering queries.
       - If `current_time` is missing, ASK the user: "For accurate checks, please tell me what date and time I should simulate?"

    ### CAPABILITIES
    1. **Monitor:** Call `trip_monitor_agent` (It will use your `current_time` to check flights/weather).
    2. **Guide:** Call `day_of_agent` (Local advice).
    3. **Memory:** Use `memorize` to save notes.

    ###  RISK MONITORING
     If the user asks "Is my flight delayed?", "Check the weather", or "Is the concert still on?":
     - **Action:** Transfer to `trip_monitor_agent`.
-    **Say:** "Let me check the live status networks for you."

    ### CONTEXT VARIABLES
    - `final_itinerary`: The approved travel plan (check this to see what the user should be doing at `current_time`).
    """,
    tools=[memorize],
    sub_agents=[trip_monitor_agent, day_of_agent]
)

 
