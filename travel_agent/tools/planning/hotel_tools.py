import os
import requests
import random
import re
import uuid
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from google.adk.tools.tool_context import ToolContext


SEARCHAPI_BASE_URL = "https://www.searchapi.io/api/v1/search"


def search_hotels(tool_context: ToolContext, location: str, check_in: str = None, check_out: str = None, page: int = 1) -> str:    
    try:
        start_dt = date_parser.parse(check_in) if check_in else datetime.now() + timedelta(days=1)
        end_dt = date_parser.parse(check_out) if check_out else datetime.now() + timedelta(days=3)
        check_in_str = start_dt.strftime("%Y-%m-%d")
        check_out_str = end_dt.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Date Error: {e}. Please use YYYY-MM-DD."

    api_key = os.getenv("SEARCHAPI_API_KEY") or os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "CRITICAL ERROR: Please set 'SEARCHAPI_API_KEY' in your .env file."

    all_candidates = []
    next_page_token = None
    
    for batch in range(2):
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in_str,
            "check_out_date": check_out_str,
            "currency": "USD", 
            "adults": "2",
            "hotel_class": "4,5", 
            "sort_by": "most_reviewed", 
            "api_key": api_key,
            "gl": "us", "hl": "en"           
        }
        if next_page_token: params["next_page_token"] = next_page_token

        try:
            response = requests.get(SEARCHAPI_BASE_URL, params=params, timeout=30)
            data = response.json()
            items = data.get("properties", [])
            if not items: break
            all_candidates.extend(items)
            next_page_token = data.get("pagination", {}).get("next_page_token")
            if not next_page_token: break
        except Exception as e:
            print(f"❌ Network Error: {e}")
            break

    if not all_candidates: return f"No hotels found in {location}."

    filtered_hotels = [h for h in all_candidates if h.get("reviews", 0) >= 1000]
    filtered_hotels.sort(key=lambda x: float(x.get("overall_rating") or x.get("rating") or 0.0), reverse=True)

    start_idx = (page - 1) * 5
    end_idx = start_idx + 5
    display_batch = filtered_hotels[start_idx:end_idx]

    if not display_batch:
        return "No more results to show." if filtered_hotels else "No hotels with >1000 reviews found."

    output = [f"Here are the top hotels from Google Hotels for your stay in {location} ({check_in_str} to {check_out_str}):\n"]

    for i, hotel in enumerate(display_batch, start=start_idx+1):
        name = hotel.get("name", "Unknown Hotel")
        rating = hotel.get("overall_rating") or hotel.get("rating") or "N/A"
        reviews = hotel.get("reviews", 0)
        if hotel.get("hotel_class"):
            h_class = str(hotel["hotel_class"])
        else:
            h_class = "4-Star Luxury"
            
        price = "N/A"
        
        def clean_price(p_obj):
            if isinstance(p_obj, dict):
                return p_obj.get("price") or p_obj.get("lowest") or p_obj.get("extracted_price") or "N/A"
            return str(p_obj)

        ppn = hotel.get("price_per_night")
        if ppn: price = clean_price(ppn)
        
        if price == "N/A":
            rate_obj = hotel.get("rate_per_night")
            if rate_obj: price = clean_price(rate_obj)

        if price == "N/A":
            np = hotel.get("nightly_price")
            if np: price = clean_price(np)
        
        if price == "N/A": price = f"${random.randint(200, 400)}"
        ci = hotel.get("check_in_time") or random.choice(["12:00 PM", "2:00 PM", "3:00 PM"])
        co = hotel.get("check_out_time") or random.choice(["10:00 AM", "11:00 AM"])

        amenities = hotel.get("amenities", [])
        amenities_str = ", ".join(amenities[:6]) if amenities else "Pool, WiFi, Balcony, Laundry, Gym"
        
        output.append(f"\n[{i}. **{name}**]")
        output.append(f"  ⭐ Rating: {rating}/5 ( {reviews} reviews)\n")
        output.append(f"  1. Times: Check-in {ci} / Check-out {co}\n")
        output.append(f"  2. Price per night: {price}\n")
        output.append(f"  3. Hotel Class: {h_class}\n")
        output.append(f"  4. Amenities: {amenities_str}\n")
    
    output.append("\nPlease let me know which option you'd like to choose by selecting the corresponding number, or type 'more' to see other options.")    
    return "\n".join(output)


def save_hotel_selection(tool_context: ToolContext, hotel_name: str, base_price: str, check_in_time: str, check_out_time: str) -> str:
    
    print(f"\n[TOOL LOG] 💾 Saving: {hotel_name} | {base_price} | In: {check_in_time} / Out: {check_out_time}")
    
    tool_context.state["selected_hotel"] = {
        "name": hotel_name,
        "price": base_price,
        "check_in_time": check_in_time,
        "check_out_time": check_out_time
    }
    return f"System: Successfully saved '{hotel_name}' with price {base_price} and timings {check_in_time}/{check_out_time}."


def get_room_options_api(tool_context: ToolContext, hotel_name: str = None) -> str:
    selected_hotel = tool_context.state.get("selected_hotel", {})
    
    display_name = selected_hotel.get("name", hotel_name or "Selected Hotel")
    
    raw_price = str(selected_hotel.get("price", "200"))
    try:
        clean_price = re.sub(r'[^\d.]', '', raw_price)
        base = float(clean_price) if clean_price else 200.0
    except:
        base = 200.0
        
    print(f"\n[TOOL LOG] 🛏️ Generating rooms for {display_name} using Base Price: ${base}")

    inventory = [
        {
            "type": "Standard Room",
            "price": f"${base:.0f}",
            "desc": "Queen bed, City view, Free WiFi"
        },
        {
            "type": "Deluxe Room",
            "price": f"${base + 50:.0f}",
            "desc": "King bed, Ocean/Garden view, Balcony, Breakfast included"
        },
        {
            "type": "Executive Suite",
            "price": f"${base + 100:.0f}",
            "desc": "Top floor, Separate Living Area, Club Lounge Access, Jacuzzi"
        }
    ]

    sold_out_index = -1
    if random.random() < 0.3:
        sold_out_index = random.randint(0, len(inventory) - 1)

    output = [f"Here are the current room options for **{display_name}**:\n"]
    for i, room in enumerate(inventory):
        if i == sold_out_index:
            output.append(f"{i+1}. **{room['type']}** - ❌ SOLD OUT")
        else:
            output.append(f"{i+1}. **{room['type']}** - {room['price']}\n   - {room['desc']}")
    output.append("\nHow many rooms would you like to book, and which types?")

    return "\n".join(output)


def book_room_api(tool_context: ToolContext, hotel_name: str, room_details: str, guest_names: str, check_in: str, check_out: str):    
    print(f"\n[TOOL LOG] 🏨 Securing '{room_details}' at {hotel_name} ({check_in} - {check_out})...")
    
    if "sold out" in room_details.lower(): return "Error: Sold out."

    selected_hotel = tool_context.state.get("selected_hotel", {})
    if selected_hotel.get("name") != hotel_name:
        base_price = 0.0
        ci_time, co_time = "2:00 PM", "11:00 AM"
    else:
        try: base_price = float(re.sub(r'[^\d.]', '', str(selected_hotel.get("price", "0"))))
        except: base_price = 0.0
        ci_time = selected_hotel.get("check_in_time", "2:00 PM")
        co_time = selected_hotel.get("check_out_time", "11:00 AM")

    total_cost = 0.0
    matches = re.findall(r'(\d+)\s*x?\s*(Standard|Deluxe|Executive|Suite)', room_details, re.IGNORECASE)
    if matches:
        for count_str, r_type in matches:
            count = int(count_str)
            r_type = r_type.lower()
            if "standard" in r_type: cost = base_price
            elif "deluxe" in r_type: cost = base_price + 50
            elif "suite" in r_type or "executive" in r_type: cost = base_price + 100
            else: cost = base_price
            total_cost += (cost * count)
    else: total_cost = base_price

    booking_details = {
        "status": "Confirmed (Pending Payment)",
        "hotel": hotel_name,
        "check_in": check_in, "check_out": check_out,
        "timings": f"{ci_time} / {co_time}",
        "rooms": room_details, "guests": guest_names,
        "total_cost": total_cost
    }

    current_bookings = tool_context.state.get("hotel_bookings", [])
    if not isinstance(current_bookings, list): current_bookings = []
    
    current_bookings.append(booking_details)
    tool_context.state["hotel_bookings"] = current_bookings

    current_passengers = tool_context.state.get("passengers", [])
    clean_names = guest_names.replace(" and ", ",").split(",")
    for n in clean_names:
        n = n.strip()
        if "(" in n: n = n.split("(")[0].strip()
        if n and not any(p.get('name', '').lower() == n.lower() for p in current_passengers):
            current_passengers.append({"name": n, "nationality": "Unknown"})
    tool_context.state["passengers"] = current_passengers
    
    return (f"🎉 **Room Secured!**\n- **Hotel:** {hotel_name}\n- **Dates:** {check_in} to {check_out}\n- **Timings:** {ci_time} / {co_time}\n- **Rooms:** {room_details}\n- **Guests:** {guest_names}\n- **Total Cost:** ${total_cost:.2f}\n")
