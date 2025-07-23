from flask import Flask, request, jsonify
import requests
import re
from pymongo import MongoClient
import json
from flask import request

app = Flask(__name__)

# MongoDB setup (assuming a running MongoDB instance)
client = MongoClient('mongodb://localhost:27017/')
db = client['ims_db']  # Replace 'ims_db' with your actual database name

# Access MongoDB collections (models)
product_collection = db['product']



# This is your chosen verification token
VERIFY_TOKEN = 'my_secure_token'  # Set this in the Facebook Dashboard too


@app.route('/')
def hello_world():
    return "<p> Helloo world </p>"


@app.route('/privacy_policy')
def privacy_policy():
    with open("/privacy.html", "rb") as file:
        privacy_policy_html = file.read()
    return privacy_policy_html


@app.route("/webhook", methods = ["GET", "POST"])
def webhook():
    if request.method == "POST":
        try:
            print(json.dumps(request.get_json(), indent=4))
        except:
            pass
        return "<p> This is POST request, Helloo Webhook!</p>"
    
    if request.method == "GET":
        hub_mode = request.args.get("hub.mode")
        hub_challenge = request.args.get("hub.challange")
        hub_verify_token = request.args.get("hub.verify_token")

        if hub_challange:

            return hub_challenge
        else:
            return "<p> This is get requesr, HElLLlloo po </p>"




# # Helper function to query MongoDB for product stock
# def get_product_stock(product_name):
#     product = product_collection.find_one({'name': {'$regex': product_name, '$options': 'i'}})  # Case-insensitive search
#     if product:
#         return f"Stock available for {product_name}: {product['stock']} units."
#     else:
#         return f"Sorry, we couldn't find the product '{product_name}' in our inventory."




# @app.route('/webhook', methods=['GET', 'POST'])
# def instagram_webhook():
#     if request.method == 'GET':
#         # Instagram will send a GET request to verify the webhook
#         # Check the 'hub.verify_token' against your VERIFY_TOKEN
#         verify_token = request.args.get('hub.verify_token')
#         challenge = request.args.get('hub.challenge')
        
#         # If the token matches, return the challenge
#         if verify_token == VERIFY_TOKEN:
#             return challenge  # Respond with the challenge code to complete verification
#         else:
#             return 'Verification failed', 403  # Verification failed if tokens don't match

#     elif request.method == 'POST':
#         # Handle incoming messages from Instagram
#         data = request.json
#         print("Received data:", data)  # Log the entire incoming request for debugging

#         # Extract the message sent by the user
#         user_message = data.get('entry', [{}])[0].get('messaging', [{}])[0].get('message', {}).get('text', '')
#         sender_id = data.get('entry', [{}])[0].get('messaging', [{}])[0].get('sender', {}).get('id', '')

#         # Log the user message and sender info
#         print(f"Message from user: {user_message}")
#         print(f"Sender ID: {sender_id}")

#         return jsonify({"status": "success"}), 200  # Return a success status




# # Function to send a message back to the user on Instagram
# def send_instagram_response(user_id, message):
#     response_url = f"https://graph.facebook.com/v12.0/{PAGE_ID}/messages"
#     payload = {
#         'recipient': {'id': user_id},
#         'message': {'text': message},
#         'access_token': ACCESS_TOKEN
#     }
#     response = requests.post(response_url, data=payload)
#     print(f"Sent response: {response.text}")

# # Basic function to extract product name (you can improve this logic)
# def extract_product_name(message):
#     # Check for a match with the product names in MongoDB
#     products = list(product_collection.find())
#     for product in products:
#         if re.search(r'\b' + re.escape(product['name']) + r'\b', message, re.IGNORECASE):
#             return product['name']
#     return None

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)  # Run Flask app locally for testing
