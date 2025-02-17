from flask import Flask, request, jsonify, make_response
from pms_simulator import pms
import os
import secrets
import time
from dotenv import load_dotenv
from google.cloud import dialogflow
from flask_cors import CORS  # Import Flask-CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Dialogflow Setup (remains the same)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
project_id = os.getenv("PROJECT_ID")
session_client = dialogflow.SessionsClient()

# --- OTP System (Simplified) --- (remains the same)
otp_store = {}  # In-memory store for OTPs (replace with database in a real system)

def generate_otp(room_number):
    otp = secrets.token_hex(3)  # 6-character hex OTP
    otp_store[room_number] = {"otp": otp, "timestamp": time.time()}
    return otp

def verify_otp(room_number, user_otp):
    if room_number in otp_store:
        stored_otp_data = otp_store[room_number]
        stored_otp = stored_otp_data["otp"]
        timestamp = stored_otp_data["timestamp"]
        if time.time() - timestamp < 300:  # 5-minute expiry
            if user_otp == stored_otp:
                del otp_store[room_number]  # Remove OTP after successful verification
                return True
    return False

# --- Dialogflow Integration --- (remains the same)
def detect_intent_texts(text, session_id, language_code="en"):
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result

@app.route("/", methods=["POST"])
def webhook():
      req = request.get_json(silent=True, force=True)
      intent_name = req["queryResult"]["intent"]["displayName"]
      parameters = req["queryResult"]["parameters"]
      session_id = req["session"].split("/")[-1]

      if intent_name == "RoomService.Order":
          food_item = parameters.get("food_item")
          room_number = parameters.get("room_number") # Get room number from parameters
          print(food_item)
          if food_item and room_number: #Check if both parameters are present.
              if pms.place_order(room_number, food_item): #place the order
                  response_text = f"Your room service order for a {food_item} has been placed and will be delivered shortly."
              else:
                  response_text = "Sorry, we couldn't place the order."
          else:
              response_text = "Your room service order has been placed and will be delivered shortly. Please be patient."
      elif intent_name == "GetMenu":
          response_text = "The menu includes cheeseburger, pizza, and salad."
      elif intent_name == "Welcome":
          response_text = "Welcome! How may I assist you?"
      elif intent_name == "actions.intent.MAIN":
          response_text = "Welcome to the Hotel Concierge! How may I help you?"
      else:
          response_text = "I'm not sure how to handle that request yet."

      fulfillment_response = {"fulfillmentText": response_text}
      return make_response(jsonify(fulfillment_response))
# --- API Endpoints (for OTP and testing) ---

@app.route("/api/otp/generate", methods=["POST"])
def generate_otp_route():
    data = request.get_json()
    room_number = data.get("room_number")
     # Check if the room number is valid
    if not pms.room_exists(room_number):
        return jsonify({"error": "Invalid room number"}), 400

    if not room_number:
        return jsonify({"error": "Missing room_number"}), 400


    otp = generate_otp(room_number)
    # In a real system, you would send the OTP via SMS here.
    # For this prototype, we'll return it in the response (for testing).
    return jsonify({"otp": otp})

@app.route("/api/otp/verify", methods=["POST"])
def verify_otp_route():
    data = request.get_json()
    room_number = data.get("room_number")
    otp = data.get("otp")
    print(f"Verifying OTP: room_number={room_number}, otp={otp}")

    if not room_number or not otp:
        return jsonify({"error": "Missing room_number or otp"}), 400

    if verify_otp(room_number, otp):
        return jsonify({"message": "OTP verified successfully"})
    return jsonify({"error": "Invalid OTP"}), 401

@app.route("/menu", methods=["GET"])
def get_menu_route():
    # menu_items = pms.get_menu()  # Remove this line
    return jsonify(pms.menu)  # Access pms.menu directly

# --- Run the App ---

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))