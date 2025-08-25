"""
Clinic information tools for querying clinic data.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class ClinicInfoTools:
    """Clinic information tools class for querying clinic data."""
    
    def __init__(self):
        """Initialize clinic info tools."""
        self.clinic_data = self._load_clinic_info()
    
    def _load_clinic_info(self) -> Dict[str, Any]:
        """Load clinic information from JSON file."""
        try:
            config_path = Path(__file__).parent.parent / "config" / "clinic_info.json"
            with open(config_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading clinic info: {e}")
            return {}
    
    def get_clinic_name(self) -> str:
        """Get the clinic name."""
        return self.clinic_data.get("clinic_name", "Medical Clinic")
    
    def get_address(self) -> Dict[str, str]:
        """Get the clinic address."""
        return self.clinic_data.get("address", {})
    
    def get_full_address(self) -> str:
        """Get the full formatted address."""
        address = self.get_address()
        if not address:
            return "Address not available"
        
        parts = [
            address.get("street", ""),
            address.get("city", ""),
            address.get("state", ""),
            address.get("zip_code", ""),
            address.get("country", "")
        ]
        
        return ", ".join(filter(None, parts))
    
    def get_contact_info(self) -> Dict[str, str]:
        """Get contact information."""
        return self.clinic_data.get("contact", {})
    
    def get_phone_number(self) -> str:
        """Get the main phone number."""
        return self.clinic_data.get("contact", {}).get("phone", "Phone not available")
    
    def get_emergency_contact(self) -> str:
        """Get emergency contact number."""
        return self.clinic_data.get("contact", {}).get("emergency", "Emergency contact not available")
    
    def get_opening_hours(self) -> Dict[str, str]:
        """Get opening hours for all days."""
        return self.clinic_data.get("hours", {})
    
    def get_hours_for_day(self, day: str) -> str:
        """Get opening hours for a specific day."""
        day_lower = day.lower()
        hours = self.clinic_data.get("hours", {})
        
        # Handle different day formats
        if day_lower in hours:
            return hours[day_lower]
        elif day_lower == "mon" and "monday" in hours:
            return hours["monday"]
        elif day_lower == "tue" and "tuesday" in hours:
            return hours["tuesday"]
        elif day_lower == "wed" and "wednesday" in hours:
            return hours["wednesday"]
        elif day_lower == "thu" and "thursday" in hours:
            return hours["thursday"]
        elif day_lower == "fri" and "friday" in hours:
            return hours["friday"]
        elif day_lower == "sat" and "saturday" in hours:
            return hours["saturday"]
        elif day_lower == "sun" and "sunday" in hours:
            return hours["sunday"]
        
        return "Hours not available for this day"
    
    def get_services(self) -> List[str]:
        """Get list of available services."""
        return self.clinic_data.get("services", [])
    
    def check_service_available(self, service_name: str) -> bool:
        """Check if a specific service is available."""
        services = self.get_services()
        return any(service.lower() in service_name.lower() for service in services)
    
    def get_specialties(self) -> List[Dict[str, Any]]:
        """Get list of medical specialties."""
        return self.clinic_data.get("specialties", [])
    
    def get_specialty_by_name(self, specialty_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific specialty by name."""
        specialties = self.get_specialties()
        for specialty in specialties:
            if specialty["name"].lower() == specialty_name.lower():
                return specialty
        return None
    
    def get_doctors_by_specialty(self, specialty_name: str) -> List[str]:
        """Get doctors for a specific specialty."""
        specialty = self.get_specialty_by_name(specialty_name)
        if specialty:
            return specialty.get("doctors", [])
        return []
    
    def get_all_doctors(self) -> List[str]:
        """Get all doctors across all specialties."""
        doctors = []
        specialties = self.get_specialties()
        for specialty in specialties:
            doctors.extend(specialty.get("doctors", []))
        return list(set(doctors))  # Remove duplicates
    
    def get_insurance_plans(self) -> List[str]:
        """Get list of accepted insurance plans."""
        return self.clinic_data.get("insurance_plans", [])
    
    def check_insurance_accepted(self, insurance_name: str) -> bool:
        """Check if a specific insurance plan is accepted."""
        plans = self.get_insurance_plans()
        return any(plan.lower() in insurance_name.lower() for plan in plans)
    
    def get_facilities(self) -> List[str]:
        """Get list of available facilities."""
        return self.clinic_data.get("facilities", [])
    
    def get_policies(self) -> Dict[str, str]:
        """Get clinic policies."""
        return self.clinic_data.get("policies", {})
    
    def get_policy(self, policy_name: str) -> str:
        """Get a specific policy."""
        policies = self.get_policies()
        return policies.get(policy_name, "Policy not available")
    
    def get_covid_info(self) -> Dict[str, Any]:
        """Get COVID-19 related information."""
        return self.clinic_data.get("covid_19", {})
    
    def search_clinic_info(self, query: str) -> List[Dict[str, Any]]:
        """Search clinic information for a specific query."""
        query_lower = query.lower()
        results = []
        
        # Search in services
        services = self.get_services()
        for service in services:
            if query_lower in service.lower():
                results.append({
                    "type": "service",
                    "content": service,
                    "category": "Services"
                })
        
        # Search in specialties
        specialties = self.get_specialties()
        for specialty in specialties:
            if (query_lower in specialty["name"].lower() or 
                query_lower in specialty["description"].lower()):
                results.append({
                    "type": "specialty",
                    "content": specialty,
                    "category": "Specialties"
                })
        
        # Search in insurance plans
        insurance_plans = self.get_insurance_plans()
        for plan in insurance_plans:
            if query_lower in plan.lower():
                results.append({
                    "type": "insurance",
                    "content": plan,
                    "category": "Insurance"
                })
        
        # Search in facilities
        facilities = self.get_facilities()
        for facility in facilities:
            if query_lower in facility.lower():
                results.append({
                    "type": "facility",
                    "content": facility,
                    "category": "Facilities"
                })
        
        return results
    
    def get_clinic_summary(self) -> str:
        """Get a summary of clinic information."""
        name = self.get_clinic_name()
        address = self.get_full_address()
        phone = self.get_phone_number()
        hours = self.get_hours_for_day("monday")  # Use Monday as example
        
        summary = f"{name}\n"
        summary += f"Address: {address}\n"
        summary += f"Phone: {phone}\n"
        summary += f"Hours: {hours}\n"
        summary += f"Services: {', '.join(self.get_services()[:5])}...\n"
        summary += f"Specialties: {', '.join([s['name'] for s in self.get_specialties()[:3]])}..."
        
        return summary
