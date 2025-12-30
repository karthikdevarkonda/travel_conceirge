import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.in_trip.in_trip_tools import flight_status_check, weather_impact_check, event_booking_check
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tools.in_trip.in_trip_tools import flight_status_check, weather_impact_check, event_booking_check


model_name = os.getenv("MODEL")

trip_monitor_agent = Agent(
    name="trip_monitor_agent",
    model=model_name,
    description="Proactively checks for travel disruptions.",
    instruction="""
    You are the **Trip Monitor**. Your ONLY job is to detect problems.

    ### EXECUTION FLOW
    1. **Analyze the Request:** Identify the Flight #, Location, or Event being asked about.
    2. **Check Status:** Use the appropriate tool (`flight_status_check`, etc.).
    3. **Report:**
       - If everything is fine, say "All Clear."
       - If there is a delay/storm/cancellation, **FLAG IT** clearly.
    """,
    tools=[flight_status_check, weather_impact_check, event_booking_check]
)