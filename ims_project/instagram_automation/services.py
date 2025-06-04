from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.iguser import IGUser
from .models import InstagramCredentials, AutoResponseRule, MessageLog
from ims.models import Product
import requests

class InstagramAutomationService:
    def __init__(self):
        credentials = InstagramCredentials.objects.first()
        if credentials:
            FacebookAdsApi.init(access_token=credentials.access_token)
            self.access_token = credentials.access_token
            self.instagram_account_id = credentials.instagram_account_id
        else:
            raise ValueError("Instagram credentials not found")
        
        self.product_model = Product()
        self.rule_model = AutoResponseRule()
        self.log_model = MessageLog()

    @staticmethod
    def test_credentials(access_token, instagram_account_id):
        """Test if the provided credentials are valid."""
        try:
            # Initialize the API with the provided token
            FacebookAdsApi.init(access_token=access_token)
            
            # Try to get the Instagram account info
            page = Page(instagram_account_id)
            page.api_get(fields=['instagram_business_account'])
            
            return True
        except Exception as e:
            raise ValueError(f"Invalid credentials: {str(e)}")

    def get_stock_level(self, product):
        """Determine stock level based on quantity and threshold."""
        rules = self.rule_model.collection.find({'product_id': str(product['_id'])})
        low_stock_threshold = next((rule['low_stock_threshold'] for rule in rules if 'low_stock_threshold' in rule), 10)
        
        if product['quantity'] <= 0:
            return 'OUT_OF_STOCK'
        elif product['quantity'] <= low_stock_threshold:
            return 'LOW_STOCK'
        return 'IN_STOCK'

    def get_response_message(self, product):
        """Get appropriate response message based on stock level."""
        stock_level = self.get_stock_level(product)
        rule = self.rule_model.get_rule_for_product(product['_id'], stock_level)
        
        if rule:
            return rule['response_message'].format(
                product_name=product['name'],
                stock_level=stock_level
            ), rule['_id']
        return None, None

    def handle_incoming_message(self, sender_id, message_text):
        """Process incoming message and send automated response."""
        # Try to find product mention in message
        products = self.product_model.all()
        for product in products:
            if product['name'].lower() in message_text.lower():
                response, rule_id = self.get_response_message(product)
                if response:
                    self.send_message(sender_id, response)
                    # Log the interaction
                    self.log_model.log_message(
                        instagram_user_id=sender_id,
                        message_received=message_text,
                        response_sent=response,
                        rule_id=rule_id
                    )
                    return True
        return False

    def send_message(self, recipient_id, message):
        """Send message using Instagram Graph API."""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/messages"
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
                "access_token": self.access_token
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False 