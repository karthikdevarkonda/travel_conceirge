import re
from typing import Any
from google.adk.tools.tool_context import ToolContext

def memorize_list(key: str, value: Any, tool_context: ToolContext):
    mem_dict = tool_context.state
    if key not in mem_dict: mem_dict[key] = []
    if not isinstance(mem_dict[key], list): mem_dict[key] = [mem_dict[key]]
    if value not in mem_dict[key]: mem_dict[key].append(value)
    return {"status": f'Stored "{key}": "{value}"'}

def memorize(key: str, value: Any, tool_context: ToolContext):
    tool_context.state[key] = value
    return {"status": f'Stored "{key}": "{value}"'}

def forget(key: str, value: Any, tool_context: ToolContext):
    if key not in tool_context.state: return {"status": f'Key "{key}" not found.'}
    current = tool_context.state[key]
    if isinstance(current, list):
        if value in current:
            current.remove(value)
            return {"status": f'Removed "{value}" from "{key}"'}
    elif str(current) == str(value):
        del tool_context.state[key]
        return {"status": f'Cleared "{key}"'}
    return {"status": f'Value not found in "{key}"'}

def add_passengers_bulk(tool_context: ToolContext, passenger_string: str) -> str:
    print(f"DEBUG: Adding passengers: {passenger_string}")
    try:
        clean_text = passenger_string.replace("\n", ",").replace(" and ", ",")
        raw_segments = clean_text.split(",")
        current_passengers = tool_context.state.get("passengers", [])
        existing_set = {(p['name'].lower(), p['nationality'].lower()) for p in current_passengers}
        added_count = 0
        for segment in raw_segments:
            segment = segment.strip()
            if not segment: continue
            name, nat = "", ""
            if " from " in segment: parts = segment.split(" from "); name, nat = parts[0].strip(), parts[1].strip()
            elif "(" in segment and ")" in segment: name = segment.split("(")[0].strip(); nat = segment.split("(")[1].replace(")", "").strip()
            elif " - " in segment: parts = segment.split(" - "); name, nat = parts[0].strip(), parts[1].strip()
            else: parts = segment.split(" "); name = " ".join(parts[:-1]); nat = parts[-1] if len(parts) >= 2 else ""
            if name and nat:
                if (name.lower(), nat.lower()) not in existing_set:
                    current_passengers.append({"name": name, "nationality": nat})
                    existing_set.add((name.lower(), nat.lower()))
                    added_count += 1
        tool_context.state["passengers"] = current_passengers
        return f"SUCCESS: Added {added_count} passengers. SYSTEM COMMAND: Do not loop. IMMEDIATELY call 'save_flight_selection'."
    except Exception as e: return f"ERROR: {str(e)}"

def get_passengers(tool_context: ToolContext) -> str:
    passengers = tool_context.state.get("passengers", [])
    if not passengers: return "No passengers found."
    return "\n".join([f"{i+1}. {p['name']} ({p['nationality']})" for i, p in enumerate(passengers)])


def save_flight_selection(tool_context: ToolContext, airline_info: str = None, route: str = None, scheduling: str = None, passengers: str = None, price: str = None, seats: str = None, seat_cost: str = None) -> str:

    flights = tool_context.state.get("flights", [])
    
    if seats and flights and not airline_info:
        last_flight = flights[-1]
        
        last_flight['seats'] = seats 
        last_flight['seat_cost'] = seat_cost if seat_cost else "0"
        
        tool_context.state["flights"] = flights
        return f"System: Successfully added seats {seats} (Cost: {seat_cost}) to flight {last_flight.get('airline_info')}."

    if not airline_info:
        return "Error: Missing flight details."

    new_flight = {
        "airline_info": airline_info,
        "route": route,
        "scheduling": scheduling,
        "passengers": passengers,
        "price": price,
        "seats": seats if seats else None,
        "seat_cost": seat_cost if seat_cost else "0"
    }
    
    flights.append(new_flight)
    tool_context.state["flights"] = flights
    return f"FLIGHT SAVED: {airline_info} ({route}). Passengers: {passengers}."

def get_latest_flight(tool_context: ToolContext) -> str:
    flights = tool_context.state.get("flights", [])
    if not flights: return "No flights found"
    info = flights[-1].get('airline_info', 'Unknown')
    return info.split(' ')[0] if info else "Unknown"

def get_trip_summary(tool_context: ToolContext) -> str:
    try:
        flights = tool_context.state.get("flights", [])
        global_seats = tool_context.state.get("seat_bookings", [])
        
        if not flights: 
            return "System Notification: No flights selected."

        summary = ["\n-------------------------------------------"]
        summary.append("### ✈️ TRIP SUMMARY")
        grand_total = 0.0

        for i, flight in enumerate(flights):
            title = "Outbound Flight" if i == 0 else ("Return Flight" if i == 1 else f"Flight {i+1}")
            summary.append(f"\n**{title}:**")
            
            try:
                price_str = re.sub(r'[^\d.]', '', str(flight.get('price', '0')))
                unit_price = float(price_str) if price_str else 0.0
            except: unit_price = 0.0

            p_raw = str(flight.get('passengers', ''))
            numbered_matches = re.findall(r'\d+\.\s*([^\d,]+)', p_raw) 
            
            if numbered_matches:
                p_list = [m.strip() for m in numbered_matches]
            elif ',' in p_raw:
                p_list = [p.strip() for p in p_raw.split(',') if p.strip()]
            else:
                p_list = [p_raw] if p_raw else []

            pass_count = len(p_list) if p_list else 1
            flight_fare_total = unit_price * pass_count

            seats_data = flight.get('seats') or flight.get('selected_seats')
            
            if not seats_data and global_seats:
                flight_num = flight.get('airline_info', '').split(' ')[0]
                seats_data = [s for s in global_seats if flight_num in str(s.get('flight', ''))]

            seat_list = [] 
            seats_cost = 0.0
            
            if isinstance(seats_data, str):
                seat_list = [s.strip() for s in seats_data.split(',') if s.strip()]
                try:
                    c_str = re.sub(r'[^\d.]', '', str(flight.get('seat_cost', '0')))
                    seats_cost = float(c_str) if c_str else 0.0
                except: seats_cost = 0.0

            elif isinstance(seats_data, list):
                for s in seats_data:
                    if isinstance(s, dict):
                        seat_list.append(s.get('seat', '?'))
                        try: s_p = float(re.sub(r'[^\d.]', '', str(s.get('price', 0))))
                        except: s_p = 0.0
                        seats_cost += s_p
                    else:
                        seat_list.append(str(s))

            passenger_display = []
            for idx, p_name in enumerate(p_list):
                if idx < len(seat_list):
                    assigned_seat = seat_list[idx]
                    passenger_display.append(f"{idx+1}. {p_name} (**Seat: {assigned_seat}**)")
                else:
                    passenger_display.append(f"{idx+1}. {p_name}")

            display_str = "\n   " + "\n   ".join(passenger_display)

            segment_total = flight_fare_total + seats_cost
            grand_total += segment_total

            sched = flight.get('scheduling', '').replace("Departure::", "Dep:").replace("Arrival::", "Arr:")
            
            summary.append(f"* **Airline:** {flight.get('airline_info', 'Unknown')}")
            summary.append(f"* **Route:** {flight.get('route', 'Unknown')}")
            summary.append(f"* **Schedule:** {sched}")
            summary.append(f"* **Travelers & Seats:** {display_str}")
            summary.append(f"* **Cost Breakdown:**")
            summary.append(f"   - Fare: ${unit_price:.2f} x {pass_count} = ${flight_fare_total:.2f}")
            summary.append(f"   - Seat Fees: ${seats_cost:.2f}")
            summary.append(f"* **Subtotal:** ${segment_total:.2f}")

        summary.append(f"\n### 💰 GRAND TOTAL: ${grand_total:.2f}")
        summary.append("-------------------------------------------\n")
        
        return "\n".join(summary)

    except Exception as e:
        return f"System Error: {e}"

def get_stay_summary(tool_context: ToolContext) -> str:
    try:
        hotels = tool_context.state.get("hotel_bookings", [])
        
        if not hotels: 
            return "System Notification: No hotel bookings found."

        summary = ["\n-------------------------------------------"]
        summary.append("### 🏨 STAY SUMMARY")
        grand_total = 0.0

        for i, booking in enumerate(hotels):
            title = f"Hotel Stay {i+1}"
            summary.append(f"\n**{title}:**")
            
            segment_total = float(booking.get('total_cost', 0.0))
            grand_total += segment_total
            dates = f"{booking.get('check_in', 'N/A')} to {booking.get('check_out', 'N/A')}"
            timings = booking.get('timings', '2:00 PM / 11:00 AM')
            summary.append(f"* **Hotel:** {booking.get('hotel', 'Unknown')}")
            summary.append(f"* **Dates:** {dates}")
            summary.append(f"* **Timings:** {timings}")
            summary.append(f"* **Rooms:** {booking.get('rooms', 'Unknown')}")
            summary.append(f"* **Guests:** {booking.get('guests', 'Unknown')}")
            summary.append(f"* **Confirmation #:** {booking.get('confirmation_number', 'Pending')}")
            summary.append(f"* **Cost:** ${segment_total:.2f}")

        summary.append(f"\n### 💰 GRAND TOTAL: ${grand_total:.2f}")
        summary.append("-------------------------------------------\n")
        
        return "\n".join(summary)

    except Exception as e:
        return f"System Error in hotel summary: {e}"

def memorize_guests(guest_names: str, tool_context: ToolContext) -> str:
    tool_context.state["current_hotel_guests"] = guest_names    
    add_passengers_bulk(tool_context, guest_names)    
    return f"Guest list updated. Saved: {guest_names}"

def get_guest_list(tool_context: ToolContext) -> str:
    passengers = tool_context.state.get("passengers", [])
    if not passengers: return "No travelers currently on file."
    return "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(passengers)]) + "\n"