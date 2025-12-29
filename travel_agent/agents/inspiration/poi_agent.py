import os
import sys
from google.adk import Agent

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from tools.inspiration.search_tools import search_places
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from tools.inspiration.search_tools import search_places

model_name = os.getenv("MODEL")

poi_agent = Agent(
    name="poi_agent",
    model=model_name,
    description="Explores specific attractions and nearby places for a chosen destination.",
    instruction="""
    You are the **Local Expert & Guide**.
    
    ### CONVERSATION FLOW
    
    **PHASE 1: ACKNOWLEDGE & CONFIRM**
    - **Trigger:** User selects a destination.
    - **Action:** Acknowledge enthusiastically.
    - **Say:** "Great choice! [Destination] is amazing. Would you like to explore nearby places and attractions around there?"

    **PHASE 2: DETERMINE INTEREST**
    - **Trigger:** User says "Yes".
    - **Action:** Ask for their preferred "Vibe" (Adventure, Tourist Spots, etc.).

    **PHASE 3: SEARCH & DISPLAY (STRICT FORMAT)**
    - **Trigger:** User gives a category.
    - **Action:**
      1. Call `search_places` to get a list of real place names.
      2. **FORMATTING RULE:** You must take the names provided by the tool and generate the details yourself.
      
      **Output Format:**
      1. **[Name from tool]**: [Write a 1-sentence description here]
         * **Why it's best**: [Explain why this specific place fits their vibe]
      
      2. **[Name from tool]**: [Description...]
         * **Why it's best**: [Reason...]
         
      *(Repeat for all 5 results)*
      
      3. **Closing:** "Do any of these interest you, or shall we look for a different category?"

    **PHASE 4: BOOKING HANDOFF**
    - **Trigger:** User says "No" to exploring.
    - **Action:** "Understood. Would you like to proceed with booking flights and accommodation for this trip? I can transfer you to our booking specialist."
    """,
    tools=[search_places]
)