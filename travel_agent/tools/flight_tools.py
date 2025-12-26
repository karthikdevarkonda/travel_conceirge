import os
import sys
from datetime import datetime
import dateparser 
from amadeus import Client, ResponseError
from google.adk.tools.tool_context import ToolContext

try:
    amadeus = Client(
        client_id=os.getenv('AMADEUS_CLIENT_ID'),
        client_secret=os.getenv('AMADEUS_CLIENT_SECRET')
    )
except Exception:
    amadeus = None

def _format_time(iso_str):

    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
        return dt.strftime("%b %d, %I:%M %p")
    except ValueError:
        return iso_str
def _clean_date(date_str):
   
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        try:
            dt = dateparser.parse(date_str)
            if dt: return dt.strftime("%Y-%m-%d")
        except:
            pass 
            
        try:
            clean = date_str.lower().replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
            dt = datetime.strptime(clean, "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except:
            return date_str 
def search_flights_amadeus(tool_context: ToolContext, origin: str, destination: str, date: str) -> str:
   
    if not amadeus: return "Error: Amadeus credentials missing."

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=20,
            currencyCode='USD'
        )
        
        offers = response.data
        if not offers: return f"No flights found for {origin}->{destination} on {date}."

        results = []
        for i, offer in enumerate(offers, 1):
            price = offer['price']['total']
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            duration = itinerary['duration'][2:] 
            
            first = segments[0]
            dep_code = first['departure']['iataCode']
            dep_raw = first['departure']['at']
            dep_pretty = _format_time(dep_raw)
            carrier = first['carrierCode']
            flight_num = first['number']
            
            last = segments[-1]
            arr_code = last['arrival']['iataCode']
            arr_raw = last['arrival']['at']
            arr_pretty = _format_time(arr_raw)
            
            stops = len(segments) - 1
            stop_msg = f"{stops} Stop" if stops > 0 else "Direct"
                    
            flight_str = (
                f"[{i}] ✈️ {carrier}{flight_num} ({stop_msg})\n"
                f"    🕒 Dep: {dep_pretty} ({dep_code}) ➝ 🕒 Arr: {arr_pretty} ({arr_code}) | ⏳ {duration} |  Price: ${price}"
            )
            results.append(flight_str)

        return "\n\n".join(results)

    except ResponseError as error:
        return f"API Error: {error}"
    except Exception as e:
        return f"Error: {str(e)}"