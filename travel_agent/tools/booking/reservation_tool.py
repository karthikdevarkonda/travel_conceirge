import random
import string
import re
from google.adk.tools.tool_context import ToolContext

def get_booking_context(tool_context: ToolContext) -> str:
   
    flights = tool_context.state.get("flights", [])
    hotels = tool_context.state.get("hotel_bookings", [])
    
    if flights and 'pnr' not in flights[-1]:
        return "FLIGHT"
    
    if hotels:
        return "HOTEL"
        
    return "FLIGHT" 

def generate_flight_reservation(tool_context: ToolContext) -> str:
    flights = tool_context.state.get("flights", [])
    if not flights: return "No flights found to reserve."

    res_id = "RES-FLT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    tool_context.state["flight_reservation_id"] = res_id
    
    output = [f"### ✈️ FLIGHT RESERVATION CONFIRMED"]
    output.append(f"**Flight Reservation ID:** {res_id}\n")
    
    updated_flights = []
    total_cost = 0.0
    
    for flight in flights:
        if 'pnr' not in flight:
            flight['pnr'] = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        try:
            price = float(re.sub(r'[^\d.]', '', str(flight['price'])))
            p_str = str(flight.get('passengers', ''))
            p_count = len(p_str.split(',')) if ',' in p_str else 1
            total_cost += price * p_count
        except:
            pass
            
        updated_flights.append(flight)
        output.append(f"- **{flight.get('airline_info', 'Flight')}**: PNR {flight['pnr']}")

    tool_context.state["flights"] = updated_flights
    output.append(f"\n**Total Flight Cost:** ${total_cost:.2f}")
    
    return "\n".join(output)

def generate_hotel_reservation(tool_context: ToolContext) -> str:
    """Generates Reservation ID specifically for HOTELS."""
    hotels = tool_context.state.get("hotel_bookings", [])
    if not hotels: return "No hotel bookings found."

    res_id = "RES-HTL-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    tool_context.state["hotel_reservation_id"] = res_id
    
    output = [f"### 🏨 HOTEL RESERVATION CONFIRMED"]
    output.append(f"**Master Reservation ID:** {res_id}\n")
    
    total_cost = 0.0
    updated_hotels = []
    
    for h in hotels:
        if 'confirmation_number' not in h:
            h['confirmation_number'] = "CNF-" + "".join(random.choices(string.digits, k=8))
        
        try:
            raw_cost = str(h.get('total_cost', 0))
            cost = float(re.sub(r'[^\d.]', '', raw_cost))
            total_cost += cost
        except:
            pass
        
        output.append(f"- **{h.get('hotel')}**")
        output.append(f"  Selection: {h.get('rooms')}")
        output.append(f"  Ref: {h.get('confirmation_number')}\n")
        
        updated_hotels.append(h)

    tool_context.state["hotel_bookings"] = updated_hotels

    output.append(f"**Total Hotel Cost:** ${total_cost:.2f}")
    return "\n".join(output)