from django.db import models
from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
from ims.models import MongoBase, Product
from datetime import datetime

class InstagramCredentials(models.Model):
    access_token = models.CharField(max_length=500)
    instagram_account_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Instagram Credentials'
        verbose_name_plural = 'Instagram Credentials'

    def __str__(self):
        return f"Instagram Account: {self.instagram_account_id}"

class AutoResponseRule:
    STOCK_LEVEL_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_NAME]
        self.collection = self.db['auto_response_rules']

    def all(self):
        rules = list(self.collection.find())
        # Convert _id to id for template compatibility
        for rule in rules:
            rule['id'] = str(rule['_id'])
        return rules

    def create_rule(self, product_id, stock_level, response_message, low_stock_threshold=10, is_active=True):
        rule = {
            'product_id': product_id,
            'stock_level': stock_level,
            'response_message': response_message,
            'low_stock_threshold': low_stock_threshold,
            'is_active': is_active
        }
        result = self.collection.insert_one(rule)
        return str(result.inserted_id)

    def read(self, rule_id):
        rule = self.collection.find_one({'_id': ObjectId(rule_id)})
        if rule:
            rule['id'] = str(rule['_id'])
        return rule

    def update_rule(self, rule_id, data):
        self.collection.update_one(
            {'_id': ObjectId(rule_id)},
            {'$set': data}
        )

    def delete(self, rule_id):
        self.collection.delete_one({'_id': ObjectId(rule_id)})

    def get_rule_for_product(self, product_id):
        rule = self.collection.find_one({'product_id': product_id, 'is_active': True})
        if rule:
            rule['id'] = str(rule['_id'])
        return rule

class MessageLog:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_NAME]
        self.collection = self.db['message_logs']

    def log_message(self, sender_id, message_text, response_text=None, rule_id=None):
        log = {
            'sender_id': sender_id,
            'message_text': message_text,
            'response_text': response_text,
            'rule_id': rule_id,
            'timestamp': datetime.now()
        }
        result = self.collection.insert_one(log)
        return str(result.inserted_id)

    def get_recent_logs(self, limit=50):
        logs = list(self.collection.find().sort('timestamp', -1).limit(limit))
        for log in logs:
            log['id'] = str(log['_id'])
        return logs

# Simple function to handle automated responses
def handle_instagram_message(message_text):
    # Add your custom logic here
    # For example, you could check for specific keywords and return appropriate responses
    message_lower = message_text.lower()
    
    if 'price' in message_lower:
        return "Please provide the product name or code, and I'll check the price for you."
    
    elif 'stock' in message_lower or 'available' in message_lower:
        return "Please provide the product name or code, and I'll check the availability for you."
    
    elif 'delivery' in message_lower or 'shipping' in message_lower:
        return "We offer delivery within 2-3 business days. Shipping costs depend on your location."
    
    elif 'contact' in message_lower:
        return "You can reach our customer services "
    
    else:
        return "Thank you for your message! How can I help you today? You can ask about prices, stock availability, or delivery information." 