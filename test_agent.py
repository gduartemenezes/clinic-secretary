#!/usr/bin/env python3
"""
Test script for debugging the AI agent functionality.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.graph import medical_secretary_graph
from src.database import db_manager


class AgentTester:
    """Test class for the AI agent functionality."""
    
    def __init__(self):
        """Initialize the agent tester."""
        self.db_manager = db_manager
        self.medical_secretary_graph = medical_secretary_graph
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        print("Testing agent initialization...")
        try:
            # Initialize database
            self.db_manager.create_tables()
            print("✅ Database tables created successfully")
            
            # Test graph initialization
            print("✅ Medical secretary graph initialized")
            
            return True
        except Exception as e:
            print(f"❌ Error initializing agent: {e}")
            return False
    
    def test_basic_conversation(self):
        """Test basic conversation flow."""
        print("\nTesting basic conversation...")
        try:
            # Get a database session
            with self.db_manager.get_session() as session:
                # Test a simple message
                result = self.medical_secretary_graph.process_message(
                    user_message="Hello, I need to schedule an appointment",
                    conversation_state={},
                    db_session=session
                )
                
                print(f"✅ Agent response: {result['response'][:100]}...")
                print(f"✅ Intent detected: {result['intent']}")
                print(f"✅ Status: {result['status']}")
                
                return True
        except Exception as e:
            print(f"❌ Error in conversation: {e}")
            return False
    
    def test_clinic_information(self):
        """Test clinic information requests."""
        print("\nTesting clinic information...")
        try:
            with self.db_manager.get_session() as session:
                result = self.medical_secretary_graph.process_message(
                    user_message="What are your clinic hours?",
                    conversation_state={},
                    db_session=session
                )
                
                print(f"✅ Clinic info response: {result['response'][:100]}...")
                print(f"✅ Intent detected: {result['intent']}")
                
                return True
        except Exception as e:
            print(f"❌ Error in clinic info: {e}")
            return False
    
    def test_emergency_handling(self):
        """Test emergency intent detection."""
        print("\nTesting emergency handling...")
        try:
            with self.db_manager.get_session() as session:
                result = self.medical_secretary_graph.process_message(
                    user_message="I have an emergency!",
                    conversation_state={},
                    db_session=session
                )
                
                print(f"✅ Emergency response: {result['response'][:100]}...")
                print(f"✅ Intent detected: {result['intent']}")
                
                return True
        except Exception as e:
            print(f"❌ Error in emergency handling: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting AI Agent Debug Tests\n")
        
        tests = [
            self.test_agent_initialization,
            self.test_basic_conversation,
            self.test_clinic_information,
            self.test_emergency_handling
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the output above.")
        
        return passed == total


def main():
    """Main function."""
    tester = AgentTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
