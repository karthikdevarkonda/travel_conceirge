import random
import uuid
from google.adk.tools.tool_context import ToolContext

def get_room_options_api(hotel_name: str) -> str:
    print(f"\n[TOOL LOG] 🛏️ Checking room inventory for {hotel_name}...")
    base = random.randint(180, 250)    
    inventory = [
        {
            "type": "Standard Room",
            "price": f"${base}",
            "desc": "Queen bed, City view, Free WiFi"
        },
        {
            "type": "Deluxe Room",
            "price": f"${base + 100}",
            "desc": "King bed, Ocean/Garden view, Balcony, Breakfast included"
        },
        {
            "type": "Executive Suite",
            "price": f"${base * 2}",
            "desc": "Top floor, Separate Living Area, Club Lounge Access, Jacuzzi"
        }
    ]
    sold_out_index = -1  
    
    if random.random() < 0.3:
        sold_out_index = random.randint(0, len(inventory) - 1)    
    output = [f"Here are the current room options for **{hotel_name}**:\n"]
    
    for i, room in enumerate(inventory):
        if i == sold_out_index:
            output.append(f"{i+1}. **{room['type']}** - ❌ SOLD OUT")
        else:
            output.append(f"{i+1}. **{room['type']}** - {room['price']}\n   - {room['desc']}")
            
    return "\n".join(output)


def book_room_api(tool_context: ToolContext, hotel_name: str, room_details: str, guest_names: str):
    print(f"\n[TOOL LOG] 🏨 Booking '{room_details}' at {hotel_name} for {guest_names}...")    
    if "sold out" in room_details.lower():
        return "Error: One of the selected room types is currently sold out. Please modify your selection."

    conf_number = "HTL-" + "".join(random.choices("0123456789", k=8))
    
    booking_details = {
        "status": "Confirmed",
        "hotel": hotel_name,
        "rooms": room_details,
        "guests": guest_names,
        "confirmation_number": conf_number
    }
    
    if "hotel_bookings" not in tool_context.state:
        tool_context.state["hotel_bookings"] = []
    
    tool_context.state["hotel_bookings"].append(booking_details)
    
    return (f"🎉 **Booking Confirmed!**\n"
            f"- **Hotel:** {hotel_name}\n"
            f"- **Rooms:** {room_details}\n"
            f"- **Guests:** {guest_names}\n"
            f"- **Confirmation #:** {conf_number}\n"
            f"Enjoy your stay!")