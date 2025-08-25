"""
Conversation State Manager for maintaining conversation context across messages.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import json


class ConversationStateManager:
    """Manages conversation state persistence across messages."""
    
    def __init__(self, db_session: Session):
        """Initialize the conversation state manager."""
        self.db = db_session
    
    def get_conversation_state(
        self,
        channel_id: str,
        channel_type: str = "whatsapp",
        max_age_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """Get conversation state for a specific channel."""
        try:
            # Look for existing conversation state
            # In a real implementation, you'd have a ConversationState table
            # For now, we'll use a simple approach with the existing database
            
            # Check if we have any recent appointments for this phone number
            if channel_type == "whatsapp":
                # Try to find patient by phone number
                from src.models.patient import Patient
                from src.models.appointment import Appointment
                
                # Look for patient with this phone number
                patient = self.db.query(Patient).filter(
                    Patient.phone.ilike(f"%{channel_id}%")
                ).first()
                
                if patient:
                    # Get recent appointments for context
                    recent_appointments = self.db.query(Appointment).filter(
                        and_(
                            Appointment.patient_id == patient.id,
                            Appointment.appointment_datetime >= datetime.now() - timedelta(days=30)
                        )
                    ).order_by(Appointment.appointment_datetime.desc()).limit(5).all()
                    
                    # Build conversation state from patient data
                    conversation_state = {
                        "messages": [],
                        "intent": "",
                        "collected_params": {
                            "patient_name": patient.name,
                            "patient_phone": patient.phone,
                            "patient_id": patient.id
                        },
                        "required_params": [],
                        "status": "",
                        "modification_mode": False,
                        "last_updated": datetime.now().isoformat(),
                        "channel_id": channel_id,
                        "channel_type": channel_type,
                        "patient_context": {
                            "name": patient.name,
                            "phone": patient.phone,
                            "recent_appointments": [
                                {
                                    "id": apt.id,
                                    "datetime": apt.appointment_datetime.isoformat(),
                                    "type": apt.appointment_type,
                                    "status": apt.status.value
                                }
                                for apt in recent_appointments
                            ]
                        }
                    }
                    
                    return conversation_state
            
            # If no patient found, return basic state
            return {
                "messages": [],
                "intent": "",
                "collected_params": {},
                "required_params": [],
                "status": "",
                "modification_mode": False,
                "last_updated": datetime.now().isoformat(),
                "channel_id": channel_id,
                "channel_type": channel_type
            }
            
        except Exception as e:
            print(f"Error getting conversation state: {e}")
            # Return basic state on error
            return {
                "messages": [],
                "intent": "",
                "collected_params": {},
                "required_params": [],
                "status": "",
                "modification_mode": False,
                "last_updated": datetime.now().isoformat(),
                "channel_id": channel_id,
                "channel_type": channel_type
            }
    
    def update_conversation_state(
        self,
        channel_id: str,
        conversation_state: Dict[str, Any],
        channel_type: str = "whatsapp"
    ) -> bool:
        """Update conversation state for a specific channel."""
        try:
            # Update the last_updated timestamp
            conversation_state["last_updated"] = datetime.now().isoformat()
            conversation_state["channel_id"] = channel_id
            conversation_state["channel_type"] = channel_type
            
            # In a real implementation, you'd save this to a ConversationState table
            # For now, we'll just return success since the state is passed back to the caller
            
            return True
            
        except Exception as e:
            print(f"Error updating conversation state: {e}")
            return False
    
    def create_or_update_patient(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None
    ) -> Optional[int]:
        """Create or update a patient record."""
        try:
            from src.models.patient import Patient
            
            # Check if patient already exists
            patient = self.db.query(Patient).filter(
                Patient.phone.ilike(f"%{phone}%")
            ).first()
            
            if patient:
                # Update existing patient
                patient.name = name
                if email:
                    patient.email = email
                patient.updated_at = datetime.now()
            else:
                # Create new patient
                patient = Patient(
                    name=name,
                    phone=phone,
                    email=email,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.db.add(patient)
            
            self.db.commit()
            self.db.refresh(patient)
            
            return patient.id
            
        except Exception as e:
            print(f"Error creating/updating patient: {e}")
            self.db.rollback()
            return None
    
    def get_patient_context(
        self,
        channel_id: str,
        channel_type: str = "whatsapp"
    ) -> Optional[Dict[str, Any]]:
        """Get patient context for a channel."""
        try:
            if channel_type == "whatsapp":
                from src.models.patient import Patient
                from src.models.appointment import Appointment
                
                # Look for patient by phone number
                patient = self.db.query(Patient).filter(
                    Patient.phone.ilike(f"%{channel_id}%")
                ).first()
                
                if patient:
                    # Get upcoming appointments
                    upcoming_appointments = self.db.query(Appointment).filter(
                        and_(
                            Appointment.patient_id == patient.id,
                            Appointment.appointment_datetime >= datetime.now(),
                            Appointment.status.in_(["SCHEDULED", "CONFIRMED"])
                        )
                    ).order_by(Appointment.appointment_datetime).all()
                    
                    return {
                        "patient_id": patient.id,
                        "name": patient.name,
                        "phone": patient.phone,
                        "email": patient.email,
                        "upcoming_appointments": [
                            {
                                "id": apt.id,
                                "datetime": apt.appointment_datetime.isoformat(),
                                "type": apt.appointment_type,
                                "status": apt.status.value
                            }
                            for apt in upcoming_appointments
                        ]
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting patient context: {e}")
            return None
    
    def cleanup_old_conversations(self, max_age_hours: int = 24) -> int:
        """Clean up old conversation states."""
        try:
            # In a real implementation, you'd delete old conversation states
            # For now, just return 0 since we're not persisting them
            return 0
            
        except Exception as e:
            print(f"Error cleaning up old conversations: {e}")
            return 0
