# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import requests
import re
from rasa_sdk import  ActionExecutionRejection
from rasa_sdk.events import SlotSet
from config.config import API_URL
from config.config import DB_CONFIG
import mysql.connector
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker,FormValidationAction
from config.queries import GET_CLAIM_STATUS_QUERY,GET_POLICY_DETAILS_QUERY
from typing import Any, Dict, List,Text
from rasa_sdk.events import UserUtteranceReverted

# to set the slot created as policy so that bot understands that story for policy details needs to be executed
class ActionSetPolicyGoal(Action):
    def name(self):
        return "action_set_policy_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "policy")]

# to set the slot created as fund so that bot understands that story for fund details needs to be executed
class ActionSetFundGoal(Action):
    def name(self):
        return "action_set_fund_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "fund")]

# to set the slot created as topup so that bot understands that story for topup needs to be executed
class ActionSetFundGoal(Action):
    def name(self):
        return "action_set_topup_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "topup")]

# to set the slot created as topup so that bot understands that story for topup needs to be executed
class ActionSetStatementGoal(Action):
    def name(self):
        return "action_set_statement_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "statement")]

# to set the slot created as paypremium so that bot understands that story for paypremium needs to be executed
class ActionSetPayPremiumGoal(Action):
    def name(self):
        return "action_set_paypremium_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "paypremium")]

# to set the slot created as paypremium so that bot understands that story for paypremium needs to be executed
class ActionSetProfileDetailsGoal(Action):
    def name(self):
        return "action_set_profiledetails_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "profiledetails")]

# to set the slot created as standinginstruction so that bot understands that story for paypremium needs to be executed
class ActionSetStandingInstructionGoal(Action):
    def name(self):
        return "action_set_standinginstruction_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "standinginstruction")]

# to set the slot created as callback so that bot understands that story for paypremium needs to be executed
class ActionSetCallbackGoal(Action):
    def name(self):
        return "action_set_callback_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "callback")]

# to set the slot created as panupdate so that bot understands that story for paypremium needs to be executed
class ActionSetPanUpdateGoal(Action):
    def name(self):
        return "action_set_panupdate_goal"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("user_goal", "panupdate")]

# to process the user request slot and fetch the "policy details" or "fund details"
class ActionProcessUserRequest(Action):
    def name(self) -> Text:
        return "action_process_user_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("action_process_user_request")
        user_goal = tracker.get_slot("user_goal")
        print("user_goal",user_goal)
        mobile = tracker.get_slot("mobile_number")
        dob_str = tracker.get_slot("dob")

        if not mobile or not dob_str:
            dispatcher.utter_message("Mobile number or DOB required.")
            return []

        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            cursor.execute(GET_POLICY_DETAILS_QUERY, (mobile, dob_str))
            result = cursor.fetchone()

            if result:
                policy_number, name = result
                url = f"{API_URL}/api/policy/policySearch/{policy_number}"
                api_response = requests.get(url)

                if api_response.status_code == 200:
                    data = api_response.json()
                    policy = data.get("FinalElement", {}).get("ContractDetails", [{}])[0]

                    if user_goal == "policy":
                        msg = (
                            f"One moment... I’m fetching your details ⏳\n"
                            f"Hi {name}, here are the details for your policy number {policy.get('policyNumber')}-plan issued on {policy.get('PolicyIssueDate', '')[:10]}\n"
                            f"The life assured is {name}.You are covered for ₹{policy.get('SumAssured', 0):,}. Total Premium Paid: ₹{policy.get('TotalPremPaid', 0):,}.Premium Frequency: {'Single' if policy.get('PremFreq') == '00' else 'Annual'}\n"
                            f"Status: {policy.get('CurrentStatus')}\n"
                            f"Paid To: {policy.get('PaidToDate', '')[:10]}\n"
                            f"Maturity Date: {policy.get('RiskCessDate', '')[:10]}\n"
                            f"Plan: {policy.get('ProductName')}"
                        )
                    elif user_goal == "fund":
                        fund_value = policy.get('FundValue', '')
                        income = data.get('FinalElement', {}).get('LifeAssured', {}).get('ClientDetails', [{}])[0].get('Income', '')
                        msg = (
                            f"Hi {name}. The fund value for your policy number {policy.get('policyNumber')} is {fund_value}.\n"
                            f"Income: {income}"
                        )
                    elif user_goal == "topup":
                        msg = (
                            f"Hi *{name}*, please select the policy number you want to Top Up for:\n"
                            f"*03942589*: https://s.ipru.co/ICICIP/uo0bqr4v - LifeTime Super Pension\n"
                            f"*03922143*: https://s.ipru.co/ICICIP/odawcuvi - ICICI Pru Signature - LP/RP/WL\n\n"
                            "To top-up please *tap* on the link corresponding to the policies."
                        )
                    elif user_goal == "statement":
                        msg = (
                            f"Hi *{name}*, click on this link to view or download statements for:\n"
                            f"{policy.get('policyNumber')} : link \n"
                           
                        )
                    elif user_goal == "paypremium":
                        msg = (
                            f"Hi *{name}*, please click on the policy to make payment:\n"
                            f"link"
                        )
                    
                    elif user_goal == "profiledetails":
                        client_details = data.get("FinalElement", {}).get("LifeAssured", {}).get("ClientDetails", [{}])[0]

                        address_parts = [client_details.get("Flat", ""), client_details.get("Road", ""), client_details.get("Area", ""), client_details.get("City", ""), client_details.get("State", ""), str(client_details.get("Pincode", ""))]
                        full_address = ', '.join(filter(None, address_parts))

                        mobile_no = client_details.get("MobileNo", "NA")
                        dob = client_details.get("DOB", "")[:10]
                        pan = client_details.get("pan", "NA") 

                        msg = (
                            f"Hi {name}., your details updated with us:\n"
                            f"Address : {full_address}\n"
                            f"Mobile No: {mobile_no}\n"
                            f"Email-id: [Not available in API response]\n"
                            f"Date of birth: {dob}\n"
                            f"PAN: {pan}"
                        )
                    elif user_goal == "standinginstruction":
                        msg = (
                            # f"Hi *{name} ., select the policy you want to set standing instruction for: {Buttons with different policy No.}\n"
                            f"Hi *{name} ., select the policy you want to set standing instruction for:\n"
                        )

                    elif user_goal == "callback":
                        msg = (
                            f"Call goes to customer *{name}*\n"
                        )
                    elif user_goal == "panupdate":
                        msg = (
                            f"Hi  *{name}*, click on this link to update your PAN : https//:s.ipru.co/skjkfrb (user clicks the link to update the details)\n"
                        )
                    else:
                        msg = "I couldn't determine the goal of your request."

                    dispatcher.utter_message(msg)
                else:
                    dispatcher.utter_message("Sorry, I couldn’t fetch the policy details from the server.")
            else:
                dispatcher.utter_message("Sorry, no matching policy was found for the given mobile and DOB.")

        except Exception as e:
            dispatcher.utter_message(f"Something went wrong while accessing policy data. Error: {e}")

        # to reset the slots created as none so that bot can reask the dob and mobile number    
        return [
            # so that user is not asked to enter mobile no and dob again and again
            # SlotSet("mobile_number", None),
            # SlotSet("dob", None),
            SlotSet("user_goal", None),
            SlotSet("statement_type", None),
            SlotSet("customer_type", None),
            SlotSet("payment_type", None)
        ]


class ActionCheckClaimStatus(Action):
    def name(self):
        return "action_check_claim_status"

    def run(self, dispatcher,tracker,domain):
        
        claim_number = tracker.get_slot("claim_number")
        if not claim_number:
            dispatcher.utter_message(text="I need your claim number to get the status.")
            return []

        try:
            # if connection with mysql is not made then exception will run

            # unpack the dictionary hence **
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()
            # for parametreized query, we need to pass tuple hence ,
            cursor.execute(GET_CLAIM_STATUS_QUERY, (claim_number,))
            result = cursor.fetchone()

            # if claim number exists if runs else else will run
            if result:
                claim_status = result[0]
                status = f"Your claim status for claim {claim_number} is: {claim_status}."
            else:
                status = f"The status of claim {claim_number} is unknown."

            dispatcher.utter_message(text=status)

        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while checking claim status: {str(e)}")

        finally:
            if cursor: cursor.close()
            if connection: connection.close()

        return []


def validate_mobile_number(slot_value: Any, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
    """Validate mobile number for any form."""
    if re.fullmatch(r"\d{10}", slot_value):
        return {"mobile_number": slot_value}
    else:
        dispatcher.utter_message(text="The mobile number must be exactly 10 digits. Please re-enter.")
        return {"mobile_number": None}

def validate_dob(slot_value: Any, dispatcher: CollectingDispatcher) -> Dict[Text, Any]:
    """Validate DOB in yyyy/mm/dd format for any form."""
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", slot_value):
        return {"dob": slot_value}
    else:
        dispatcher.utter_message(text="The date of birth must be in yyyy/mm/dd format. Please re-enter.")
        return {"dob": None}

class ValidateUserDetailsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_user_details_form"

    async def validate_mobile_number(self, slot_value, dispatcher, tracker, domain):
        return validate_mobile_number(slot_value, dispatcher)

    async def validate_dob(self, slot_value, dispatcher, tracker, domain):
        return validate_dob(slot_value, dispatcher)

class ValidateStatementsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_statements_form"

    async def validate_mobile_number(self, slot_value, dispatcher, tracker, domain):
        return validate_mobile_number(slot_value, dispatcher)

    async def validate_dob(self, slot_value, dispatcher, tracker, domain):
        return validate_dob(slot_value, dispatcher)

class ValidatePayPremiumForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_paypremium_form"

    async def validate_mobile_number(self, slot_value, dispatcher, tracker, domain):
        return validate_mobile_number(slot_value, dispatcher)

    async def validate_dob(self, slot_value, dispatcher, tracker, domain):
        return validate_dob(slot_value, dispatcher)

class ValidateCallbackForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_callback_form"

    async def validate_mobile_number(self, slot_value, dispatcher, tracker, domain):
        return validate_mobile_number(slot_value, dispatcher)

    async def validate_dob(self, slot_value, dispatcher, tracker, domain):
        return validate_dob(slot_value, dispatcher)

class CustomFallback(Action):
    def name(self):
        return "action_custom_fallback"

    def run(self, dispatcher, tracker, domain):
        confidence = tracker.latest_message.get("intent", {}).get("confidence", 0)
        print(confidence)
        if confidence < 0.4:
            dispatcher.utter_message(
                f"I'm not sure I understood \"{tracker.latest_message.get('text')}\". Can you please rephrase?"
            )
            return [UserUtteranceReverted()] # so the user can try again