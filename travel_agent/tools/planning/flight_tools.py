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

def _format_time_new(iso_str):
    
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S")
        
        # Helper for 'th', 'st', 'nd'
        day = dt.day
        suffix = 'th' if 11 <= day <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(day % 10, 'th')
        
        date_part = dt.strftime(f"%B %-d{suffix}, %Y") 
        time_part = dt.strftime("%I:%M %p")             
        
        return f"{date_part}, at {time_part} UTC"
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
        return date_str 

def search_flights_amadeus(tool_context: ToolContext, origin: str, destination: str, departure_date: str) -> str:
   
    if not amadeus: return "Error: Amadeus credentials missing."

    # Clean date input just in case
    clean_date = _clean_date(departure_date)

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=clean_date,
            adults=1,
            max=20,
            currencyCode='USD'
        )
        
        carrier_map = {}
        if hasattr(response, 'result') and 'dictionaries' in response.result:
            carrier_map = response.result['dictionaries'].get('carriers', {})
        elif hasattr(response, 'body'): 
             import json
             try:
                 body_json = json.loads(response.body)
                 carrier_map = body_json.get('dictionaries', {}).get('carriers', {})
             except:
                 pass

        offers = response.data
        if not offers: return f"No flights found for {origin}->{destination} on {clean_date}."

        results = []
        for i, offer in enumerate(offers, 1):
            price = offer['price']['total']
            itinerary = offer['itineraries'][0]
            segments = itinerary['segments']
            
            first = segments[0]
            dep_code = first['departure']['iataCode']
            dep_pretty = _format_time_new(first['departure']['at'])
            carrier_code = first['carrierCode']
            flight_num = first['number']
            
            airline_name = carrier_map.get(carrier_code, carrier_code).title()
            
            last = segments[-1]
            arr_code = last['arrival']['iataCode']
            arr_pretty = _format_time_new(last['arrival']['at'])
            
            stops_count = len(segments) - 1
            stop_msg = f"{stops_count} Stop{'s' if stops_count > 1 else ''}" if stops_count > 0 else "Non-stop"
            
            flight_block = (
                f"**{i}. {airline_name} (Flight {carrier_code}{flight_num}):**\n"
                f"   * Departure: {dep_code} on {dep_pretty}\n"
                f"   * Arrival: {arr_code} on {arr_pretty}\n"
                f"   * Stops: {stop_msg}\n"
                f"   * Price: ${price}"
            )
            
            results.append(flight_block)

        return "\n\n".join(results)

    except ResponseError as error:
        return f"API Error: {error}"
    except Exception as e:
        return f"Error: {str(e)}"