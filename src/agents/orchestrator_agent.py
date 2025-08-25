"""
Orchestrator Agent for intent detection and routing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.tools.database_tools import DatabaseTools
from src.tools.google_calendar_tools import GoogleCalendarTools
from src.tools.clinic_info_tools import ClinicInfoTools
from src.agents.calendar_agent import CalendarAgent
from src.agents.clinic_info_agent import ClinicInfoAgent


class OrchestratorAgent:
    """Orchestrator Agent for detecting intent and routing to appropriate agents."""
    
    def __init__(self, db_tools: DatabaseTools, calendar_tools: GoogleCalendarTools):
        """Initialize the Orchestrator Agent."""
        self.db_tools = db_tools
        self.calendar_tools = calendar_tools
        self.clinic_info_tools = ClinicInfoTools()
        self.calendar_agent = CalendarAgent(db_tools, calendar_tools)
        self.clinic_info_agent = ClinicInfoAgent(self.clinic_info_tools)
        
        # Agent personality and identity
        self.agent_name = "Sarah"
        self.agent_role = "Medical Secretary"
        self.clinic_name = "HealthFirst Medical Clinic"
        
        # Define intent keywords with better coverage
        self.scheduling_keywords = [
            "schedule", "book", "appointment", "make appointment", "set up",
            "reserve", "book time", "schedule visit", "make reservation",
            "need to see", "want to see", "see doctor", "visit doctor",
            "checkup", "consultation", "follow-up", "examination"
        ]
        
        self.information_keywords = [
            "information", "info", "details", "about", "what", "how", "when",
            "where", "hours", "address", "phone", "contact", "specialist",
            "specialty", "doctor", "physician", "service", "offer", "available",
            "know", "tell me", "show me", "find out", "learn about"
        ]
        
        self.cancellation_keywords = [
            "cancel", "reschedule", "change", "modify", "postpone", "move",
            "different time", "different date", "not available", "can't make it",
            "need to cancel", "want to cancel", "have to cancel"
        ]
        
        self.appointment_check_keywords = [
            "my appointment", "check appointment", "appointment status",
            "when is my", "what time", "confirmation", "reminder",
            "appointments", "my schedule", "upcoming", "check on my",
            "check on my appointment", "my apppointments", "my apppointment"
        ]
        
        self.emergency_keywords = [
            "emergency", "urgent", "immediate", "critical", "pain", "hurt",
            "serious", "bad", "worse", "can't wait", "need help now"
        ]
    
    def detect_intent(self, user_message: str) -> str:
        """Detect the user's intent from their message."""
        message_lower = user_message.lower()
        
        # Check for emergency intent first (highest priority)
        if any(keyword in message_lower for keyword in self.emergency_keywords):
            return "emergency"
        
        # Check for personal questions (high priority)
        if any(word in message_lower for word in ["do you know me", "remember me", "my name", "who am i"]):
            return "personal_question"
        
        # Check for cancellation intent (high priority - before scheduling)
        if any(keyword in message_lower for keyword in self.cancellation_keywords):
            return "modify_appointment"
        
        # Check for appointment checking intent
        if any(keyword in message_lower for keyword in self.appointment_check_keywords):
            return "check_appointment"
        
        # Check for scheduling intent
        if any(keyword in message_lower for keyword in self.scheduling_keywords):
            return "schedule_appointment"
        
        # Check for information intent
        if any(keyword in message_lower for keyword in self.information_keywords):
            return "get_information"
        
        # Default to general conversation
        return "general_conversation"
    
    def process_message(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a user message and route to appropriate agent."""
        # Detect intent
        intent = self.detect_intent(user_message)
        
        # Update conversation state
        conversation_state["intent"] = intent
        conversation_state["messages"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add conversation context for better memory
        if "conversation_context" not in conversation_state:
            conversation_state["conversation_context"] = {
                "total_messages": 0,
                "first_message_time": datetime.now().isoformat(),
                "last_message_time": datetime.now().isoformat()
            }
        
        conversation_state["conversation_context"]["total_messages"] += 1
        conversation_state["conversation_context"]["last_message_time"] = datetime.now().isoformat()
        
        # Route to appropriate agent based on intent
        if intent == "schedule_appointment":
            return self._handle_scheduling(user_message, conversation_state)
        elif intent == "get_information":
            return self._handle_information_request(user_message, conversation_state)
        elif intent == "modify_appointment":
            return self._handle_modification_request(user_message, conversation_state)
        elif intent == "check_appointment":
            return self._handle_appointment_check(user_message, conversation_state)
        elif intent == "emergency":
            return self._handle_emergency_request(user_message, conversation_state)
        elif intent == "personal_question":
            return self._handle_personal_question(user_message, conversation_state)
        else:
            return self._handle_general_conversation(user_message, conversation_state)
    
    def _handle_scheduling(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle appointment scheduling requests."""
        # Initialize scheduling parameters if not already present
        if "collected_params" not in conversation_state:
            conversation_state["collected_params"] = {}
        
        if "required_params" not in conversation_state:
            conversation_state["required_params"] = [
                "patient_name",
                "patient_phone", 
                "date",
                "time",
                "doctor_specialty",
                "appointment_type"
            ]
        
        # Extract patient name from user message if not already collected
        if "patient_name" not in conversation_state["collected_params"]:
            # Simple name extraction (you could use more sophisticated NLP here)
            words = user_message.split()
            if len(words) >= 2 and words[0].lower() in ["my", "i'm", "i", "this", "the"]:
                if words[1].lower() in ["name", "is", "am"]:
                    if len(words) >= 3:
                        conversation_state["collected_params"]["patient_name"] = " ".join(words[2:4])  # Take first two words after "is"
        
        # Process with calendar agent
        result = self.calendar_agent.process_scheduling_request(
            user_message,
            conversation_state["collected_params"],
            conversation_state["required_params"]
        )
        
        # Update conversation state with new parameters
        conversation_state["collected_params"].update(result["collected_params"])
        conversation_state["required_params"] = result["required_params"]
        conversation_state["status"] = result["status"]
        
        # Add agent response to messages
        conversation_state["messages"].append({
            "role": "assistant",
            "content": result["response"],
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": result["response"],
            "conversation_state": conversation_state,
            "next_agent": "calendar_agent" if result["status"] == "collecting_info" else None
        }
    
    def _handle_information_request(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle information requests."""
        # Use the ClinicInfoAgent to process the request
        result = self.clinic_info_agent.process_information_request(
            user_message,
            conversation_state
        )
        
        return {
            "response": result["response"],
            "conversation_state": result["conversation_state"],
            "next_agent": None
        }
    
    def _handle_modification_request(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle appointment modification requests."""
        # Check if we have patient info from previous conversation
        if conversation_state.get("collected_params", {}).get("patient_name"):
            response = f"I can help you modify your appointment, {conversation_state['collected_params']['patient_name']}. To proceed, I'll need your phone number to look up your existing appointment. What is your phone number?"
        else:
            response = "I can help you modify your appointment. To proceed, I'll need your name and phone number to look up your existing appointment. What is your name?"
        
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        # Set state for modification flow
        conversation_state["modification_mode"] = True
        conversation_state["required_params"] = ["patient_name", "patient_phone"]
        conversation_state["collected_params"] = {}
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "next_agent": None
        }
    
    def _handle_appointment_check(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle appointment checking requests."""
        # Check if we have patient info
        patient_name = conversation_state.get("collected_params", {}).get("patient_name")
        patient_phone = conversation_state.get("collected_params", {}).get("patient_phone")
        
        if patient_name and patient_phone:
            # Try to look up appointments
            try:
                appointments = self.db_tools.get_appointments_by_patient(patient_name, patient_phone)
                if appointments:
                    response = f"Here are your upcoming appointments, {patient_name}:\n\n"
                    for apt in appointments[:3]:  # Show next 3 appointments
                        response += f"• {apt.appointment_datetime.strftime('%B %d, %Y at %I:%M %p')} - {apt.appointment_type}\n"
                    response += "\nIs there anything specific you'd like to know about these appointments?"
                else:
                    response = f"I don't see any upcoming appointments for {patient_name}. Would you like to schedule a new appointment?"
            except Exception as e:
                response = "I'm having trouble accessing your appointment information right now. Could you please provide your name and phone number so I can help you?"
                conversation_state["required_params"] = ["patient_name", "patient_phone"]
                conversation_state["collected_params"] = {}
        else:
            response = "I'd be happy to check your appointments for you. To do that, I'll need your name and phone number. What is your name?"
            conversation_state["required_params"] = ["patient_name", "patient_phone"]
            conversation_state["collected_params"] = {}
        
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "next_agent": None
        }
    
    def _handle_personal_question(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle personal questions about the user."""
        patient_name = conversation_state.get("collected_params", {}).get("patient_name")
        
        if patient_name:
            response = f"Of course I remember you, {patient_name}! You're a valued patient at {self.clinic_name}. How can I assist you today?"
        else:
            response = f"I'm {self.agent_name}, your medical secretary at {self.clinic_name}. While I don't have your information yet, I'm here to help you with appointments, information, or any other questions you might have. What's your name?"
            conversation_state["required_params"] = ["patient_name"]
            conversation_state["collected_params"] = {}
        
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "next_agent": None
        }
    
    def _handle_general_conversation(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general conversation with personality."""
        # Check if we have patient info
        patient_name = conversation_state.get("collected_params", {}).get("patient_name")
        
        # Generate varied, natural responses
        responses = [
            f"Hello! I'm {self.agent_name}, your medical secretary at {self.clinic_name}. I'm here to help you with appointments, information, or any questions you might have. How can I assist you today?",
            f"Hi there! I'm {self.agent_name}, and I'm here to make your healthcare experience as smooth as possible. What can I help you with today?",
            f"Good day! I'm {self.agent_name}, your dedicated medical secretary. Whether you need to schedule an appointment, get information about our services, or have any other questions, I'm here to help. What would you like to do?",
            f"Welcome! I'm {self.agent_name}, and I'm excited to assist you today. How can I make your visit to {self.clinic_name} more convenient?"
        ]
        
        # Use conversation context to choose appropriate response
        if patient_name:
            response = f"Hello {patient_name}! It's great to see you again. How can I help you today?"
        else:
            import random
            response = random.choice(responses)
        
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "next_agent": None
        }
    
    def _handle_emergency_request(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle emergency requests."""
        try:
            emergency_contact = self.clinic_info_tools.get_emergency_contact()
        except:
            emergency_contact = "+1-555-911-0000"
        
        response = f"🚨 EMERGENCY: If this is a medical emergency, please call {emergency_contact} immediately or go to the nearest emergency room.\n\n"
        response += "For urgent but non-emergency care, please call our main office during business hours.\n\n"
        response += "This AI assistant cannot provide emergency medical advice."
        
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "next_agent": None
        }
    
    def get_conversation_summary(self, conversation_state: Dict[str, Any]) -> str:
        """Get a summary of the current conversation."""
        if not conversation_state.get("messages"):
            return "No conversation history available."
        
        # Get the last few messages for context
        recent_messages = conversation_state["messages"][-5:]  # Last 5 messages
        
        summary = "Recent conversation:\n"
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            summary += f"{role}: {msg['content']}\n"
        
        if conversation_state.get("intent"):
            summary += f"\nDetected intent: {conversation_state['intent']}"
        
        if conversation_state.get("collected_params"):
            summary += f"\nCollected parameters: {conversation_state['collected_params']}"
        
        return summary
