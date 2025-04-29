import requests
from django.conf import settings
from .models import Product

class InstagramBot:
    def __init__(self):
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.page_id = settings.INSTAGRAM_PAGE_ID
        self.product_model = Product()

    def get_messages(self):
        url = f"https://graph.facebook.com/v20.0/{self.page_id}/conversations?fields=messages&access_token={self.access_token}"
        response = requests.get(url)
        return response.json()

    def send_message(self, recipient_id, message):
        url = f"https://graph.facebook.com/v20.0/{self.page_id}/messages?access_token={self.access_token}"
        payload = {
            'recipient': {'id': recipient_id},
            'message': {'text': message}
        }
        response = requests.post(url, json=payload)
        return response.json()

    def process_message(self, message_text, sender_id):
        products = self.product_model.search(message_text)
        if products:
            response = "Here are the products matching your query:\n"
            for product in products:
                response += f"- {product['name']}: ${product['price']} ({product['stock']} in stock)\n"
        else:
            response = "Sorry, no products found matching your query."
        self.send_message(sender_id, response)

    def run(self):
        messages = self.get_messages()
        for conversation in messages.get('data', []):
            for message in conversation.get('messages', {}).get('data', []):
                if message.get('from', {}).get('id') != self.page_id:
                    self.process_message(message.get('message', ''), message.get('from', {}).get('id'))