import json
import os
import re
import traceback
from google.adk.tools.tool_context import ToolContext

def _get_db_path(context: ToolContext):
    session_id = "default"
    try:
        if context:
            if hasattr(context, 'session_id') and context.session_id:
                session_id = str(context.session_id)
            elif hasattr(context, 'session') and context.session:
                session_id = str(context.session)
    except:
        pass
    
    session_id = str(session_id)
    
    session_id = "".join(c for c in session_id if c.isalnum() or c in ('-', '_'))
    
    if len(session_id) > 50:
        session_id = session_id[:50]
        
    if not session_id: 
        session_id = "default"
        
    path = os.path.join(os.path.dirname(__file__), f'trip_memory_{session_id}.json')
    print(f"DEBUG: Memory File Path -> {path}")
    return path

def _load_db(context: ToolContext):
    file_path = _get_db_path(context)
    if not os.path.exists(file_path):
        return {"passengers": [], "flights": []}
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return {"passengers": [], "flights": []}

def _save_db(context: ToolContext, data):
    file_path = _get_db_path(context)
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print("DEBUG: Database successfully written to disk.")
    except Exception as e:
        print(f"CRITICAL ERROR writing DB: {e}")
        raise e

def add_passengers_bulk(tool_context: ToolContext, passenger_string: str) -> str:
    print(f"DEBUG: Adding passengers: {passenger_string}")
    try:
        db = _load_db(tool_context)
        if "passengers" not in db: db["passengers"] = []
        
        clean_text = passenger_string.replace("\n", ",").replace(" and ", ",")
        raw_segments = clean_text.split(",")
        
        added_count = 0
        current_set = {(p['name'].lower(), p['nationality'].lower()) for p in db["passengers"]}

        for segment in raw_segments:
            segment = segment.strip()
            if not segment: continue

            name, nat = "", ""
            if " from " in segment:
                parts = segment.split(" from ")
                name, nat = parts[0].strip(), parts[1].strip()
            elif "(" in segment and ")" in segment:
                name = segment.split("(")[0].strip()
                nat = segment.split("(")[1].replace(")", "").strip()
            elif " - " in segment:
                parts = segment.split(" - ")
                name, nat = parts[0].strip(), parts[1].strip()
            else:
                parts = segment.split(" ")
                if len(parts) >= 2:
                    nat = parts[-1]
                    name = " ".join(parts[:-1])

            if name and nat:
                if (name.lower(), nat.lower()) not in current_set:
                    db["passengers"].append({"name": name, "nationality": nat})
                    current_set.add((name.lower(), nat.lower()))
                    added_count += 1
        
        _save_db(tool_context, db)
        return f"SUCCESS: Added {added_count} passengers. SYSTEM COMMAND: Do not loop. IMMEDIATELY call 'save_flight_selection'."

    except Exception as e:
        return f"ERROR adding passengers: {str(e)}"

def get_passengers(tool_context: ToolContext) -> str:
    try:
        db = _load_db(tool_context)
        if not db.get("passengers"): return "No passengers found."
        return "\n".join([f"{i+1}. {p['name']} ({p['nationality']})" for i, p in enumerate(db["passengers"])])
    except:
        return "No passengers found."


def save_flight_selection(
    tool_context: ToolContext, 
    airline_info: str = "Unknown", 
    route: str = "Unknown", 
    scheduling: str = "Unknown", 
    passengers: str = "Unknown", 
    price: str = "0.00"
) -> str:
    print(f"DEBUG: Saving Flight: {airline_info} | {price}")
    
    try:
        db = _load_db(tool_context)
        if "flights" not in db: db["flights"] = []
        
        initial_count = len(db["flights"])

        db["flights"].append({
            "airline_info": airline_info,
            "route": route,
            "scheduling": scheduling,
            "passengers": passengers,
            "price": price
        })
        
        _save_db(tool_context, db)
        
        verify_db = _load_db(tool_context)
        new_count = len(verify_db["flights"])
        
        if new_count > initial_count:
            if new_count == 1:
                return "FLIGHT SAVED SUCCESSFULLY. SYSTEM COMMAND: This is the FIRST flight. Ask: 'Do you want to book a return flight?'"
            else:
                return f"FLIGHT SAVED (Count: {new_count}). SYSTEM COMMAND: Ask: 'Do you want to book any other flights?'"
        else:
            print("CRITICAL ERROR: Verification failed. DB count did not increase.")
            return "CRITICAL ERROR: Flight data was not written to disk. Please try saving again."

    except Exception as e:
        print(f"CRITICAL EXCEPTION in save_flight: {e}")
        traceback.print_exc()
        return f"CRITICAL ERROR saving flight: {str(e)}. Please retry."

def get_trip_summary(tool_context: ToolContext) -> str:
    try:
        db = _load_db(tool_context)
        
        if not db.get("flights"): 
            print("DEBUG: get_trip_summary found 0 flights in DB.")
            return "Here is your trip summary: No flights booked yet."

        summary = "**Your Flight Selection Summary**\n"
        summary += "========================================\n\n"
        grand_total = 0.0

        for i, flight in enumerate(db["flights"], 1):
            try:
                p_str = re.sub(r'[^\d.]', '', str(flight['price']))
                unit_price = float(p_str)
                if ',' in flight['passengers']:
                    p_list = flight['passengers'].split(',')
                else:
                    p_list = [flight['passengers']]
                
                pass_count = len(p_list)
                subtotal = unit_price * pass_count
                grand_total += subtotal
                formatted_subtotal = f"${subtotal:.2f}"
            except:
                pass_count = 1
                subtotal = 0
                formatted_subtotal = "Calc Error"
                p_list = [flight['passengers']]

         
            summary += f"**Flight {i}:** {flight['airline_info']} | {flight['route']}\n"
            
            sched = flight['scheduling'].replace('Dep', 'Departure:').replace('Arr', 'Arrival:')
            summary += f"🕒 {sched}\n"
            
            summary += f" **Subtotal:** {flight['price']} x {pass_count} passengers = **{formatted_subtotal}**\n"
            
            summary += " **Passengers:**\n"
            for p in p_list:
                summary += f"   • {p.strip()}\n"
            
            summary += "\n----------------------------------------\n\n"

        summary += f"**GRAND TOTAL:** ${grand_total:.2f}\n\n"
        summary += "If everything is correct, shall we proceed to booking? Type **'Proceed'**."
        
        return summary
    except Exception as e:
        return f"Error generating summary: {e}"