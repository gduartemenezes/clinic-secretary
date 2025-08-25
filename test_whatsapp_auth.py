#!/usr/bin/env python3
"""
Test script for debugging WhatsApp authentication.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WhatsAppAuthTester:
    """Test class for WhatsApp authentication."""
    
    def __init__(self):
        """Initialize the WhatsApp auth tester."""
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("META_PHONE_NUMBER_ID")
        self.business_account_id = os.getenv("META_BUSINESS_ACCOUNT_ID")
        self.verify_token = os.getenv("META_VERIFY_TOKEN")
        self.api_base = os.getenv("META_API_BASE", "https://graph.facebook.com/v18.0")
        
        print("🔍 WhatsApp Authentication Test")
        print("=" * 50)
        print(f"Access Token: {'✅ Set' if self.access_token else '❌ Not set'}")
        print(f"Phone Number ID: {'✅ Set' if self.phone_number_id else '❌ Not set'}")
        print(f"Business Account ID: {'✅ Set' if self.business_account_id else '❌ Not set'}")
        print(f"Verify Token: {'✅ Set' if self.verify_token else '❌ Not set'}")
        print(f"API Base: {self.api_base}")
        print()
    
    def test_access_token_validity(self):
        """Test if the access token is valid."""
        print("🔐 Testing access token validity...")
        
        if not self.access_token:
            print("❌ No access token to test")
            return False
        
        # Test with a simple API call to get phone number info
        url = f"{self.api_base}/{self.phone_number_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Access token is valid!")
                print(f"Phone Number Info: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Access token validation failed: {response.status_code}")
                print(f"Error Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing access token: {e}")
            return False
    
    def test_message_sending(self):
        """Test sending a message (to a test number)."""
        print("\n📱 Testing message sending...")
        
        if not self.access_token or not self.phone_number_id:
            print("❌ Missing credentials for message test")
            return False
        
        # Use a test phone number (you can change this)
        # IMPORTANT: Replace with a real phone number that's in your allowed list
        # Format: +1234567890 (with country code, no spaces)
        test_phone = "+1234567890"  # ⚠️ REPLACE WITH YOUR REAL NUMBER
        
        print(f"⚠️  NOTE: Using test phone: {test_phone}")
        print("   If this fails, replace it with a real number in your allowed list")
        print("   You can add test numbers in Meta Developer Console → WhatsApp → Configuration")
        print()
        
        url = f"{self.api_base}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_phone,
            "type": "text",
            "text": {"body": "This is a test message from the Medical Secretary AI!"}
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"Sending test message to: {test_phone}")
            print(f"URL: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Message sent successfully!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Message sending failed: {response.status_code}")
                print(f"Error Response: {response.text}")
                
                # Provide helpful error guidance
                if "131030" in response.text:
                    print("\n🔧 This error means the phone number is not in your allowed list.")
                    print("   Solutions:")
                    print("   1. Add the phone number to your allowed list in Meta Console")
                    print("   2. Use a different phone number that's already allowed")
                    print("   3. Wait for production approval (if in development mode)")
                
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def test_api_version_compatibility(self):
        """Test different API versions to find the right one."""
        print("\n🔄 Testing API version compatibility...")
        
        if not self.access_token or not self.phone_number_id:
            print("❌ Missing credentials for version test")
            return False
        
        versions = ["v18.0", "v19.0", "v20.0", "v21.0", "v22.0"]
        
        for version in versions:
            print(f"\nTesting version: {version}")
            url = f"https://graph.facebook.com/{version}/{self.phone_number_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.get(url, headers=headers)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ Version {version} works!")
                    data = response.json()
                    print(f"  Phone Number: {data.get('verified_name', 'N/A')}")
                    print(f"  Display Name: {data.get('display_phone_number', 'N/A')}")
                    return version
                else:
                    print(f"  ❌ Version {version} failed: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Version {version} error: {e}")
        
        return None
    
    def run_all_tests(self):
        """Run all authentication tests."""
        print("🚀 Starting WhatsApp Authentication Tests\n")
        
        tests = [
            self.test_access_token_validity,
            self.test_api_version_compatibility,
            self.test_message_sending
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
            print("\n🔧 Common solutions:")
            print("1. Check if your access token is expired")
            print("2. Verify the API version compatibility")
            print("3. Ensure your phone number ID is correct")
            print("4. Check if your app has the right permissions")
        
        return passed == total


def main():
    """Main function."""
    tester = WhatsAppAuthTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 WhatsApp authentication is working correctly!")
    else:
        print("\n🔧 Please fix the authentication issues above.")
    
    return success


if __name__ == "__main__":
    main()
