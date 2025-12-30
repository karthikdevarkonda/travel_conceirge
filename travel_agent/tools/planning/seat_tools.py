import random
import re
from google.adk.tools.tool_context import ToolContext

_SEAT_CACHE = {}

def get_seat_map_api(tool_context: ToolContext, flight_number: str, known_price: str = None) -> str:
    print(f"\n[TOOL LOG] 💺 Generating dynamic seat map for {flight_number}...")
    
    if flight_number in _SEAT_CACHE:
        return _SEAT_CACHE[flight_number]
    
    # 1. TRY MEMORY FIRST
    flights = tool_context.state.get("flights", [])
    flight_price = None 
    
    for f in flights:
        if str(f.get("flight_number")) == flight_number:
            try:
                p_str = str(f.get("price", ""))
                clean_p = re.sub(r'[^\d.]', '', p_str)
                if clean_p:
                    flight_price = float(clean_p)
            except:
                pass

    if flight_price is None and known_price:
        print(f"[DEBUG] Flight not in memory. Using provided argument: {known_price}")
        try:
            clean_arg = re.sub(r'[^\d.]', '', str(known_price))
            if clean_arg:
                flight_price = float(clean_arg)
        except:
            pass

    if flight_price is None:
        return f"Error: Could not determine the price for Flight {flight_number}. Please provide the price or save the flight first."

    print(f"[DEBUG] Using Base Flight Price: ${flight_price}")

    raw_half = flight_price / 2
    biz_middle_price = round(raw_half / 10) * 10
    
    flight_seed = sum(ord(c) for c in flight_number)
    random.seed(flight_seed)
    
    biz_rows = sorted(random.sample(range(1, 10), 3))
    eco_rows = sorted(random.sample(range(10, 41), 5))
    
    random.seed(flight_seed) 

    cols = ['A', 'B', 'C', 'D', 'E', 'F']
    output_lines = [f"**Seating Plan for Flight {flight_number}** (Base Fare: ${flight_price:.0f})\n"]

    def build_row_string(row_num, is_business):
        row_items = []
        
        for col in cols:
            if is_business:
                if col in ['B', 'E']: 
                    final_price = biz_middle_price
                    sType = "Middle"
                else:
                    final_price = biz_middle_price + 20
                    sType = "Window" if col in ['A', 'F'] else "Aisle"
            else:
                if col in ['B', 'E']: 
                    final_price = 10
                    sType = "Middle"
                else: 
                    final_price = 20
                    sType = "Window" if col in ['A', 'F'] else "Aisle"
            
            is_available = random.random() < 0.6
            
            if is_available:
                item = f"**{row_num}{col}** ({sType}) ${final_price:.0f}"
            else:
                item = " X "
            
            row_items.append(item)

        left = " | ".join(row_items[:3])
        right = " | ".join(row_items[3:])
        
        return f"- {left} || {right}"

    output_lines.append("**Business Class**")
    for r in biz_rows:
        output_lines.append(build_row_string(r, is_business=True))

    output_lines.append("\n**Economy Class**")
    for r in eco_rows:
        output_lines.append(build_row_string(r, is_business=False))

    output_lines.append("\n*(X = Occupied)*")
    
    result = "\n".join(output_lines)
    _SEAT_CACHE[flight_number] = result
    return result

def reserve_seat_api(tool_context: ToolContext, flight_number: str, seat_number: str, passenger_name: str, price_string: str = "0") -> str:
    print(f"\n[TOOL LOG] 🔒 Attempting to reserve {seat_number} for {passenger_name}...")

    if flight_number not in _SEAT_CACHE:
        result = get_seat_map_api(tool_context, flight_number)
        if result.startswith("Error"):
            return result
        
    seat_map_text = _SEAT_CACHE.get(flight_number, "")
    
    target_token = f"**{seat_number}**"
    
    if target_token not in seat_map_text:
        return f"ERROR: Seat {seat_number} is unavailable or does not exist. Please check the map."

    price_pattern = re.escape(target_token) + r".*?\$(\d+)"
    match = re.search(price_pattern, seat_map_text)
    
    if match:
        real_price = float(match.group(1))
    else:
        return f"ERROR: Could not verify price for seat {seat_number} from the map."

    seat_record = {
        "flight": flight_number,
        "seat": seat_number,
        "passenger": passenger_name,
        "price": real_price
    }
    
    if "seat_bookings" not in tool_context.state:
        tool_context.state["seat_bookings"] = []
        
    tool_context.state["seat_bookings"].append(seat_record)
    
    _SEAT_CACHE[flight_number] = seat_map_text.replace(target_token, " X ")
    
    conf_code = "SEAT-" + "".join(random.choices("0123456789", k=4))
    return f"SUCCESS: Seat {seat_number} confirmed for {passenger_name} at ${real_price:.0f}. (Ref: {conf_code})"