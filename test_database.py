#!/usr/bin/env python3
"""
Test script for debugging the database functionality.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database import db_manager
from src.tools.database_tools import DatabaseTools
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment, AppointmentStatus


class DatabaseTester:
    """Test class for the database functionality."""
    
    def __init__(self):
        """Initialize the database tester."""
        self.db_manager = db_manager
    
    def test_database_connection(self):
        """Test database connection and table creation."""
        print("Testing database connection...")
        try:
            # Create tables
            self.db_manager.create_tables()
            print("✅ Database tables created successfully")
            
            # Test session creation
            with self.db_manager.get_session() as session:
                print("✅ Database session created successfully")
                
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def test_patient_creation(self):
        """Test patient creation."""
        print("\nTesting patient creation...")
        try:
            with self.db_manager.get_session() as session:
                # Create a test patient
                patient = Patient(
                    name="John Doe",
                    phone="+1234567890",
                    email="john.doe@example.com",
                    date_of_birth=datetime(1990, 1, 1),
                    insurance_provider="Blue Cross Blue Shield"
                )
                
                session.add(patient)
                session.commit()
                session.refresh(patient)
                
                print(f"✅ Patient created: ID {patient.id}, Name: {patient.name}")
                
                # Clean up
                session.delete(patient)
                session.commit()
                
                return True
        except Exception as e:
            print(f"❌ Error creating patient: {e}")
            return False
    
    def test_doctor_creation(self):
        """Test doctor creation."""
        print("\nTesting doctor creation...")
        try:
            with self.db_manager.get_session() as session:
                # Create a test doctor
                doctor = Doctor(
                    name="Dr. Jane Smith",
                    specialty="Cardiology",
                    phone="+1234567891",
                    email="jane.smith@clinic.com"
                )
                
                session.add(doctor)
                session.commit()
                session.refresh(doctor)
                
                print(f"✅ Doctor created: ID {doctor.id}, Name: {doctor.name}")
                
                # Clean up
                session.delete(doctor)
                session.commit()
                
                return True
        except Exception as e:
            print(f"❌ Error creating doctor: {e}")
            return False
    
    def test_appointment_creation(self):
        """Test appointment creation."""
        print("\nTesting appointment creation...")
        try:
            with self.db_manager.get_session() as session:
                # Create test patient and doctor
                patient = Patient(
                    name="Test Patient",
                    phone="+1234567890",
                    email="test@example.com"
                )
                session.add(patient)
                
                doctor = Doctor(
                    name="Test Doctor",
                    specialty="General Practice",
                    phone="+1234567891",
                    email="doctor@clinic.com"
                )
                session.add(doctor)
                
                session.commit()
                session.refresh(patient)
                session.refresh(doctor)
                
                # Create appointment
                appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    appointment_datetime=datetime.now() + timedelta(days=1),
                    appointment_type="Check-up",
                    notes="Regular check-up appointment"
                )
                
                session.add(appointment)
                session.commit()
                session.refresh(appointment)
                
                print(f"✅ Appointment created: ID {appointment.id}")
                
                # Test database tools
                db_tools = DatabaseTools(session)
                retrieved_appointment = db_tools.get_appointment_details(appointment.id)
                
                if retrieved_appointment:
                    print(f"✅ Appointment retrieved: {retrieved_appointment.appointment_type}")
                else:
                    print("❌ Failed to retrieve appointment")
                    return False
                
                # Clean up
                session.delete(appointment)
                session.delete(patient)
                session.delete(doctor)
                session.commit()
                
                return True
        except Exception as e:
            print(f"❌ Error creating appointment: {e}")
            return False
    
    def test_database_tools(self):
        """Test database tools functionality."""
        print("\nTesting database tools...")
        try:
            with self.db_manager.get_session() as session:
                db_tools = DatabaseTools(session)
                
                # Test statistics
                stats = db_tools.get_appointment_statistics()
                print(f"✅ Statistics retrieved: {stats['total_appointments']} total appointments")
                
                # Test upcoming appointments
                upcoming = db_tools.get_upcoming_appointments(days=7)
                print(f"✅ Upcoming appointments: {len(upcoming)} appointments")
                
                return True
        except Exception as e:
            print(f"❌ Error testing database tools: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Database Debug Tests\n")
        
        tests = [
            self.test_database_connection,
            self.test_patient_creation,
            self.test_doctor_creation,
            self.test_appointment_creation,
            self.test_database_tools
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
    tester = DatabaseTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
