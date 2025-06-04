from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.conf import settings
from .models import InstagramCredentials, AutoResponseRule
from .services.instagram_service import InstagramAutomationService
from ims.models import Product
import json
import requests

class InstagramSetupView(LoginRequiredMixin, View):
    template_name = 'instagram_automation/instagram_setup.html'

    def get(self, request):
        # Test Instagram connection
        access_token = settings.INSTAGRAM_ACCESS_TOKEN
        account_id = settings.INSTAGRAM_ACCOUNT_ID
        
        connection_status = self.test_instagram_connection(access_token, account_id)
        
        credentials = InstagramCredentials.objects.first()
        
        context = {
            'credentials': credentials,
            'has_credentials': credentials is not None,
            'connection_status': connection_status,
        }
        return render(request, self.template_name, context)

    def test_instagram_connection(self, access_token, account_id):
        try:
            # Test the Instagram Graph API connection
            url = f'https://graph.facebook.com/v18.0/{account_id}'
            params = {
                'access_token': access_token,
                'fields': 'id,username,profile_picture_url'
            }
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'username': data.get('username', 'Unknown'),
                    'profile_picture_url': data.get('profile_picture_url', ''),
                    'message': 'Successfully connected to Instagram!'
                }
            else:
                error_data = response.json()
                return {
                    'success': False,
                    'message': f"Error: {error_data.get('error', {}).get('message', 'Unknown error')}"
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }

    def post(self, request):
        access_token = request.POST.get('access_token')
        instagram_account_id = request.POST.get('instagram_account_id')
        
        if not access_token or not instagram_account_id:
            messages.error(request, 'Both Access Token and Instagram Account ID are required.')
            return redirect('instagram_automation:setup')

        try:
            # Test the credentials
            connection_status = self.test_instagram_connection(access_token, instagram_account_id)
            
            if not connection_status['success']:
                messages.error(request, f'Invalid credentials: {connection_status["message"]}')
                return redirect('instagram_automation:setup')
            
            # Save or update credentials
            credentials, created = InstagramCredentials.objects.get_or_create(
                pk=1,  # We'll always use ID 1 since we only need one set of credentials
                defaults={
                    'access_token': access_token,
                    'instagram_account_id': instagram_account_id
                }
            )
            if not created:
                credentials.access_token = access_token
                credentials.instagram_account_id = instagram_account_id
                credentials.save()
            
            messages.success(request, 'Instagram credentials saved successfully!')
            
        except Exception as e:
            messages.error(request, f'Error saving credentials: {str(e)}')
        
        return redirect('instagram_automation:setup')

class AutoResponseRuleListView(LoginRequiredMixin, TemplateView):
    template_name = 'instagram_automation/rule_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rule_model = AutoResponseRule()
        product_model = Product()
        
        # Get all rules and enrich with product data
        rules = rule_model.all()
        products = {str(p['_id']): p for p in product_model.all()}
        
        for rule in rules:
            product = products.get(rule['product_id'])
            if product:
                rule['product_name'] = product['name']
                rule['stock_level_display'] = dict(AutoResponseRule.STOCK_LEVEL_CHOICES).get(rule['stock_level'])
        
        context['rules'] = rules
        return context

class AutoResponseRuleCreateView(LoginRequiredMixin, View):
    template_name = 'instagram_automation/rule_form.html'

    def get(self, request):
        product_model = Product()
        context = {
            'products': product_model.all(),
            'stock_level_choices': AutoResponseRule.STOCK_LEVEL_CHOICES,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        rule_model = AutoResponseRule()
        try:
            rule_id = rule_model.create_rule(
                product_id=request.POST['product_id'],
                stock_level=request.POST['stock_level'],
                response_message=request.POST['response_message'],
                low_stock_threshold=int(request.POST['low_stock_threshold']),
                is_active=request.POST.get('is_active', 'off') == 'on'
            )
            messages.success(request, 'Auto-response rule created successfully.')
            return redirect('instagram_automation:rule_list')
        except Exception as e:
            messages.error(request, f'Error creating rule: {str(e)}')
            return redirect('instagram_automation:rule_create')

class AutoResponseRuleUpdateView(LoginRequiredMixin, View):
    template_name = 'instagram_automation/rule_form.html'

    def get(self, request, rule_id):
        rule_model = AutoResponseRule()
        product_model = Product()
        
        rule = rule_model.read(rule_id)
        if not rule:
            messages.error(request, 'Rule not found.')
            return redirect('instagram_automation:rule_list')
        
        context = {
            'rule': rule,
            'products': product_model.all(),
            'stock_level_choices': AutoResponseRule.STOCK_LEVEL_CHOICES,
        }
        return render(request, self.template_name, context)

    def post(self, request, rule_id):
        rule_model = AutoResponseRule()
        try:
            data = {
                'product_id': request.POST['product_id'],
                'stock_level': request.POST['stock_level'],
                'response_message': request.POST['response_message'],
                'low_stock_threshold': int(request.POST['low_stock_threshold']),
                'is_active': request.POST.get('is_active', 'off') == 'on'
            }
            rule_model.update_rule(rule_id, data)
            messages.success(request, 'Auto-response rule updated successfully.')
            return redirect('instagram_automation:rule_list')
        except Exception as e:
            messages.error(request, f'Error updating rule: {str(e)}')
            return redirect('instagram_automation:rule_update', rule_id=rule_id)

class AutoResponseRuleDeleteView(LoginRequiredMixin, View):
    def post(self, request, rule_id):
        rule_model = AutoResponseRule()
        try:
            rule_model.delete(rule_id)
            messages.success(request, 'Auto-response rule deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting rule: {str(e)}')
        return redirect('instagram_automation:rule_list')

@method_decorator(csrf_exempt, name='dispatch')
class InstagramWebhookView(View):
    def get(self, request, *args, **kwargs):
        """Handle the webhook verification from Instagram"""
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == settings.INSTAGRAM_VERIFY_TOKEN:
                return HttpResponse(challenge)
        return HttpResponse('Invalid verification token', status=403)

    def post(self, request, *args, **kwargs):
        """Handle incoming messages from Instagram"""
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            # Process the incoming message
            if 'entry' in data and len(data['entry']) > 0:
                entry = data['entry'][0]
                if 'messaging' in entry and len(entry['messaging']) > 0:
                    message_event = entry['messaging'][0]
                    sender_id = message_event['sender']['id']
                    message_text = message_event['message']['text']

                    # Handle the message using automation service
                    service = InstagramAutomationService()
                    service.handle_incoming_message(sender_id, message_text)

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class MessageLogListView(LoginRequiredMixin, TemplateView):
    template_name = 'instagram_automation/message_log_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = InstagramAutomationService()
        context['messages'] = service.message_log.get_recent_logs()
        return context 