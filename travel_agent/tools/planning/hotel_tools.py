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
 
    filtered_hotels = [h for h in all_candidates if h.get("reviews", 0) >= 400]
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
           
        def extract_price_string(p_obj):
            if not p_obj: return None
           
            if isinstance(p_obj, dict):
                return p_obj.get("price") or str(p_obj.get("extracted_price")) or None
           
            return str(p_obj)
 
        price = "N/A"
       
        raw_ppn = hotel.get("price_per_night")
        if raw_ppn:
            found = extract_price_string(raw_ppn)
            if found: price = found
           
        if price == "N/A":
            raw_rpn = hotel.get("rate_per_night")
            if raw_rpn:
                found = extract_price_string(raw_rpn)
                if found: price = found
 
        if price == "N/A":
            prices_list = hotel.get("prices", [])
            if prices_list and isinstance(prices_list, list):
                found = extract_price_string(prices_list[0])
                if found: price = found
 
        if price == "N/A":
            prices_list = hotel.get("prices", [])
            if prices_list and isinstance(prices_list, list):
                found = extract_price_string(prices_list[0])
                if found: price = found
 
        if price == "N/A":
            rand_price = random.randint(200, 400)
            price = f"${rand_price}"
 
        def clean_time(t_str):
            if not t_str: return "Check with Hotel"
            return t_str.replace('\u202f', ' ').strip()
 
        ci = clean_time(hotel.get("check_in_time")) or random.choice(["12:00 PM", "2:00 PM", "3:00 PM"])
        co = clean_time(hotel.get("check_out_time")) or random.choice(["10:00 AM", "11:00 AM"])
 
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
   
    raw_price = str(selected_hotel.get("price", ""))
    base = None
    try:
        clean_price = re.sub(r'[^\d.]', '', raw_price)
        if clean_price:
            base = float(clean_price)
    except:
        pass
 
    if base is None:
        return f"Error: Pricing information is unavailable for {display_name}. Please choose another hotel or check availability manually."
       
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
    tool_context.state["current_room_inventory"] = [
    {
        "type": r["type"],
        "price": r["price"],
        "price_val": float(re.sub(r"[^\d.]", "", r["price"]))
    }
    for r in inventory
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
 
def book_room_api(
    tool_context: ToolContext,
    hotel_name: str,
    room_details: str,
    guest_names: str,
    check_in: str,
    check_out: str
):
 
    print(f"\n[TOOL LOG] 🏨 Securing '{room_details}' at {hotel_name}...")
 
    try:
        d1 = datetime.strptime(check_in, "%Y-%m-%d")
        d2 = datetime.strptime(check_out, "%Y-%m-%d")
        nights = abs((d2 - d1).days)
        if nights == 0:
            nights = 1
    except ValueError:
        return "Error: Invalid date format. Please use YYYY-MM-DD."
 
    inventory = tool_context.state.get("current_room_inventory", [])
    print("[DEBUG] INVENTORY:", inventory)
 
    txt = room_details.lower().strip()
    txt = re.sub(r'\s+and\s+', ',', txt)
    segments = [s.strip() for s in txt.split(',') if s.strip()]
 
    total_trip_cost = 0.0
    breakdown_text = []
 
    ROOM_KEYWORDS = ["standard", "deluxe", "executive", "suite"]
 
    def normalize_tokens(text: str):
        tokens = re.findall(r"[a-zA-Z]+", text.lower())
        return {t for t in tokens if t not in {"room", "rooms"}}
 
 
    for segment in segments:
 
        count_match = re.search(r'(\d+)', segment)
        count = int(count_match.group(1)) if count_match else 1
 
        seg_tokens = normalize_tokens(segment)
 
        price = None
        matched_type = "Unknown Room"
 
        for item in inventory:
 
            inv_label = (
                item.get("type")
                or item.get("room_type")
                or ""
            )
 
            inv_tokens = normalize_tokens(inv_label)
 
            common = seg_tokens.intersection(inv_tokens)
 
            if any(k in inv_tokens for k in ROOM_KEYWORDS) and common:
                price = float(item["price_val"])
                matched_type = inv_label
                break
 
        if price is None:
            p_match = re.search(r'\$\s?(\d+)', segment)
            if p_match:
                price = float(p_match.group(1))
                matched_type = "Custom Room"
 
        if price is None:
            print(f"[DEBUG] Could not price segment: {segment}")
            continue
 
        segment_total = price * count * nights
        total_trip_cost += segment_total
        breakdown_text.append(f"{count}x {matched_type}")
 
    if total_trip_cost == 0:
        return (
            "Error: Could not match any rooms to inventory. "
            "Please specify 'Standard', 'Deluxe', or 'Suite'."
        )
 
    selected_hotel = tool_context.state.get("selected_hotel", {})
    if selected_hotel.get("name") != hotel_name:
        ci_time, co_time = "Check Hotel", "Check Hotel"
    else:
        ci_time = selected_hotel.get("check_in_time", "Check Hotel")
        co_time = selected_hotel.get("check_out_time", "Check Hotel")
 
    booking_details = {
        "status": "Confirmed (Pending Payment)",
        "hotel": hotel_name,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "timings": f"{ci_time} / {co_time}",
        "rooms": ", ".join(breakdown_text),
        "guests": guest_names,
        "total_cost": total_trip_cost
    }
 
    bookings = tool_context.state.get("hotel_bookings", [])
    if not isinstance(bookings, list):
        bookings = []
    bookings.append(booking_details)
    tool_context.state["hotel_bookings"] = bookings
 
    passengers = tool_context.state.get("passengers", [])
    clean = guest_names.replace("\n", ",").replace(" and ", ",")
    for n in clean.split(","):
        n = n.strip()
        if "(" in n:
            n = n.split("(")[0].strip()
        if n and not any(p.get("name", "").lower() == n.lower() for p in passengers):
            passengers.append({"name": n, "nationality": "Unknown"})
    tool_context.state["passengers"] = passengers
 
    return (
        f"🎉 **Room Secured!**\n"
        f"- **Hotel:** {hotel_name}\n"
        f"- **Dates:** {check_in} to {check_out} ({nights} Nights)\n"
        f"- **Rooms:** {', '.join(breakdown_text)}\n"
        f"- **Total Cost:** ${total_trip_cost:.2f}\n"
    )
 