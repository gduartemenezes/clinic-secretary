#!/usr/bin/env python3
"""
Test script for debugging Google Calendar authentication.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.google_calendar_tools import GoogleCalendarTools


class GoogleCalendarTester:
    """Test class for Google Calendar functionality."""
    
    def __init__(self):
        """Initialize the Google Calendar tester."""
        self.calendar_tools = None
    
    def test_environment_variables(self):
        """Test environment variable setup."""
        print("🔍 Testing environment variables...")
        
        env_vars = [
            "GOOGLE_SERVICE_ACCOUNT_JSON",
            "GOOGLE_SERVICE_ACCOUNT_FILE", 
            "GOOGLE_ACCESS_TOKEN",
            "GOOGLE_CREDENTIALS_FILE",
            "GOOGLE_CALENDAR_ID"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if var == "GOOGLE_SERVICE_ACCOUNT_JSON":
                    # Show first 100 characters of JSON
                    print(f"✅ {var}: Set (length: {len(value)})")
                    print(f"   Preview: {value[:100]}...")
                elif var == "GOOGLE_SERVICE_ACCOUNT_FILE":
                    # Check if file exists
                    if os.path.exists(value):
                        print(f"✅ {var}: Set to existing file: {value}")
                    else:
                        print(f"⚠️  {var}: Set to non-existent file: {value}")
                else:
                    print(f"✅ {var}: Set to: {value}")
            else:
                print(f"❌ {var}: Not set")
        
        print()
    
    def test_google_calendar_tools_initialization(self):
        """Test Google Calendar tools initialization."""
        print("🔐 Testing Google Calendar tools initialization...")
        
        try:
            self.calendar_tools = GoogleCalendarTools()
            
            if self.calendar_tools.service:
                print("✅ Google Calendar tools initialized successfully")
                return True
            else:
                print("❌ Google Calendar tools failed to initialize")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Google Calendar tools: {e}")
            return False
    
    def test_calendar_access(self):
        """Test basic calendar access."""
        if not self.calendar_tools or not self.calendar_tools.service:
            print("⚠️  Skipping calendar access test - tools not initialized")
            return False
        
        print("\n📅 Testing calendar access...")
        
        try:
            # Test listing events
            events = self.calendar_tools.list_events(max_results=5)
            print(f"✅ Successfully listed {len(events)} events from calendar")
            
            if events:
                print("📋 Sample events:")
                for i, event in enumerate(events[:3]):
                    print(f"   {i+1}. {event.get('summary', 'No Title')} - {event.get('start', 'No Date')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error accessing calendar: {e}")
            return False
    
    def test_json_parsing(self):
        """Test JSON parsing from environment variable."""
        print("\n🔍 Testing JSON parsing...")
        
        json_env = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not json_env:
            print("⚠️  GOOGLE_SERVICE_ACCOUNT_JSON not set, skipping JSON test")
            return True
        
        try:
            import json
            
            # Test basic parsing
            print(f"Testing JSON parsing of environment variable...")
            print(f"Raw value length: {len(json_env)}")
            print(f"Raw value preview: {json_env[:100]}...")
            
            # Clean the JSON string
            cleaned_json = json_env.strip().strip('"').strip("'")
            print(f"Cleaned JSON length: {len(cleaned_json)}")
            print(f"Cleaned JSON preview: {cleaned_json[:100]}...")
            
            # Parse the JSON
            parsed_json = json.loads(cleaned_json)
            print("✅ JSON parsed successfully!")
            
            # Check required fields
            required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
            missing_fields = []
            
            for field in required_fields:
                if field not in parsed_json:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️  Missing required fields: {', '.join(missing_fields)}")
            else:
                print("✅ All required fields present")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Error at line {e.lineno}, column {e.colno}")
            print(f"Problematic content around error:")
            
            # Show context around the error
            lines = json_env.split('\n')
            if e.lineno <= len(lines):
                start_line = max(0, e.lineno - 2)
                end_line = min(len(lines), e.lineno + 2)
                
                for i in range(start_line, end_line):
                    marker = ">>> " if i == e.lineno - 1 else "    "
                    print(f"{marker}{i+1:3d}: {lines[i]}")
            
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error testing JSON: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Google Calendar Debug Tests\n")
        
        tests = [
            self.test_environment_variables,
            self.test_json_parsing,
            self.test_google_calendar_tools_initialization,
            self.test_calendar_access
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
            print("1. Check your .env file format")
            print("2. Ensure JSON is properly escaped in environment variable")
            print("3. Verify file paths exist and are readable")
            print("4. Check Google API credentials are valid")
        
        return passed == total


def main():
    """Main function."""
    tester = GoogleCalendarTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
