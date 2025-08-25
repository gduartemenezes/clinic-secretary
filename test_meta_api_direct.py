#!/usr/bin/env python3
"""
Direct test of Meta API to check if the 401 error is resolved.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MetaAPIDirectTester:
    """Direct tester for Meta API calls."""
    
    def __init__(self):
        """Initialize the Meta API tester."""
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("META_PHONE_NUMBER_ID")
        self.base_url = os.getenv("META_BASE_URL", "https://graph.facebook.com/v18.0")
        
        print("🔍 Direct Meta API Test")
        print("=" * 50)
        print(f"Access Token: {'✅ Set' if self.access_token else '❌ Not set'}")
        print(f"Phone Number ID: {'✅ Set' if self.phone_number_id else '❌ Not set'}")
        print(f"Base URL: {self.base_url}")
        print()
    
    def test_phone_number_info(self):
        """Test getting phone number info (basic API call)."""
        print("📱 Testing phone number info API call...")
        
        if not self.access_token or not self.phone_number_id:
            print("❌ Missing credentials")
            return False
        
        url = f"{self.base_url}/{self.phone_number_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"Making GET request to: {url}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Phone number info retrieved successfully!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Failed to get phone number info: {response.status_code}")
                print(f"Error Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_message_sending_direct(self):
        """Test sending a message directly via Meta API."""
        print("\n📤 Testing direct message sending via Meta API...")
        
        if not self.access_token or not self.phone_number_id:
            print("❌ Missing credentials")
            return False
        
        # Use a test phone number (replace with one in your allowed list)
        test_phone = "+1234567890"  # ⚠️ REPLACE WITH ALLOWED NUMBER
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_phone,
            "type": "text",
            "text": {"body": "Direct API test from Medical Secretary AI!"}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"Sending message to: {test_phone}")
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Message sent successfully via Meta API!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Message sending failed: {response.status_code}")
                print(f"Error Response: {response.text}")
                
                # Analyze the error
                if "401" in str(response.status_code):
                    print("\n🔴 401 ERROR DETECTED - Authentication still failing!")
                    print("   This means the access token issue is NOT resolved.")
                elif "131030" in response.text:
                    print("\n🟡 Phone number restriction - add to allowed list")
                    print("   This is expected in development mode.")
                else:
                    print("\n🔴 Unexpected error - check the response above")
                
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_whatsapp_tools_class(self):
        """Test the WhatsAppTools class directly."""
        print("\n🔧 Testing WhatsAppTools class...")
        
        try:
            # Import after clearing cache
            from src.tools.whatsapp_tools import WhatsAppTools
            
            whatsapp = WhatsAppTools()
            print(f"WhatsApp Tools initialized:")
            print(f"  - Access Token: {'✅ Set' if whatsapp.access_token else '❌ Not set'}")
            print(f"  - Phone Number ID: {'✅ Set' if whatsapp.phone_number_id else '❌ Not set'}")
            print(f"  - Base URL: {whatsapp.base_url}")
            
            # Test sending a message through the class
            test_phone = "+1234567890"  # ⚠️ REPLACE WITH ALLOWED NUMBER
            result = whatsapp.send_text_message(
                to_phone_number=test_phone,
                message_text="Test message from WhatsAppTools class"
            )
            
            print(f"\nWhatsAppTools.send_text_message result:")
            print(f"  Success: {result.get('success', False)}")
            if result.get('success'):
                print(f"  Message ID: {result.get('message_id', 'N/A')}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
            
            return result.get('success', False)
            
        except Exception as e:
            print(f"❌ Error testing WhatsAppTools class: {e}")
            return False
    
    def run_all_tests(self):
        """Run all direct API tests."""
        print("🚀 Starting Direct Meta API Tests\n")
        
        tests = [
            self.test_phone_number_info,
            self.test_message_sending_direct,
            self.test_whatsapp_tools_class
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the output above.")
        
        return passed == total


def main():
    """Main function."""
    tester = MetaAPIDirectTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 Meta API is working correctly!")
    else:
        print("\n🔧 There are still issues with the Meta API.")
    
    return success


if __name__ == "__main__":
    main()
