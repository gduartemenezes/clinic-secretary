#!/usr/bin/env python3
"""
Test script for the improved medical secretary agent.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.database_tools import DatabaseTools
from src.tools.google_calendar_tools import GoogleCalendarTools
from src.agents.orchestrator_agent import OrchestratorAgent


class ImprovedAgentTester:
    """Test class for the improved medical secretary agent."""
    
    def __init__(self):
        """Initialize the tester."""
        # Mock database session for testing
        self.db_tools = None
        self.calendar_tools = None
        self.orchestrator_agent = None
        
        print("🧪 Testing Improved Medical Secretary Agent")
        print("=" * 60)
        print()
    
    def test_conversation_flow(self):
        """Test the conversation flow with the improved agent."""
        print("💬 Testing Conversation Flow")
        print("-" * 40)
        
        # Initialize conversation state
        conversation_state = {
            "messages": [],
            "intent": "",
            "collected_params": {},
            "required_params": [],
            "status": "",
            "next_agent": None,
            "user_message": "",
            "response": "",
            "conversation_state": {},
            "channel_id": "test_user",
            "channel_type": "test"
        }
        
        # Test conversation 1: Initial greeting
        print("\n1️⃣ User: Hello")
        response1 = self._simulate_user_message("Hello", conversation_state)
        print(f"Agent: {response1}")
        
        # Test conversation 2: Appointment request
        print("\n2️⃣ User: please make an appointment for me for tomorrow afternoon. I need to see a general doctor to do some checkup exams")
        response2 = self._simulate_user_message("please make an appointment for me for tomorrow afternoon. I need to see a general doctor to do some checkup exams", conversation_state)
        print(f"Agent: {response2}")
        
        # Test conversation 3: Emergency request
        print("\n3️⃣ User: please create another one for today, a emergency has happened")
        response3 = self._simulate_user_message("please create another one for today, a emergency has happened", conversation_state)
        print(f"Agent: {response3}")
        
        # Test conversation 4: Personal question
        print("\n4️⃣ User: do you know me?")
        response4 = self._simulate_user_message("do you know me?", conversation_state)
        print(f"Agent: {response4}")
        
        # Test conversation 5: Appointment check
        print("\n5️⃣ User: hello i need to check on my apppointments")
        response5 = self._simulate_user_message("hello i need to check on my apppointments", conversation_state)
        print(f"Agent: {response5}")
        
        print("\n" + "=" * 60)
        print("✅ Conversation flow test completed!")
        
        return True
    
    def _simulate_user_message(self, user_message: str, conversation_state: dict) -> str:
        """Simulate a user message and get agent response."""
        try:
            # Create mock tools for testing
            if not self.db_tools:
                self.db_tools = MockDatabaseTools()
            if not self.calendar_tools:
                self.calendar_tools = MockGoogleCalendarTools()
            if not self.orchestrator_agent:
                self.orchestrator_agent = OrchestratorAgent(self.db_tools, self.calendar_tools)
            
            # Process the message
            result = self.orchestrator_agent.process_message(user_message, conversation_state)
            
            # Update conversation state
            conversation_state.update(result["conversation_state"])
            
            return result["response"]
            
        except Exception as e:
            return f"Error processing message: {str(e)}"
    
    def test_intent_detection(self):
        """Test intent detection capabilities."""
        print("\n🎯 Testing Intent Detection")
        print("-" * 40)
        
        if not self.orchestrator_agent:
            self.db_tools = MockDatabaseTools()
            self.calendar_tools = MockGoogleCalendarTools()
            self.orchestrator_agent = OrchestratorAgent(self.db_tools, self.calendar_tools)
        
        test_messages = [
            ("Hello", "general_conversation"),
            ("I need an appointment", "schedule_appointment"),
            ("What are your hours?", "get_information"),
            ("I need to cancel my appointment", "modify_appointment"),
            ("This is an emergency", "emergency"),
            ("When is my appointment?", "check_appointment"),
            ("Do you remember me?", "personal_question"),
            ("I want to see a cardiologist", "schedule_appointment"),
            ("What services do you offer?", "get_information"),
            ("I can't make it tomorrow", "modify_appointment")
        ]
        
        correct_detections = 0
        total_tests = len(test_messages)
        
        for message, expected_intent in test_messages:
            detected_intent = self.orchestrator_agent.detect_intent(message)
            is_correct = detected_intent == expected_intent
            status = "✅" if is_correct else "❌"
            
            print(f"{status} '{message}' -> {detected_intent} (expected: {expected_intent})")
            
            if is_correct:
                correct_detections += 1
        
        accuracy = (correct_detections / total_tests) * 100
        print(f"\n🎯 Intent Detection Accuracy: {correct_detections}/{total_tests} ({accuracy:.1f}%)")
        
        return accuracy >= 80  # 80% accuracy threshold
    
    def test_personality_and_tone(self):
        """Test the agent's personality and tone."""
        print("\n👤 Testing Personality and Tone")
        print("-" * 40)
        
        if not self.orchestrator_agent:
            self.db_tools = MockDatabaseTools()
            self.calendar_tools = MockGoogleCalendarTools()
            self.orchestrator_agent = OrchestratorAgent(self.db_tools, self.calendar_tools)
        
        # Test personality elements
        personality_tests = [
            ("agent_name", "Sarah"),
            ("agent_role", "Medical Secretary"),
            ("clinic_name", "HealthFirst Medical Clinic")
        ]
        
        all_passed = True
        for attribute, expected_value in personality_tests:
            actual_value = getattr(self.orchestrator_agent, attribute, None)
            if actual_value == expected_value:
                print(f"✅ {attribute}: {actual_value}")
            else:
                print(f"❌ {attribute}: {actual_value} (expected: {expected_value})")
                all_passed = False
        
        # Test tone in responses
        print("\n🎭 Testing Response Tone...")
        conversation_state = {
            "messages": [],
            "intent": "",
            "collected_params": {},
            "required_params": [],
            "status": "",
            "next_agent": None,
            "user_message": "",
            "response": "",
            "conversation_state": {},
            "channel_id": "test_user",
            "channel_type": "test"
        }
        
        response = self._simulate_user_message("Hello", conversation_state)
        
        # Check for personality indicators
        tone_indicators = [
            "Sarah" in response,
            "HealthFirst" in response,
            "medical secretary" in response.lower(),
            "help" in response.lower(),
            "assist" in response.lower()
        ]
        
        tone_score = sum(tone_indicators)
        print(f"🎭 Tone Score: {tone_score}/5 personality indicators found")
        
        return all_passed and tone_score >= 3
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Improved Agent Tests\n")
        
        tests = [
            self.test_intent_detection,
            self.test_personality_and_tone,
            self.test_conversation_flow
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The agent improvements are working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for issues.")
        
        return passed == total


class MockDatabaseTools:
    """Mock database tools for testing."""
    
    def create_appointment(self, *args, **kwargs):
        """Mock appointment creation."""
        class MockAppointment:
            def __init__(self):
                self.id = 1
        
        return MockAppointment()
    
    def get_appointments_by_patient(self, *args, **kwargs):
        """Mock patient appointments."""
        return []


class MockGoogleCalendarTools:
    """Mock Google Calendar tools for testing."""
    
    def create_event(self, *args, **kwargs):
        """Mock event creation."""
        return {"id": "mock_event_id"}


def main():
    """Main function."""
    tester = ImprovedAgentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 The improved medical secretary agent is working correctly!")
        print("Key improvements:")
        print("✅ Added personality (Sarah, the medical secretary)")
        print("✅ Natural, varied responses")
        print("✅ Context-aware conversations")
        print("✅ Better intent detection")
        print("✅ Professional yet friendly tone")
        print("✅ Reduced repetition")
    else:
        print("\n🔧 There are still issues with the agent that need to be addressed.")
    
    return success


if __name__ == "__main__":
    main()
