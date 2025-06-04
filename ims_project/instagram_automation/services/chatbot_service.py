from typing import Dict, List, Tuple, Optional
import re
from ..models import Product, AutoResponseRule

class ChatbotService:
    def __init__(self):
        self.product_model = Product()
        self.rule_model = AutoResponseRule()
        self.greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        self.product_queries = ['price', 'cost', 'how much', 'available', 'in stock', 'stock']
        self.help_queries = ['help', 'support', 'assist', 'what can you do', 'how do you work']
        
    def process_message(self, message: str) -> Tuple[str, Optional[str]]:
        """
        Process incoming message and return appropriate response
        Returns: (response_message, rule_id if applicable)
        """
        message = message.lower().strip()
        
        # Check if it's a help request
        if any(query in message for query in self.help_queries):
            return self._handle_help_request(), None
        
        # Check if it's a greeting
        if self._is_greeting(message):
            return self._handle_greeting(), None
            
        # Check for product queries
        products = self._find_mentioned_products(message)
        if products:
            return self._handle_product_query(message, products[0])
            
        # If no specific query is detected
        return self._handle_general_query(message), None
    
    def _is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting"""
        return any(greeting in message for greeting in self.greetings)
    
    def _find_mentioned_products(self, message: str) -> List[Dict]:
        """Find any products mentioned in the message"""
        products = self.product_model.all()
        mentioned_products = []
        
        for product in products:
            # Check for product name mention
            if product['name'].lower() in message:
                mentioned_products.append(product)
                continue
                
            # Check for product code/SKU mention if available
            if 'sku' in product and product['sku'].lower() in message:
                mentioned_products.append(product)
                continue
            
            # Check for category if available
            if 'category' in product and product['category'].lower() in message:
                mentioned_products.append(product)
                continue
        
        return mentioned_products
    
    def _handle_greeting(self) -> str:
        """Handle greeting messages"""
        return ("Hello! 👋 Welcome to our store. How can I help you today?\n\n"
                "You can:\n"
                "• Ask about specific products\n"
                "• Check stock availability\n"
                "• Get pricing information\n"
                "• Ask for help at any time")
    
    def _handle_help_request(self) -> str:
        """Handle help requests"""
        return ("I'm your automated assistant! Here's what I can do:\n\n"
                "1. Product Information 📦\n"
                "   - Check prices\n"
                "   - Check stock availability\n"
                "   - Get product descriptions\n\n"
                "2. Stock Queries 📊\n"
                "   - Current stock levels\n"
                "   - Stock availability\n"
                "   - Low stock alerts\n\n"
                "Just mention a product name or ask about what you're looking for!")
    
    def _handle_product_query(self, message: str, product: Dict) -> Tuple[str, Optional[str]]:
        """Handle product-specific queries"""
        # Check stock level and get rule
        stock_level = self._get_stock_level(product)
        rule = self.rule_model.get_rule_for_product(product['_id'], stock_level)
        
        if rule:
            # If there's a specific rule, use it
            response = rule['response_message'].format(
                product_name=product['name'],
                stock_level=stock_level,
                price=product.get('price', 'Price on request')
            )
            return response, str(rule['_id'])
        
        # If no rule exists, generate a dynamic response
        response = self._generate_product_response(message, product, stock_level)
        return response, None
    
    def _handle_general_query(self, message: str) -> str:
        """Handle general queries"""
        if any(query in message for query in self.product_queries):
            return ("I can help you check product availability and prices. "
                   "Please let me know which product you're interested in.\n\n"
                   "You can ask about any product by name, or ask for help to see what else I can do!")
        
        return ("I'm here to help you with product information, availability, "
                "and pricing. Please let me know what you're looking for.\n\n"
                "Try asking about a specific product, or type 'help' to see what I can do!")
    
    def _get_stock_level(self, product: Dict) -> str:
        """Determine stock level for a product"""
        rules = self.rule_model.collection.find({'product_id': str(product['_id'])})
        low_stock_threshold = next(
            (rule['low_stock_threshold'] for rule in rules if 'low_stock_threshold' in rule),
            10
        )
        
        if product['quantity'] <= 0:
            return 'OUT_OF_STOCK'
        elif product['quantity'] <= low_stock_threshold:
            return 'LOW_STOCK'
        return 'IN_STOCK'
    
    def _generate_product_response(self, message: str, product: Dict, stock_level: str) -> str:
        """Generate a dynamic response based on the query and product details"""
        response_parts = []
        
        # Add product name and category if available
        header = f"About {product['name']}"
        if 'category' in product:
            header += f" ({product['category']})"
        response_parts.append(header + ":")
        
        # Add price information if available
        if 'price' in product:
            response_parts.append(f"💰 Price: ${product['price']}")
        
        # Add stock information
        stock_messages = {
            'IN_STOCK': f"Currently in stock ({product['quantity']} available)",
            'LOW_STOCK': f" Limited stock available ({product['quantity']} remaining)",
            'OUT_OF_STOCK': "Currently out of stock"
        }
        response_parts.append(stock_messages[stock_level])
        
        # Add product description if available
        if 'description' in product and product['description']:
            response_parts.append(f"\nDescription: {product['description']}")
        
        # Add additional information if available
        if 'specifications' in product:
            response_parts.append("\n Specifications:")
            for key, value in product['specifications'].items():
                response_parts.append(f"• {key}: {value}")
        
        # Add a call to action based on stock level
        if stock_level == 'IN_STOCK':
            response_parts.append("\nReady to order? Let me know!")
        elif stock_level == 'LOW_STOCK':
            response_parts.append("\nHurry! Only a few items left in stock!")
        else:
            response_parts.append("\nWould you like to be notified when this item is back in stock?")
        
        return "\n".join(response_parts) 