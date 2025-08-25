#!/usr/bin/env python3
"""
Test script for debugging the clinic information functionality.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.clinic_info_tools import ClinicInfoTools
from src.agents.clinic_info_agent import ClinicInfoAgent


class ClinicInfoTester:
    """Test class for the clinic information functionality."""
    
    def __init__(self):
        """Initialize the clinic info tester."""
        self.clinic_tools = ClinicInfoTools()
        self.clinic_agent = ClinicInfoAgent(self.clinic_tools)
    
    def test_clinic_tools_initialization(self):
        """Test clinic tools initialization."""
        print("Testing clinic tools initialization...")
        try:
            # Test basic clinic info
            clinic_name = self.clinic_tools.get_clinic_name()
            print(f"✅ Clinic name: {clinic_name}")
            
            address = self.clinic_tools.get_full_address()
            print(f"✅ Clinic address: {address}")
            
            phone = self.clinic_tools.get_phone_number()
            print(f"✅ Clinic phone: {phone}")
            
            return True
        except Exception as e:
            print(f"❌ Error initializing clinic tools: {e}")
            return False
    
    def test_clinic_hours(self):
        """Test clinic hours functionality."""
        print("\nTesting clinic hours...")
        try:
            # Test specific day
            monday_hours = self.clinic_tools.get_hours_for_day("monday")
            print(f"✅ Monday hours: {monday_hours}")
            
            # Test all hours
            all_hours = self.clinic_tools.get_opening_hours()
            print(f"✅ All hours: {len(all_hours)} days configured")
            
            # Test abbreviated day
            tue_hours = self.clinic_tools.get_hours_for_day("tue")
            print(f"✅ Tuesday hours (abbreviated): {tue_hours}")
            
            return True
        except Exception as e:
            print(f"❌ Error testing clinic hours: {e}")
            return False
    
    def test_clinic_services(self):
        """Test clinic services functionality."""
        print("\nTesting clinic services...")
        try:
            services = self.clinic_tools.get_services()
            print(f"✅ Services available: {len(services)} services")
            
            # Test service availability
            has_primary_care = self.clinic_tools.check_service_available("Primary Care")
            print(f"✅ Primary Care available: {has_primary_care}")
            
            has_dental = self.clinic_tools.check_service_available("Dental Care")
            print(f"✅ Dental Care available: {has_dental}")
            
            return True
        except Exception as e:
            print(f"❌ Error testing clinic services: {e}")
            return False
    
    def test_clinic_specialties(self):
        """Test clinic specialties functionality."""
        print("\nTesting clinic specialties...")
        try:
            specialties = self.clinic_tools.get_specialties()
            print(f"✅ Specialties available: {len(specialties)} specialties")
            
            # Test specific specialty
            cardiology = self.clinic_tools.get_specialty_by_name("Cardiology")
            if cardiology:
                print(f"✅ Cardiology: {cardiology['description']}")
                print(f"✅ Cardiology doctors: {', '.join(cardiology['doctors'])}")
            else:
                print("❌ Cardiology specialty not found")
                return False
            
            # Test doctors by specialty
            cardiology_doctors = self.clinic_tools.get_doctors_by_specialty("Cardiology")
            print(f"✅ Cardiology doctors count: {len(cardiology_doctors)}")
            
            # Test all doctors
            all_doctors = self.clinic_tools.get_all_doctors()
            print(f"✅ Total doctors: {len(all_doctors)}")
            
            return True
        except Exception as e:
            print(f"❌ Error testing clinic specialties: {e}")
            return False
    
    def test_clinic_insurance(self):
        """Test clinic insurance functionality."""
        print("\nTesting clinic insurance...")
        try:
            insurance_plans = self.clinic_tools.get_insurance_plans()
            print(f"✅ Insurance plans: {len(insurance_plans)} plans")
            
            # Test specific insurance
            accepts_bcbs = self.clinic_tools.check_insurance_accepted("Blue Cross Blue Shield")
            print(f"✅ Accepts Blue Cross Blue Shield: {accepts_bcbs}")
            
            accepts_medicare = self.clinic_tools.check_insurance_accepted("Medicare")
            print(f"✅ Accepts Medicare: {accepts_medicare}")
            
            return True
        except Exception as e:
            print(f"❌ Error testing clinic insurance: {e}")
            return False
    
    def test_clinic_search(self):
        """Test clinic information search."""
        print("\nTesting clinic information search...")
        try:
            # Search for cardiology
            cardiology_results = self.clinic_tools.search_clinic_info("cardiology")
            print(f"✅ Cardiology search results: {len(cardiology_results)} results")
            
            # Search for primary care
            primary_care_results = self.clinic_tools.search_clinic_info("primary care")
            print(f"✅ Primary care search results: {len(primary_care_results)} results")
            
            # Search for insurance
            insurance_results = self.clinic_tools.search_clinic_info("blue cross")
            print(f"✅ Insurance search results: {len(insurance_results)} results")
            
            return True
        except Exception as e:
            print(f"❌ Error testing clinic search: {e}")
            return False
    
    def test_clinic_agent(self):
        """Test clinic information agent."""
        print("\nTesting clinic information agent...")
        try:
            # Test hours request
            conversation_state = {"messages": []}
            result = self.clinic_agent.process_information_request(
                "What are your clinic hours?",
                conversation_state
            )
            
            print(f"✅ Hours response: {result['response'][:100]}...")
            print(f"✅ Info type: {result['info_type']}")
            
            # Test specialty request
            result2 = self.clinic_agent.process_information_request(
                "Do you have cardiology specialists?",
                conversation_state
            )
            
            print(f"✅ Specialty response: {result2['response'][:100]}...")
            print(f"✅ Info type: {result2['info_type']}")
            
            return True
        except Exception as e:
            print(f"❌ Error testing clinic agent: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Clinic Information Debug Tests\n")
        
        tests = [
            self.test_clinic_tools_initialization,
            self.test_clinic_hours,
            self.test_clinic_services,
            self.test_clinic_specialties,
            self.test_clinic_insurance,
            self.test_clinic_search,
            self.test_clinic_agent
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
    tester = ClinicInfoTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
