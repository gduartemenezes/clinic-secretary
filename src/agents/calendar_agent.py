"""
Calendar Agent for appointment scheduling.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from src.tools.google_calendar_tools import GoogleCalendarTools
from src.tools.database_tools import DatabaseTools
from src.models.appointment import AppointmentStatus


class CalendarAgent:
    """Calendar Agent for handling appointment scheduling."""
    
    def __init__(self, db_tools: DatabaseTools, calendar_tools: GoogleCalendarTools):
        """Initialize the Calendar Agent."""
        self.db_tools = db_tools
        self.calendar_tools = calendar_tools
    
    def process_scheduling_request(
        self,
        user_message: str,
        collected_params: Dict[str, Any],
        required_params: List[str]
    ) -> Dict[str, Any]:
        """Process a scheduling request from the user."""
        # Extract information from user message
        extracted_info = self._extract_scheduling_info(user_message)
        
        # Update collected parameters
        collected_params.update(extracted_info)
        
        # Check what parameters are still needed
        missing_params = [param for param in required_params if param not in collected_params]
        
        if missing_params:
            # Ask for missing information
            response = self._ask_for_missing_params(missing_params)
            return {
                "response": response,
                "collected_params": collected_params,
                "required_params": required_params,
                "status": "collecting_info"
            }
        else:
            # All parameters collected, attempt to schedule
            return self._schedule_appointment(collected_params)
    
    def _extract_scheduling_info(self, user_message: str) -> Dict[str, Any]:
        """Extract scheduling information from user message."""
        extracted_info = {}
        message_lower = user_message.lower()
        
        # Extract date/time information
        if "today" in message_lower:
            extracted_info["date"] = datetime.now().date()
        elif "tomorrow" in message_lower:
            extracted_info["date"] = (datetime.now() + timedelta(days=1)).date()
        
        # Extract time information
        if "morning" in message_lower:
            extracted_info["time_preference"] = "morning"
            extracted_info["time"] = "09:00"
        elif "afternoon" in message_lower:
            extracted_info["time_preference"] = "afternoon"
            extracted_info["time"] = "14:00"
        elif "evening" in message_lower:
            extracted_info["time_preference"] = "evening"
            extracted_info["time"] = "17:00"
        
        # Extract specific time patterns
        import re
        time_pattern = r'(\d{1,2})\s*(?:am|pm|AM|PM)?'
        time_matches = re.findall(time_pattern, message_lower)
        if time_matches:
            hour = int(time_matches[0])
            if "pm" in message_lower and hour < 12:
                hour += 12
            elif "am" in message_lower and hour == 12:
                hour = 0
            extracted_info["time"] = f"{hour:02d}:00"
        
        # Extract appointment type
        appointment_types = ["consultation", "checkup", "follow-up", "emergency"]
        for apt_type in appointment_types:
            if apt_type in message_lower:
                extracted_info["appointment_type"] = apt_type
                break
        
        # Combine date and time if both are available
        if extracted_info.get("date") and extracted_info.get("time"):
            date_str = extracted_info["date"].strftime("%Y-%m-%d")
            time_str = extracted_info["time"]
            try:
                extracted_info["datetime"] = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                pass
        
        return extracted_info
    
    def _ask_for_missing_params(self, missing_params: List[str]) -> str:
        """Generate a response asking for missing parameters."""
        if "patient_name" in missing_params:
            return "What is your name?"
        elif "patient_phone" in missing_params:
            return "What is your phone number?"
        elif "date" in missing_params:
            return "What date would you like to schedule the appointment for?"
        elif "time" in missing_params:
            return "What time would you prefer for the appointment?"
        elif "doctor_specialty" in missing_params:
            return "What type of doctor do you need to see?"
        elif "appointment_type" in missing_params:
            return "What type of appointment do you need?"
        else:
            return "I need some additional information to schedule your appointment. Could you please provide more details?"
    
    def _schedule_appointment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to schedule the appointment."""
        try:
            # Check if we have the required datetime
            if not params.get("datetime"):
                return {
                    "response": "I need to know when you'd like to schedule the appointment. What date and time would you prefer?",
                    "collected_params": params,
                    "required_params": ["datetime"],
                    "status": "collecting_info"
                }
            
            # For now, we'll use placeholder values for patient_id and doctor_id
            # In a real implementation, you'd look these up or create them
            
            # Create appointment in database
            appointment = self.db_tools.create_appointment(
                patient_id=1,  # Placeholder - should be looked up
                doctor_id=1,   # Placeholder - should be looked up
                appointment_datetime=params.get("datetime"),
                appointment_type=params.get("appointment_type", "consultation"),
                notes=params.get("notes")
            )
            
            # Create event in Google Calendar
            calendar_event = self.calendar_tools.create_event(
                summary=f"Appointment: {params.get('patient_name', 'Patient')}",
                start_time=params.get("datetime"),
                end_time=params.get("datetime") + timedelta(hours=1),
                description=f"Appointment Type: {params.get('appointment_type', 'consultation')}",
                location="Medical Clinic"
            )
            
            return {
                "response": f"Great! I've scheduled your {params.get('appointment_type', 'appointment')} for {params.get('datetime').strftime('%B %d, %Y at %I:%M %p')}. You'll receive a confirmation shortly.",
                "collected_params": params,
                "required_params": [],
                "status": "completed",
                "appointment_id": appointment.id,
                "calendar_event_id": calendar_event.get("id") if calendar_event else None
            }
            
        except Exception as e:
            return {
                "response": f"I'm sorry, but I encountered an error while scheduling your appointment: {str(e)}. Please try again or contact our office directly.",
                "collected_params": params,
                "required_params": params.get("required_params", []),
                "status": "error"
            }
    
    def check_availability(
        self,
        doctor_id: int,
        date: datetime,
        time_slot: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check doctor availability for a specific date/time."""
        try:
            # Get doctor's schedule from database
            schedule = self.db_tools.get_doctor_schedule(doctor_id, date)
            
            # Get Google Calendar events
            calendar_events = self.calendar_tools.list_events(
                time_min=date,
                time_max=date + timedelta(days=1)
            )
            
            # Combine and analyze availability
            available_slots = self._find_available_slots(schedule, calendar_events, date)
            
            return {
                "date": date.strftime("%Y-%m-%d"),
                "available_slots": available_slots,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "date": date.strftime("%Y-%m-%d"),
                "available_slots": [],
                "status": "error",
                "error": str(e)
            }
    
    def _find_available_slots(
        self,
        db_schedule: List,
        calendar_events: List[Dict],
        date: datetime
    ) -> List[str]:
        """Find available time slots based on database and calendar data."""
        # This is a simplified implementation
        # In a real system, you'd have more sophisticated logic
        
        # Standard business hours: 9 AM to 5 PM
        start_hour = 9
        end_hour = 17
        
        available_slots = []
        
        for hour in range(start_hour, end_hour):
            slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Check if slot conflicts with database appointments
            db_conflict = any(
                apt.appointment_datetime.hour == hour 
                for apt in db_schedule
            )
            
            # Check if slot conflicts with calendar events
            calendar_conflict = any(
                (event_start := datetime.fromisoformat(event['start'].replace('Z', '+00:00')),
                event_start.hour == hour)
                for event in calendar_events
                if 'T' in event['start']  # Only check time-based events
            )
            
            if not db_conflict and not calendar_conflict:
                available_slots.append(slot_time.strftime("%I:%M %p"))
        
        return available_slots
