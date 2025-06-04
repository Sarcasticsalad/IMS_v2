import requests
from django.conf import settings
from ..models import InstagramCredentials, AutoResponseRule, MessageLog
from ims.models import Product

class InstagramAutomationService:
    def __init__(self):
        self.credentials = InstagramCredentials.objects.first()
        self.rule_model = AutoResponseRule()
        self.message_log = MessageLog()
        self.base_url = 'https://graph.facebook.com/v18.0'

    @staticmethod
    def test_credentials(access_token, instagram_account_id):
        """Test if the provided credentials are valid"""
        url = f'https://graph.facebook.com/v18.0/{instagram_account_id}'
        params = {
            'access_token': access_token,
            'fields': 'id,username'
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception('Invalid credentials')
        return True

    def send_message(self, recipient_id, message_text):
        """Send a message to a specific Instagram user"""
        if not self.credentials:
            raise Exception('Instagram credentials not configured')

        url = f'{self.base_url}/me/messages'
        params = {'access_token': self.credentials.access_token}
        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text}
        }
        
        response = requests.post(url, params=params, json=data)
        if response.status_code != 200:
            raise Exception(f'Failed to send message: {response.text}')
        return response.json()

    def handle_incoming_message(self, sender_id, message_text):
        """Handle an incoming message and generate an automated response"""
        # Check if message contains product inquiry
        product_model = Product()
        products = product_model.all()
        
        # Simple product matching - can be improved with NLP
        matched_product = None
        for product in products:
            if product['name'].lower() in message_text.lower():
                matched_product = product
                break
        
        response_text = None
        rule_id = None
        
        if matched_product:
            # Get the appropriate rule based on stock level
            stock_level = self._determine_stock_level(matched_product)
            rule = self.rule_model.get_rule_for_product(str(matched_product['_id']))
            
            if rule and rule['stock_level'] == stock_level:
                response_text = rule['response_message']
                rule_id = str(rule['_id'])
            else:
                # Default response if no specific rule matches
                response_text = f"Thank you for asking about {matched_product['name']}. "
                if stock_level == 'out_of_stock':
                    response_text += "This item is currently out of stock."
                elif stock_level == 'low_stock':
                    response_text += f"This item is running low on stock (only {matched_product['quantity']} left)."
                else:
                    response_text += "This item is in stock and available for purchase!"
        else:
            response_text = "Thank you for your message! Please let me know which product you're interested in."
        
        # Send the response
        if response_text:
            try:
                self.send_message(sender_id, response_text)
            except Exception as e:
                print(f"Error sending message: {str(e)}")
                response_text = None
        
        # Log the interaction
        self.message_log.log_message(
            sender_id=sender_id,
            message_text=message_text,
            response_text=response_text,
            rule_id=rule_id
        )

    def _determine_stock_level(self, product):
        """Determine the stock level category for a product"""
        quantity = product.get('quantity', 0)
        if quantity <= 0:
            return 'out_of_stock'
        elif quantity <= product.get('low_stock_threshold', 10):
            return 'low_stock'
        return 'in_stock' 