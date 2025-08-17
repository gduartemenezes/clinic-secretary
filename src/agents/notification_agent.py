"""
Notification Agent for sending appointment reminders and confirmations.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.tools.whatsapp_tools import WhatsAppTools
from src.tools.database_tools import DatabaseTools
from src.models.appointment import Appointment, AppointmentStatus


class NotificationAgent:
    """Notification Agent for sending appointment notifications via WhatsApp."""
    
    def __init__(self, whatsapp_tools: WhatsAppTools, db_tools: DatabaseTools):
        """Initialize the Notification Agent."""
        self.whatsapp_tools = whatsapp_tools
        self.db_tools = db_tools
    
    def send_appointment_confirmation(
        self,
        appointment_id: int,
        patient_phone: str
    ) -> Dict[str, Any]:
        """Send appointment confirmation to patient."""
        try:
            # Get appointment details
            appointment = self.db_tools.get_appointment_details(appointment_id)
            if not appointment:
                return {"success": False, "error": "Appointment not found"}
            
            # Format appointment details
            appointment_date = appointment.appointment_datetime.strftime("%B %d, %Y")
            appointment_time = appointment.appointment_datetime.strftime("%I:%M %p")
            
            # Get patient and doctor names (placeholder for now)
            patient_name = "Patient"  # In real implementation, get from patient table
            doctor_name = "Dr. Smith"  # In real implementation, get from doctor table
            
            # Send confirmation via WhatsApp
            result = self.whatsapp_tools.send_appointment_confirmation(
                to_phone_number=patient_phone,
                patient_name=patient_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                doctor_name=doctor_name,
                appointment_type=appointment.appointment_type
            )
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "whatsapp_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send confirmation: {str(e)}"
            }
    
    def send_appointment_reminder(
        self,
        appointment_id: int,
        patient_phone: str
    ) -> Dict[str, Any]:
        """Send appointment reminder to patient."""
        try:
            # Get appointment details
            appointment = self.db_tools.get_appointment_details(appointment_id)
            if not appointment:
                return {"success": False, "error": "Appointment not found"}
            
            # Format appointment details
            appointment_date = appointment.appointment_datetime.strftime("%B %d, %Y")
            appointment_time = appointment.appointment_datetime.strftime("%I:%M %p")
            
            # Get patient and doctor names (placeholder for now)
            patient_name = "Patient"  # In real implementation, get from patient table
            doctor_name = "Dr. Smith"  # In real implementation, get from doctor table
            
            # Send reminder via WhatsApp
            result = self.whatsapp_tools.send_appointment_reminder(
                to_phone_number=patient_phone,
                patient_name=patient_name,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                doctor_name=doctor_name
            )
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "whatsapp_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send reminder: {str(e)}"
            }
    
    def send_custom_message(
        self,
        patient_phone: str,
        message_text: str
    ) -> Dict[str, Any]:
        """Send custom message to patient."""
        try:
            result = self.whatsapp_tools.send_text_message(
                to_phone_number=patient_phone,
                message_text=message_text
            )
            
            return {
                "success": True,
                "whatsapp_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send custom message: {str(e)}"
            }
    
    def send_appointment_cancellation(
        self,
        appointment_id: int,
        patient_phone: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send appointment cancellation notice to patient."""
        try:
            # Get appointment details
            appointment = self.db_tools.get_appointment_details(appointment_id)
            if not appointment:
                return {"success": False, "error": "Appointment not found"}
            
            # Format appointment details
            appointment_date = appointment.appointment_datetime.strftime("%B %d, %Y")
            appointment_time = appointment.appointment_datetime.strftime("%I:%M %p")
            
            # Create cancellation message
            message = f"Your appointment scheduled for {appointment_date} at {appointment_time} has been cancelled."
            if reason:
                message += f" Reason: {reason}"
            message += "\n\nPlease contact us to reschedule."
            
            # Send cancellation notice
            result = self.whatsapp_tools.send_text_message(
                to_phone_number=patient_phone,
                message_text=message
            )
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "whatsapp_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send cancellation notice: {str(e)}"
            }
    
    def send_appointment_reschedule(
        self,
        appointment_id: int,
        patient_phone: str,
        new_datetime: datetime
    ) -> Dict[str, Any]:
        """Send appointment reschedule notice to patient."""
        try:
            # Get appointment details
            appointment = self.db_tools.get_appointment_details(appointment_id)
            if not appointment:
                return {"success": False, "error": "Appointment not found"}
            
            # Format old and new appointment details
            old_date = appointment.appointment_datetime.strftime("%B %d, %Y")
            old_time = appointment.appointment_datetime.strftime("%I:%M %p")
            new_date = new_datetime.strftime("%B %d, %Y")
            new_time = new_datetime.strftime("%I:%M %p")
            
            # Create reschedule message
            message = f"Your appointment has been rescheduled from {old_date} at {old_time} to {new_date} at {new_time}."
            message += "\n\nPlease confirm this new time works for you."
            
            # Send reschedule notice
            result = self.whatsapp_tools.send_text_message(
                to_phone_number=patient_phone,
                message_text=message
            )
            
            return {
                "success": True,
                "appointment_id": appointment_id,
                "whatsapp_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send reschedule notice: {str(e)}"
            }
    
    def get_upcoming_appointments_for_reminders(
        self,
        hours_ahead: int = 24
    ) -> list:
        """Get appointments that need reminders sent."""
        try:
            # Calculate the time range for reminders
            now = datetime.utcnow()
            reminder_time = now + timedelta(hours=hours_ahead)
            
            # This would need to be implemented in database_tools
            # For now, return empty list
            return []
            
        except Exception as e:
            print(f"Error getting upcoming appointments: {e}")
            return []
    
    def send_bulk_reminders(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Send reminders for all upcoming appointments."""
        try:
            appointments = self.get_upcoming_appointments_for_reminders(hours_ahead)
            
            results = []
            for appointment in appointments:
                # This would need patient phone number from the appointment
                # For now, skip
                pass
            
            return {
                "success": True,
                "reminders_sent": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send bulk reminders: {str(e)}"
            }
