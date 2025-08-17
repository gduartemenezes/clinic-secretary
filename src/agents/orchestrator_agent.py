"""
Orchestrator Agent for intent detection and routing.
"""

from typing import Dict, Any, List, Optional
from src.tools.database_tools import DatabaseTools
from src.tools.google_calendar_tools import GoogleCalendarTools
from src.agents.calendar_agent import CalendarAgent


class OrchestratorAgent:
    """Orchestrator Agent for detecting intent and routing to appropriate agents."""
    
    def __init__(self, db_tools: DatabaseTools, calendar_tools: GoogleCalendarTools):
        """Initialize the Orchestrator Agent."""
        self.db_tools = db_tools
        self.calendar_tools = calendar_tools
        self.calendar_agent = CalendarAgent(db_tools, calendar_tools)
        
        # Define intent keywords
        self.scheduling_keywords = [
            "schedule", "book", "appointment", "make appointment", "set up",
            "reserve", "book time", "schedule visit", "make reservation"
        ]
        
        self.information_keywords = [
            "information", "info", "details", "about", "what", "how", "when",
            "where", "hours", "address", "phone", "contact"
        ]
        
        self.cancellation_keywords = [
            "cancel", "reschedule", "change", "modify", "postpone", "move"
        ]
    
    def detect_intent(self, user_message: str) -> str:
        """Detect the user's intent from their message."""
        message_lower = user_message.lower()
        
        # Check for scheduling intent
        if any(keyword in message_lower for keyword in self.scheduling_keywords):
            return "schedule_appointment"
        
        # Check for information intent
        if any(keyword in message_lower for keyword in self.information_keywords):
            return "get_information"
        
        # Check for cancellation intent
        if any(keyword in message_lower for keyword in self.cancellation_keywords):
            return "modify_appointment"
        
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
            "content": user_message
        })
        
        # Route to appropriate agent based on intent
        if intent == "schedule_appointment":
            return self._handle_scheduling(user_message, conversation_state)
        elif intent == "get_information":
            return self._handle_information_request(user_message, conversation_state)
        elif intent == "modify_appointment":
            return self._handle_modification_request(user_message, conversation_state)
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
        
        # Process with calendar agent
        result = self.calendar_agent.process_scheduling_request(
            user_message,
            conversation_state["collected_params"],
            conversation_state["required_params"]
        )
        
        # Update conversation state
        conversation_state["collected_params"] = result["collected_params"]
        conversation_state["required_params"] = result["required_params"]
        conversation_state["status"] = result["status"]
        
        # Add agent response to messages
        conversation_state["messages"].append({
            "role": "assistant",
            "content": result["response"]
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
        # For now, provide basic clinic information
        # In Phase 3, this will be handled by a dedicated ClinicInfoAgent
        
        response = "I'd be happy to help you with information about our clinic. What specifically would you like to know? You can ask about our hours, location, services, or insurance plans."
        
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "next_agent": None
        }
    
    def _handle_modification_request(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle appointment modification requests."""
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
    
    def _handle_general_conversation(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general conversation."""
        response = "Hello! I'm your AI medical secretary. I can help you schedule appointments, get information about our clinic, or modify existing appointments. How can I assist you today?"
        
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
