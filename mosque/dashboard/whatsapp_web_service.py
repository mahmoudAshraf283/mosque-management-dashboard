import requests
import json
from django.conf import settings

class WhatsAppWebService:
    """
    Service to send WhatsApp messages using whatsapp-web.js Node.js server
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'WHATSAPP_SERVICE_URL', 'http://localhost:3000')
    
    def is_ready(self):
        """Check if WhatsApp service is ready"""
        try:
            response = requests.get(f'{self.base_url}/status', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('ready', False)
            return False
        except Exception as e:
            print(f"Error checking WhatsApp service status: {e}")
            return False
    
    def send_message(self, phone_number, message):
        """
        Send WhatsApp message
        
        Args:
            phone_number: Phone number with country code (e.g., "966501234567")
            message: Message text to send
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Check if service is ready
            if not self.is_ready():
                return False, "WhatsApp service is not ready. Please make sure the service is running and authenticated."
            
            # Prepare request data
            data = {
                'phone_number': phone_number,
                'message': message
            }
            
            # Send POST request
            response = requests.post(
                f'{self.base_url}/send',
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result.get('message', 'Message sent successfully')
            else:
                error_data = response.json()
                return False, error_data.get('error', 'Unknown error')
                
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to WhatsApp service. Make sure the Node.js server is running."
        except requests.exceptions.Timeout:
            return False, "Request timeout. WhatsApp service took too long to respond."
        except Exception as e:
            return False, f"Error sending WhatsApp message: {str(e)}"
