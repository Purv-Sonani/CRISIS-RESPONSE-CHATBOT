import re
import requests
import random
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionProcessLocation(Action):
    def name(self) -> Text:
        return "action_process_location"

    def run(self, dispatcher, tracker, domain):
        text = tracker.latest_message.get("text", "").strip()
        print(f"DEBUG: Processing Location for text: '{text}'")

        headers = {
            "User-Agent": "CrisisBot_Test_Script/1.0",
            "Referer": "http://localhost"
        }

        try:
            # Check if input is GPS coordinates
            coord_match = re.match(r"(-?\d+\.\d+),\s*(-?\d+\.\d+)", text)
            
            if coord_match:
                print("DEBUG: Coordinates detected")
                lat, lng = coord_match.groups()
                url = "https://nominatim.openstreetmap.org/reverse"
                params = {"lat": lat, "lon": lng, "format": "json"}
            else:
                print("DEBUG: City name detected")
                url = "https://nominatim.openstreetmap.org/search"
                params = {"q": text, "format": "json", "limit": 1}

            # 2. Make the request with a timeout
            print(f"DEBUG: Sending request to {url}")
            res = requests.get(url, params=params, headers=headers, timeout=10)
            
            print(f"DEBUG: API Status Code: {res.status_code}")

            if res.status_code == 200:
                data = res.json()
                
                # Handle List vs Dict response
                if isinstance(data, list):
                    result = data[0] if data else None
                else:
                    result = data if "error" not in data else None

                if result:
                    address = result.get("display_name", text)
                    lat = float(result.get("lat", 0.0))
                    lng = float(result.get("lon", 0.0))
                    
                    print(f"DEBUG: Success! Found: {address}")
                    dispatcher.utter_message(
                        text=f"I have your location as: {address}. Is this correct?",
                        buttons=[
                            {"title": "Yes", "payload": "/confirm_location"},
                            {"title": "No", "payload": "/provide_location"},
                        ],
                    )
                    return [
                        SlotSet("location", address),
                        SlotSet("location_lat", lat),
                        SlotSet("location_lng", lng),
                    ]
                else:
                    print("DEBUG: API returned empty data or error.")
                    dispatcher.utter_message(text="I couldn't find that place. Please check the spelling.")
                    return []
            else:
                print(f"DEBUG: API Failed. Text: {res.text}")
                dispatcher.utter_message(text="Map service is unavailable. Please try again.")
                return []

        except Exception as e:
            print(f"DEBUG: CRITICAL ERROR: {e}") 
            dispatcher.utter_message(text="Technical error finding location.")
            return []


class ActionRouteAfterLocation(Action):
    def name(self) -> Text:
        return "action_route_after_location"

    def run(self, dispatcher, tracker, domain):
        disaster = tracker.get_slot("disaster_type")

        if disaster == "earthquake":
            dispatcher.utter_message(response="utter_ask_indoors")
        elif disaster == "fire":
            dispatcher.utter_message(response="utter_ask_fire_severity")
        elif disaster == "flood":
            dispatcher.utter_message(response="utter_ask_water_level")
        else:
            dispatcher.utter_message(text="Please describe what is happening.")

        return []


class ActionCalculateRisk(Action):
    def name(self) -> Text:
        return "action_calculate_risk"
    
    def run(self, dispatcher, tracker, domain):
        # 1. Get Context
        disaster = tracker.get_slot("disaster_type")
        injury = tracker.get_slot("injury_status")
        fire_sev = tracker.get_slot("fire_severity")
        water = tracker.get_slot("water_level")
        fire_control = tracker.get_slot("fire_under_control")
        can_evacuate = tracker.get_slot("can_evacuate")
        in_flood_zone = tracker.get_slot("in_flood_zone")
        
        latest_intent = tracker.latest_message.get("intent", {}).get("name")
        user_text = tracker.latest_message.get("text", "").lower()

        print(f"DEBUG: Intent={latest_intent}, Text={user_text}")

        # Define standard buttons for the end of generic flows
        safety_buttons = [
            {"title": "🏠 Find Shelter", "payload": "/find_shelter"},
            {"title": "👤 Talk to Operator", "payload": "/request_operator"}
        ]

        # ---------------------------------------------------------
        # EARTHQUAKE FLOW
        # ---------------------------------------------------------
        if latest_intent == "report_location_context":
            if "indoors" in user_text:
                dispatcher.utter_message(response="utter_advice_indoors")
            elif "outdoors" in user_text:
                dispatcher.utter_message(response="utter_advice_outdoors")
            elif "vehicle" in user_text:
                dispatcher.utter_message(response="utter_advice_vehicle")
            dispatcher.utter_message(response="utter_ask_injury")
            return []

        if latest_intent == "report_injury":
            # CASE 1: TRAPPED
            if injury == "trapped" or "trapped" in user_text:
                # Urgent: Immediate Operator
                dispatcher.utter_message(response="utter_earthquake_trapped") 
                return [SlotSet("escalation_required", True)]
            
            # CASE 2: INJURED
            elif injury == "injured" or "injured" in user_text:
                # Urgent: Advice + Operator
                dispatcher.utter_message(response="utter_earthquake_injured")
                return [SlotSet("escalation_required", True)]
            
            # CASE 3: SAFE
            else:
                if disaster == "earthquake":
                    dispatcher.utter_message(response="utter_ask_structural_damage")
                elif disaster == "fire":
                    dispatcher.utter_message(
                        text="Proceed to the nearest assembly point immediately. Do not return inside.",
                        buttons=safety_buttons
                    )
                else:
                    dispatcher.utter_message(
                        text="Please remain cautious and follow official orders.",
                        buttons=safety_buttons
                    )
                return []

        if latest_intent == "report_damage_status":
            if "yes" in user_text or "damage" in user_text:
                dispatcher.utter_message(text="Danger: Do not enter damaged buildings.")
                return [SlotSet("escalation_required", True)]
            else:
                dispatcher.utter_message(response="utter_ask_gas_leak")
            return []

        if latest_intent == "report_gas_status":
            if "yes" in user_text or "gas" in user_text:
                dispatcher.utter_message(text="Danger: Gas leak detected. Evacuate immediately.")
                return [SlotSet("escalation_required", True)]
            else:
                dispatcher.utter_message(response="utter_ask_needs")
            return []

        # ---------------------------------------------------------
        # FIRE FLOW
        # ---------------------------------------------------------
        if latest_intent == "report_fire_control":
            is_controlled = str(fire_control).lower() == "true" or "yes" in user_text
            if is_controlled:
                dispatcher.utter_message(response="utter_fire_monitor")
                return []
            else:
                dispatcher.utter_message(response="utter_fire_evacuate_now")
                dispatcher.utter_message(response="utter_ask_injury")
                return [SlotSet("escalation_required", True)]

        # ---------------------------------------------------------
        # FLOOD FLOW
        # ---------------------------------------------------------
        if latest_intent == "report_evacuation_ability":
            is_able = str(can_evacuate).lower() == "true" or "yes" in user_text
            if is_able:
                dispatcher.utter_message(response="utter_flood_shutdown_evacuate")
            else:
                dispatcher.utter_message(response="utter_flood_move_high")
                return [SlotSet("escalation_required", True)]
            return []

        if latest_intent == "report_flood_zone":
            is_zone = str(in_flood_zone).lower() == "true" or "yes" in user_text
            if is_zone:
                dispatcher.utter_message(response="utter_flood_prepare")
            else:
                dispatcher.utter_message(response="utter_flood_stay_informed")
            return []

        # ---------------------------------------------------------
        # INITIAL TRIGGER
        # ---------------------------------------------------------
        if disaster == "earthquake":
            pass 

        elif disaster == "flood":
            if water == "inside_home" or "inside" in user_text:
                dispatcher.utter_message(response="utter_ask_evacuate")
            else:
                dispatcher.utter_message(response="utter_ask_flood_zone")

        elif disaster == "fire":
            if fire_sev == "large" or "large" in user_text:
                dispatcher.utter_message(response="utter_fire_large")
                dispatcher.utter_message(response="utter_ask_injury")
                return [SlotSet("escalation_required", True)]
            else:
                dispatcher.utter_message(response="utter_fire_small")
                dispatcher.utter_message(response="utter_ask_fire_control")

        return []


class ActionEscalateToHuman(Action):
    def name(self) -> Text:
        return "action_escalate_to_human"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(
            text="Connecting to emergency operator...",
            json_message={"handoff": True}
        )
        return []


class ActionProvideShelters(Action):
    def name(self) -> Text:
        return "action_provide_shelters"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location = tracker.get_slot("location") or "Berlin"
        location_lower = location.lower()

        shelter_db = {
            "berlin": [
                {
                    "name": "Berliner Stadtmission",
                    "address": "Lehrter Str. 68, 10557 Berlin",
                    "distance": "1.2 km",
                    "maps_link": "https://www.google.com/maps/search/?api=1&query=Berliner+Stadtmission+Lehrter+Str+68"
                },
            ],
            "munich": [
                 {
                    "name": "Munich Stadtmission",
                    "address": "Lehrter Str. 68, 10557 Munich",
                    "distance": "1.2 km",
                    "maps_link": "https://www.google.com/maps/search/?api=1&query=Berliner+Stadtmission+Lehrter+Str+68"
                },
            ]
        }

        if "munich" in location_lower or "münchen" in location_lower:
            selected_shelters = shelter_db["munich"]
        elif "berlin" in location_lower:
            selected_shelters = shelter_db["berlin"]
        else:
            selected_shelters = shelter_db["berlin"]

        dispatcher.utter_message(
            text=f"I found {len(selected_shelters)} emergency shelters near {location}.",
            json_message={
                "show_shelters": True, 
                "shelters": selected_shelters
            },
            buttons=[
                {"title": "Talk to Operator", "payload": "/request_operator"}, 
                {"title": "End Chat", "payload": "/deny_emergency"} 
            ]
        )
        
        return []