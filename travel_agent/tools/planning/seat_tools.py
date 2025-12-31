import random
import re
from google.adk.tools.tool_context import ToolContext

_SEAT_CACHE = {}
def get_seat_map_api(tool_context: ToolContext, flight_number: str, known_price: str = None) -> str:
    print(f"\n[TOOL LOG] 💺 Generating dynamic seat map for {flight_number}...")
    
    if flight_number in _SEAT_CACHE:
        return _SEAT_CACHE[flight_number]
    
    def parse_price(value):
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return float(value)
            s_val = str(value)
            clean_s = re.sub(r'[^\d.]', '', s_val)
            if not clean_s:
                return None
            return float(clean_s)
        except:
            return None

    flights = tool_context.state.get("flights", [])
    flight_price = None 
    
    for f in flights:
        if str(f.get("flight_number")) == flight_number:
            flight_price = parse_price(f.get("price"))
            if flight_price:
                break

    if flight_price is None:
        flight_price = parse_price(known_price)

    if flight_price is None:
        return f"Error: Could not determine the price for Flight {flight_number}. Please ask the user for the ticket price or save the flight details first."

    raw_half = flight_price / 2
    biz_middle_price = round(raw_half / 10) * 10
    
    flight_seed = sum(ord(c) for c in flight_number)
    random.seed(flight_seed)
    
    biz_rows = [2, 4, 9] 
    eco_rows = [11, 17, 20, 22, 31]
    
    random.seed(flight_seed) 

    cols = ['A', 'B', 'C', 'D', 'E', 'F']
    output_lines = [f"Seating Plan for Flight {flight_number}\n"]

    def build_row_string(row_num, is_business):
        row_items = []
        for col in cols:
            if is_business:
                if col in ['B', 'E']: 
                    final_price = biz_middle_price
                    sType = "(Middle)"
                else:
                    final_price = biz_middle_price + 20
                    sType = "(Window)" if col in ['A', 'F'] else "(Aisle)"
            else:
                if col in ['B', 'E']: 
                    final_price = 10
                    sType = "(Middle)"
                else: 
                    final_price = 20
                    sType = "(Window)" if col in ['A', 'F'] else "(Aisle)"
            
            is_available = random.random() < 0.6
            
            if is_available:
                item = f"{row_num}{col} {sType} ${final_price:.0f}"
            else:
                item = "X"
            
            row_items.append(item)

        left = f"{row_items[0]} | {row_items[1]} | {row_items[2]}"
        right = f"{row_items[3]} | {row_items[4]} | {row_items[5]}"
        
        return f"• {left} || {right}"

    output_lines.append("**Business Class**")
    for r in biz_rows:
        output_lines.append(build_row_string(r, is_business=True))

    output_lines.append("\n**Economy Class**")
    for r in eco_rows:
        output_lines.append(build_row_string(r, is_business=False))

    output_lines.append("\n(X = Occupied)")
    
    result = "\n".join(output_lines)
    _SEAT_CACHE[flight_number] = result
    return result

def reserve_seat_api(tool_context: ToolContext, flight_number: str, seat_number: str, passenger_name: str, price_string: str = "0") -> str:
    print(f"\n[TOOL LOG] 🔒 Attempting to reserve {seat_number} for {passenger_name}...")

    if flight_number not in _SEAT_CACHE:
        result = get_seat_map_api(tool_context, flight_number)
        
        if result.startswith("Error") or "Error" in result[:20]:
            return result
            
        _SEAT_CACHE[flight_number] = result

    seat_map_text = _SEAT_CACHE.get(flight_number, "")
    
    seat_pattern = r"\b" + re.escape(seat_number) + r"\b"
    
    if not re.search(seat_pattern, seat_map_text):
        return f"ERROR: Seat {seat_number} is unavailable, occupied (X), or does not exist. Please check the map and pick another."

    price_pattern = seat_pattern + r".*?\$(\d+)"
    match = re.search(price_pattern, seat_map_text)
    
    if match:
        real_price = float(match.group(1))
    else:
        clean_price = re.sub(r'[^\d.]', '', str(price_string))
        real_price = float(clean_price) if clean_price else 0.0

    seat_record = {
        "flight": flight_number,
        "seat": seat_number,
        "passenger": passenger_name,
        "price": real_price
    }
    
    if "seat_bookings" not in tool_context.state:
        tool_context.state["seat_bookings"] = []        
    tool_context.state["seat_bookings"].append(seat_record)    
    updated_map = re.sub(seat_pattern, " X ", seat_map_text, count=1)
    _SEAT_CACHE[flight_number] = updated_map
    
    conf_code = "SEAT-" + "".join(random.choices("0123456789", k=4))
    return f"SUCCESS: Seat {seat_number} confirmed for {passenger_name} at ${real_price:.0f}. (Ref: {conf_code})"
