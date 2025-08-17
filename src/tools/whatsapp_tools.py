"""
WhatsApp tools for sending messages via Meta API.
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class WhatsAppTools:
    """WhatsApp tools class for Meta API integration."""
    
    def __init__(self):
        """Initialize WhatsApp tools."""
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("META_PHONE_NUMBER_ID")
        self.business_account_id = os.getenv("META_BUSINESS_ACCOUNT_ID")
        self.verify_token = os.getenv("META_VERIFY_TOKEN")
        
        if not all([self.access_token, self.phone_number_id]):
            print("Warning: Missing required Meta API credentials")
        
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def send_text_message(
        self,
        to_phone_number: str,
        message_text: str
    ) -> Dict[str, Any]:
        """Send a text message via WhatsApp."""
        if not self.access_token or not self.phone_number_id:
            return {"error": "Missing Meta API credentials"}
        
        # Format phone number (remove + and add country code if needed)
        formatted_phone = self._format_phone_number(to_phone_number)
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "text",
            "text": {"body": message_text}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to send message: {str(e)}"
            }
    
    def send_template_message(
        self,
        to_phone_number: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send a template message via WhatsApp."""
        if not self.access_token or not self.phone_number_id:
            return {"error": "Missing Meta API credentials"}
        
        # Format phone number
        formatted_phone = self._format_phone_number(to_phone_number)
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        # Add components if provided
        if components:
            payload["template"]["components"] = components
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("messages", [{}])[0].get("id"),
                "response": result
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to send template message: {str(e)}"
            }
    
    def send_appointment_confirmation(
        self,
        to_phone_number: str,
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        doctor_name: str,
        appointment_type: str
    ) -> Dict[str, Any]:
        """Send appointment confirmation using template message."""
        # Create components for the template
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": patient_name},
                    {"type": "text", "text": appointment_date},
                    {"type": "text", "text": appointment_time},
                    {"type": "text", "text": doctor_name},
                    {"type": "text", "text": appointment_type}
                ]
            }
        ]
        
        return self.send_template_message(
            to_phone_number=to_phone_number,
            template_name="appointment_confirmation",
            components=components
        )
    
    def send_appointment_reminder(
        self,
        to_phone_number: str,
        patient_name: str,
        appointment_date: str,
        appointment_time: str,
        doctor_name: str
    ) -> Dict[str, Any]:
        """Send appointment reminder using template message."""
        components = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": patient_name},
                    {"type": "text", "text": appointment_date},
                    {"type": "text", "text": appointment_time},
                    {"type": "text", "text": doctor_name}
                ]
            }
        ]
        
        return self.send_template_message(
            to_phone_number=to_phone_number,
            template_name="appointment_reminder",
            components=components
        )
    
    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number for WhatsApp API."""
        # Remove common formatting characters
        cleaned = phone_number.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        # Ensure it starts with country code
        if not cleaned.startswith("1") and len(cleaned) == 10:
            cleaned = "1" + cleaned  # Add US country code for 10-digit numbers
        
        return cleaned
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook for Meta API."""
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def extract_message_from_webhook(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract user message from webhook payload."""
        try:
            if webhook_data.get("object") != "whatsapp_business_account":
                return None
            
            entry = webhook_data.get("entry", [])
            if not entry:
                return None
            
            for entry_item in entry:
                changes = entry_item.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    for message in messages:
                        if message.get("type") == "text":
                            return {
                                "from": message.get("from"),
                                "message_id": message.get("id"),
                                "timestamp": message.get("timestamp"),
                                "text": message.get("text", {}).get("body", ""),
                                "type": "text"
                            }
            
            return None
            
        except Exception as e:
            print(f"Error extracting message from webhook: {e}")
            return None
