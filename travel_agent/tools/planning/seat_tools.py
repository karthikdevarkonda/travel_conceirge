import random
import re
from google.adk.tools.tool_context import ToolContext

_SEAT_CACHE = {}

def get_seat_map_api(tool_context: ToolContext, flight_number: str) -> str:
    print(f"\n[TOOL LOG] 💺 Generating dynamic seat map for {flight_number}...")
    
    if flight_number in _SEAT_CACHE:
        return _SEAT_CACHE[flight_number]
    
    flight_seed = sum(ord(c) for c in flight_number)
    random.seed(flight_seed)
    
    base_biz = 200 + (flight_seed % 150) 
    base_eco = 50 + (flight_seed % 80)   
    
    random.seed() 

    biz_rows = sorted(random.sample(range(1, 10), 3))
    eco_rows = sorted(random.sample(range(10, 41), 5))

    cols = ['A', 'B', 'C', 'D', 'E', 'F']
    output_lines = [f"**Seating Plan for Flight {flight_number}**\n"]

    def build_row_string(row_num, base_price):
        row_items = []
        
        for col in cols:
            if col in ['A', 'F']: 
                mod = 30
                sType = "Window"
            elif col in ['C', 'D']: 
                mod = 20
                sType = "Aisle"
            else: 
                mod = 0
                sType = "Middle"
            
            raw_price = base_price + mod
            final_price = round(raw_price / 10) * 10            
            is_available = random.random() < 0.6
            
            if is_available:
                item = f"**{row_num}{col}** ({sType}) ${final_price}"
            else:
                item = " X "
            
            row_items.append(item)

        left = " | ".join(row_items[:3])
        right = " | ".join(row_items[3:])
        
        return f"- {left} || {right}"

    output_lines.append("**Business Class**")
    for r in biz_rows:
        output_lines.append(build_row_string(r, base_biz))

    output_lines.append("\n**Economy Class**")
    for r in eco_rows:
        output_lines.append(build_row_string(r, base_eco))

    output_lines.append("\n*(X = Occupied)*")
    
    result = "\n".join(output_lines)
    
    _SEAT_CACHE[flight_number] = result
    return result

def reserve_seat_api(tool_context: ToolContext, flight_number: str, seat_number: str, passenger_name: str, price_string: str = "0") -> str:

    try:
        price_val = float(re.sub(r'[^\d.]', '', str(price_string)))
        if price_val == 0: price_val = 100.0 
    except:
        price_val = 100.0

    seat_record = {
        "flight": flight_number,
        "seat": seat_number,
        "passenger": passenger_name,
        "price": price_val
    }
    
    if "seat_bookings" not in tool_context.state:
        tool_context.state["seat_bookings"] = []
        
    tool_context.state["seat_bookings"].append(seat_record)
    
    conf_code = "SEAT-" + "".join(random.choices("0123456789", k=4))
    return f"SUCCESS: Seat {seat_number} confirmed for {passenger_name} (${price_val}). (Ref: {conf_code})"