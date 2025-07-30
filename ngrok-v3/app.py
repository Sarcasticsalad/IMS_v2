import json
from flask import Flask, request, send_file, jsonify
import threading
import requests
import re
from pymongo import MongoClient
import time
import uuid
from flask_cors import CORS
import os

temporary_messages_lock = threading.Lock()

# app = Flask(__name__)
TEMPLATE_DIR = os.path.abspath("../ims_project/instagram_automation/templates/instagram_automation/")
app = Flask(__name__, template_folder=TEMPLATE_DIR)

CORS(app)

app_id = "722208127015775"
app_secret = "8a9b4db86d3178a591300d918f729a12"
redirect_url = "https://1cbd-2400-1a00-4b4f-713-6dd4-424e-7b81-3189.ngrok-free.app/"
PAGE_ACCESS_TOKEN = "IGAAKQ2C7dW19BZAFBuOTV0SzNjeEFKcTFVSE5ySDNtd2xzQ00tdnNSVzZA2LURTaFZAxT2RfdGc1bEFJdnJWOHMyNXBfbHI0cnYtQzhHN24tNnUxUUp1SFcwazhsekJYdlhrZATYyMVhSVWdGRDhrWjYwanpDcUJncGN4a0NyaGQxRQZDZD"
VERIFY_TOKEN = "123456"


# MongoDB setup ()
client = MongoClient('mongodb://localhost:27017/')
db = client['ims_db']
product_collection = db['products']
# Temporary in-memory message list
temporary_messages = []



@app.route("/")
def hello_world():
    return "<p>Hello world</p>"

@app.route("/privacy")
def privacy():
    return send_file("privacy.html")  # Make sure this file is in same folder

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    elif request.method == "POST":
        data = request.get_json()
        print(json.dumps(data, indent=4))  # Log the entire incoming data

        try:
            for entry in data.get("entry", []):
                for event in entry.get("messaging", []):
                    sender_id = event["sender"]["id"]

                    if "message" in event:
                        message_text = event["message"].get("text", "")
                        print(f"Message from {sender_id}: {message_text}")

                        # Generate a unique conversation ID for this user message + bot reply pair
                        conversation_id = str(uuid.uuid4())

                        # Append message to temporary memory
                        with temporary_messages_lock:
                            # Save user message
                            temporary_messages.append({
                                "id": conversation_id,
                                "type": "user",
                                "timestamp": int(time.time()* 1000),
                                "sender_id": sender_id,
                                "message": message_text,
                                
                            })

                        product_name = extract_product_name(message_text)

                        if product_name:
                            reply = get_product_stock(product_name)
                        else:
                            reply = "Hello Thankyou for Inquiring ! " \
                            "Please provide a valid product name to check availability. Just Write the name of the product"

                        send_reply(sender_id, reply)

                        with temporary_messages_lock:
                            # Save bot reply linked to the same conversation ID
                            temporary_messages.append({
                                "id": conversation_id,
                                "type": "bot",
                                "timestamp": int(time.time() * 1000),
                                "sender_id": "bot",
                                "message": reply,
                            })

        except Exception as e:
            print("Error:", e)

        return "EVENT_RECEIVED", 200

@app.route("/get_messages", methods=["GET"])
def get_messages():
    with temporary_messages_lock:
        last_20 = sorted(temporary_messages, key=lambda x: x.get("timestamp", 0), reverse=True)[:20]
    # Return last 20 messages as JSON
    return jsonify(last_20)

def extract_product_name(message):
    """
    Simple product name matching based on MongoDB product names.
    """
    message = message.lower()
    products = product_collection.find()
    for product in products:
        name = product.get("name", "").strip().lower()
        if name in message:
            return product['name']
    return None

def get_product_stock(product_name):
    product = product_collection.find_one({'name': {'$regex': product_name, '$options': 'i'}})
    if not product:
        return f"❌ Sorry, the product '{product_name}' is not available in our inventory."

    try:
        stock = int(product.get("stock", 0))
    except (ValueError, TypeError):
        return f" '{product_name}' found, but stock value is invalid."
    if stock == 0:
        return f" '{product_name}' is currently out of stock."
    elif stock < 10:
        return f" '{product_name}' is in stock but running low: only {stock} units left."
    else:
        return f" '{product_name}' is available. Stock: {stock} units."



def send_reply(recipient_id, message_text):
    url = f"https://graph.instagram.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {
        
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Reply sent:", response.status_code, response.text)


if __name__ == '__main__':
    app.run(debug=True, port=8001)