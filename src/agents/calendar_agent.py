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
        
        # Agent personality
        self.agent_name = "Sarah"
        self.clinic_name = "HealthFirst Medical Clinic"
    
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
            # Ask for missing information in a natural way
            response = self._ask_for_missing_params_naturally(missing_params, collected_params)
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
        
        # Extract date information with natural language processing
        if "today" in message_lower:
            extracted_info["date"] = datetime.now().date()
        elif "tomorrow" in message_lower:
            extracted_info["date"] = (datetime.now() + timedelta(days=1)).date()
        elif "next week" in message_lower:
            extracted_info["date"] = (datetime.now() + timedelta(days=7)).date()
        elif "this week" in message_lower:
            # Find next available day this week
            current_day = datetime.now()
            days_ahead = 0
            while days_ahead < 7:
                check_date = current_day + timedelta(days=days_ahead)
                if check_date.weekday() < 5:  # Monday to Friday
                    extracted_info["date"] = check_date.date()
                    break
                days_ahead += 1
        
        # Extract time information with natural language processing
        if "morning" in message_lower:
            extracted_info["time_preference"] = "morning"
            extracted_info["time"] = "09:00"
        elif "afternoon" in message_lower:
            extracted_info["time_preference"] = "afternoon"
            extracted_info["time"] = "14:00"
        elif "evening" in message_lower:
            extracted_info["time_preference"] = "evening"
            extracted_info["time"] = "17:00"
        elif "early" in message_lower:
            extracted_info["time_preference"] = "early"
            extracted_info["time"] = "08:00"
        elif "late" in message_lower:
            extracted_info["time_preference"] = "late"
            extracted_info["time"] = "16:00"
        
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
        
        # Extract appointment type with better recognition
        appointment_types = {
            "consultation": ["consultation", "consult", "visit", "see doctor"],
            "checkup": ["checkup", "check up", "check-up", "physical", "exam", "examination"],
            "follow-up": ["follow up", "follow-up", "followup", "follow"],
            "emergency": ["emergency", "urgent", "immediate"],
            "routine": ["routine", "regular", "annual", "yearly"],
            "specialist": ["specialist", "specialty", "specialized"]
        }
        
        for apt_type, keywords in appointment_types.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted_info["appointment_type"] = apt_type
                break
        
        # Extract doctor specialty
        specialties = [
            "general", "family", "internal medicine", "cardiology", "dermatology",
            "orthopedics", "pediatrics", "gynecology", "neurology", "psychiatry"
        ]
        
        for specialty in specialties:
            if specialty in message_lower:
                extracted_info["doctor_specialty"] = specialty
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
    
    def _ask_for_missing_params_naturally(
        self, 
        missing_params: List[str], 
        collected_params: Dict[str, Any]
    ) -> str:
        """Generate natural responses asking for missing parameters."""
        patient_name = collected_params.get("patient_name", "")
        
        # Personalized responses based on what we already know
        if "patient_name" in missing_params:
            if patient_name:
                return f"Thanks {patient_name}! I just need a few more details to schedule your appointment. What is your phone number?"
            else:
                return "I'd be happy to help you schedule an appointment! To get started, what's your name?"
        
        elif "patient_phone" in missing_params:
            if patient_name:
                return f"Perfect {patient_name}! I just need your phone number to complete the scheduling. What's the best number to reach you at?"
            else:
                return "Great! I just need your phone number to complete the scheduling. What's the best number to reach you at?"
        
        elif "date" in missing_params:
            if patient_name:
                return f"Thanks {patient_name}! What date would work best for you? You can say 'tomorrow', 'next week', or give me a specific date."
            else:
                return "What date would work best for you? You can say 'tomorrow', 'next week', or give me a specific date."
        
        elif "time" in missing_params:
            if patient_name:
                return f"Perfect {patient_name}! What time of day would you prefer? I have morning, afternoon, and evening slots available."
            else:
                return "What time of day would you prefer? I have morning, afternoon, and evening slots available."
        
        elif "doctor_specialty" in missing_params:
            if patient_name:
                return f"Thanks {patient_name}! What type of doctor do you need to see? I can help with general practitioners, specialists, or specific medical areas."
            else:
                return "What type of doctor do you need to see? I can help with general practitioners, specialists, or specific medical areas."
        
        elif "appointment_type" in missing_params:
            if patient_name:
                return f"Thanks {patient_name}! What type of appointment do you need? For example, a consultation, checkup, follow-up, or something else?"
            else:
                return "What type of appointment do you need? For example, a consultation, checkup, follow-up, or something else?"
        
        else:
            if patient_name:
                return f"I need a few more details to schedule your appointment, {patient_name}. Could you please provide more information about what you need?"
            else:
                return "I need a few more details to schedule your appointment. Could you please provide more information about what you need?"
    
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
            
            # Ensure we have a valid datetime
            appointment_datetime = params.get("datetime")
            if not appointment_datetime:
                return {
                    "response": "I need to know when you'd like to schedule the appointment. What date and time would you prefer?",
                    "collected_params": params,
                    "required_params": ["datetime"],
                    "status": "collecting_info"
                }
            
            # Create appointment in database
            appointment = self.db_tools.create_appointment(
                patient_id=1,  # Placeholder - should be looked up
                doctor_id=1,   # Placeholder - should be looked up
                appointment_datetime=appointment_datetime,
                appointment_type=params.get("appointment_type", "consultation"),
                notes=params.get("notes")
            )
            
            # Create event in Google Calendar
            calendar_event = self.calendar_tools.create_event(
                summary=f"Appointment: {params.get('patient_name', 'Patient')}",
                start_time=appointment_datetime,
                end_time=appointment_datetime + timedelta(hours=1),
                description=f"Appointment Type: {params.get('appointment_type', 'consultation')}",
                location="Medical Clinic"
            )
            
            # Generate natural confirmation message
            patient_name = params.get('patient_name', '')
            appointment_type = params.get('appointment_type', 'appointment')
            formatted_datetime = appointment_datetime.strftime('%B %d, %Y at %I:%M %p')
            
            if patient_name:
                response = f"Perfect {patient_name}! I've successfully scheduled your {appointment_type} for {formatted_datetime}. You'll receive a confirmation message shortly with all the details."
            else:
                response = f"Excellent! I've successfully scheduled your {appointment_type} for {formatted_datetime}. You'll receive a confirmation message shortly with all the details."
            
            response += "\n\nIs there anything else I can help you with today?"
            
            return {
                "response": response,
                "collected_params": params,
                "required_params": [],
                "status": "completed",
                "appointment_id": appointment.id,
                "calendar_event_id": calendar_event.get("id") if calendar_event else None
            }
            
        except Exception as e:
            # Handle errors gracefully with natural language
            error_response = f"I'm sorry, but I encountered an issue while scheduling your appointment. "
            error_response += "This sometimes happens due to system updates or temporary issues. "
            error_response += "Could you please try again in a moment, or if the problem persists, "
            error_response += "feel free to call our office directly and I'll make sure they help you right away."
            
            return {
                "response": error_response,
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
