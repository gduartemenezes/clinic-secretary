"""
Clinic Information Agent for answering general clinic questions.
"""

from typing import Dict, Any, List, Optional
from src.tools.clinic_info_tools import ClinicInfoTools


class ClinicInfoAgent:
    """Clinic Information Agent for handling general clinic questions."""
    
    def __init__(self, clinic_info_tools: ClinicInfoTools):
        """Initialize the Clinic Information Agent."""
        self.clinic_tools = clinic_info_tools
    
    def process_information_request(
        self,
        user_message: str,
        conversation_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process an information request from the user."""
        # Extract the type of information being requested
        info_type = self._detect_information_type(user_message)
        
        # Generate appropriate response based on information type
        response = self._generate_information_response(user_message, info_type)
        
        # Update conversation state
        conversation_state["messages"].append({
            "role": "user",
            "content": user_message
        })
        conversation_state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "conversation_state": conversation_state,
            "info_type": info_type,
            "status": "completed"
        }
    
    def _detect_information_type(self, user_message: str) -> str:
        """Detect what type of information the user is requesting."""
        message_lower = user_message.lower()
        
        # Check for specific information types
        if any(word in message_lower for word in ["address", "location", "where"]):
            return "address"
        elif any(word in message_lower for word in ["phone", "call", "contact", "number"]):
            return "contact"
        elif any(word in message_lower for word in ["hours", "open", "close", "time", "schedule"]):
            return "hours"
        elif any(word in message_lower for word in ["service", "offer", "provide", "available"]):
            return "services"
        elif any(word in message_lower for word in ["doctor", "physician", "specialist", "specialty"]):
            return "doctors"
        elif any(word in message_lower for word in ["insurance", "plan", "cover", "accept"]):
            return "insurance"
        elif any(word in message_lower for word in ["policy", "rule", "procedure", "requirement"]):
            return "policies"
        elif any(word in message_lower for word in ["covid", "vaccine", "test", "safety"]):
            return "covid"
        elif any(word in message_lower for word in ["facility", "equipment", "room", "lab"]):
            return "facilities"
        else:
            return "general"
    
    def _generate_information_response(self, user_message: str, info_type: str) -> str:
        """Generate a response based on the information type requested."""
        message_lower = user_message.lower()
        
        if info_type == "address":
            return self._get_address_response()
        elif info_type == "contact":
            return self._get_contact_response()
        elif info_type == "hours":
            return self._get_hours_response(message_lower)
        elif info_type == "services":
            return self._get_services_response(message_lower)
        elif info_type == "doctors":
            return self._get_doctors_response(message_lower)
        elif info_type == "insurance":
            return self._get_insurance_response(message_lower)
        elif info_type == "policies":
            return self._get_policies_response(message_lower)
        elif info_type == "covid":
            return self._get_covid_response()
        elif info_type == "facilities":
            return self._get_facilities_response()
        else:
            return self._get_general_response()
    
    def _get_address_response(self) -> str:
        """Generate address response."""
        address = self.clinic_tools.get_full_address()
        return f"Our clinic is located at: {address}"
    
    def _get_contact_response(self) -> str:
        """Generate contact response."""
        phone = self.clinic_tools.get_phone_number()
        emergency = self.clinic_tools.get_emergency_contact()
        
        response = f"You can reach us at: {phone}\n"
        response += f"For emergencies, please call: {emergency}"
        return response
    
    def _get_hours_response(self, message: str) -> str:
        """Generate hours response."""
        # Check if asking for specific day
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in message:
                hours = self.clinic_tools.get_hours_for_day(day)
                return f"Our hours for {day.title()} are: {hours}"
        
        # General hours response
        hours = self.clinic_tools.get_opening_hours()
        response = "Our clinic hours are:\n"
        for day, time in hours.items():
            response += f"{day.title()}: {time}\n"
        return response
    
    def _get_services_response(self, message: str) -> str:
        """Generate services response."""
        services = self.clinic_tools.get_services()
        
        # Check if asking about specific service
        for service in services:
            if service.lower() in message:
                return f"Yes, we do offer {service}. This service is available at our clinic."
        
        # General services response
        response = "We offer the following services:\n"
        for service in services:
            response += f"• {service}\n"
        response += "\nIs there a specific service you'd like to know more about?"
        return response
    
    def _get_doctors_response(self, message: str) -> str:
        """Generate doctors response."""
        # Check if asking about specific specialty
        specialties = self.clinic_tools.get_specialties()
        for specialty in specialties:
            if specialty["name"].lower() in message:
                doctors = specialty["doctors"]
                response = f"Our {specialty['name']} specialists are:\n"
                for doctor in doctors:
                    response += f"• {doctor}\n"
                response += f"\n{specialty['description']}"
                return response
        
        # General doctors response
        all_doctors = self.clinic_tools.get_all_doctors()
        response = "We have specialists in various fields:\n"
        for specialty in specialties[:3]:  # Show first 3 specialties
            response += f"• {specialty['name']}: {', '.join(specialty['doctors'])}\n"
        response += "\nWhat type of specialist are you looking for?"
        return response
    
    def _get_insurance_response(self, message: str) -> str:
        """Generate insurance response."""
        insurance_plans = self.clinic_tools.get_insurance_plans()
        
        # Check if asking about specific insurance
        for plan in insurance_plans:
            if plan.lower() in message:
                return f"Yes, we do accept {plan}. Please bring your insurance card to your appointment."
        
        # General insurance response
        response = "We accept most major insurance plans including:\n"
        for plan in insurance_plans[:6]:  # Show first 6 plans
            response += f"• {plan}\n"
        response += "\nPlease contact us to verify your specific insurance coverage."
        return response
    
    def _get_policies_response(self, message: str) -> str:
        """Generate policies response."""
        policies = self.clinic_tools.get_policies()
        
        # Check if asking about specific policy
        for policy_name, policy_desc in policies.items():
            if policy_name.lower().replace("_", " ") in message:
                return f"Our {policy_name.replace('_', ' ')} policy: {policy_desc}"
        
        # General policies response
        response = "Here are some of our key policies:\n"
        for policy_name, policy_desc in policies.items():
            response += f"• {policy_name.replace('_', ' ').title()}: {policy_desc}\n"
        return response
    
    def _get_covid_response(self) -> str:
        """Generate COVID-19 response."""
        covid_info = self.clinic_tools.get_covid_info()
        
        response = "COVID-19 Information:\n"
        if covid_info.get("vaccination_available"):
            response += "• Vaccinations are available\n"
        if covid_info.get("testing_available"):
            response += "• Testing is available\n"
        
        response += "\nSafety measures:\n"
        for measure in covid_info.get("safety_measures", []):
            response += f"• {measure}\n"
        
        return response
    
    def _get_facilities_response(self) -> str:
        """Generate facilities response."""
        facilities = self.clinic_tools.get_facilities()
        
        response = "Our clinic features:\n"
        for facility in facilities:
            response += f"• {facility}\n"
        return response
    
    def _get_general_response(self) -> str:
        """Generate general information response."""
        summary = self.clinic_tools.get_clinic_summary()
        response = f"Here's some general information about our clinic:\n\n{summary}\n\n"
        response += "What specific information would you like to know? I can help with:\n"
        response += "• Address and location\n"
        response += "• Contact information\n"
        response += "• Hours of operation\n"
        response += "• Available services\n"
        response += "• Doctors and specialties\n"
        response += "• Insurance plans\n"
        response += "• Clinic policies\n"
        response += "• COVID-19 information"
        return response
    
    def search_clinic_info(self, query: str) -> List[Dict[str, Any]]:
        """Search clinic information for a specific query."""
        return self.clinic_tools.search_clinic_info(query)
    
    def get_clinic_summary(self) -> str:
        """Get a summary of clinic information."""
        return self.clinic_tools.get_clinic_summary()
