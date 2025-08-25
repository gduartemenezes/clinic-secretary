"""
Database tools for appointment management.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment, AppointmentStatus


class DatabaseTools:
    """Database tools class for appointment operations."""
    
    def __init__(self, db_session: Session):
        """Initialize database tools with a session."""
        self.db = db_session
    
    def create_appointment(
        self,
        patient_id: int,
        doctor_id: int,
        appointment_datetime: datetime,
        appointment_type: str,
        notes: Optional[str] = None
    ) -> Appointment:
        """Create a new appointment."""
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_datetime,
            appointment_type=appointment_type,
            notes=notes,
            status=AppointmentStatus.SCHEDULED
        )
        
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        
        return appointment
    
    def get_appointment_details(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment details by ID."""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    def check_doctor_availability(
        self,
        doctor_id: int,
        appointment_datetime: datetime,
        duration_minutes: int = 60
    ) -> bool:
        """Check if a doctor is available at a specific time."""
        end_time = appointment_datetime + timedelta(minutes=duration_minutes)
        
        # Check for overlapping appointments
        conflicting_appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                or_(
                    and_(
                        Appointment.appointment_datetime < end_time,
                        Appointment.appointment_datetime >= appointment_datetime
                    ),
                    and_(
                        Appointment.appointment_datetime <= appointment_datetime,
                        Appointment.appointment_datetime + timedelta(minutes=60) > appointment_datetime
                    )
                )
            )
        ).count()
        
        return conflicting_appointments == 0
    
    def get_doctor_schedule(
        self,
        doctor_id: int,
        date: datetime
    ) -> List[Appointment]:
        """Get a doctor's schedule for a specific date."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_datetime >= start_of_day,
                Appointment.appointment_datetime < end_of_day,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).order_by(Appointment.appointment_datetime).all()
    
    def get_patient_appointments(
        self,
        patient_id: int,
        status: Optional[AppointmentStatus] = None
    ) -> List[Appointment]:
        """Get appointments for a specific patient."""
        query = self.db.query(Appointment).filter(Appointment.patient_id == patient_id)
        
        if status:
            query = query.filter(Appointment.status == status)
        
        return query.order_by(Appointment.appointment_datetime).all()
    
    def update_appointment_status(
        self,
        appointment_id: int,
        new_status: AppointmentStatus
    ) -> Optional[Appointment]:
        """Update appointment status."""
        appointment = self.get_appointment_details(appointment_id)
        if appointment:
            appointment.status = new_status
            appointment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(appointment)
        
        return appointment
    
    def update_appointment_datetime(
        self,
        appointment_id: int,
        new_datetime: datetime
    ) -> Optional[Appointment]:
        """Update appointment date and time."""
        appointment = self.get_appointment_details(appointment_id)
        if appointment:
            appointment.appointment_datetime = new_datetime
            appointment.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(appointment)
        
        return appointment
    
    def cancel_appointment(self, appointment_id: int) -> Optional[Appointment]:
        """Cancel an appointment (update status to cancelled)."""
        return self.update_appointment_status(appointment_id, AppointmentStatus.CANCELLED)
    
    def get_appointments_by_date(self, date: datetime) -> List[Appointment]:
        """Get all appointments for a specific date."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_datetime >= start_of_day,
                Appointment.appointment_datetime < end_of_day
            )
        ).order_by(Appointment.appointment_datetime).all()
    
    def get_appointments_by_doctor_and_date(
        self,
        doctor_id: int,
        date: datetime
    ) -> List[Appointment]:
        """Get appointments for a specific doctor on a specific date."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_datetime >= start_of_day,
                Appointment.appointment_datetime < end_of_day
            )
        ).order_by(Appointment.appointment_datetime).all()
    
    def get_upcoming_appointments(
        self,
        days_ahead: int = 7
    ) -> List[Appointment]:
        """Get upcoming appointments within specified days."""
        now = datetime.utcnow()
        end_date = now + timedelta(days=days_ahead)
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_datetime >= now,
                Appointment.appointment_datetime <= end_date,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).order_by(Appointment.appointment_datetime).all()
    
    def get_appointments_for_reminders(
        self,
        hours_ahead: int = 24
    ) -> List[Appointment]:
        """Get appointments that need reminders sent."""
        now = datetime.utcnow()
        reminder_time = now + timedelta(hours=hours_ahead)
        
        return self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_datetime >= now,
                Appointment.appointment_datetime <= reminder_time,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
            )
        ).order_by(Appointment.appointment_datetime).all()
    
    def get_appointments_by_patient(
        self,
        patient_name: str,
        patient_phone: str
    ) -> List[Appointment]:
        """Get appointments for a specific patient by name and phone."""
        # First find the patient by name and phone
        patient = self.db.query(Patient).filter(
            and_(
                Patient.name.ilike(f"%{patient_name}%"),
                Patient.phone.ilike(f"%{patient_phone}%")
            )
        ).first()
        
        if not patient:
            return []
        
        # Get appointments for this patient
        return self.get_patient_appointments(patient.id)
    
    def search_appointments(
        self,
        patient_name: Optional[str] = None,
        doctor_name: Optional[str] = None,
        appointment_type: Optional[str] = None,
        status: Optional[AppointmentStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Appointment]:
        """Search appointments with multiple criteria."""
        query = self.db.query(Appointment)
        
        if patient_name:
            # This would need to join with Patient table in a real implementation
            pass
        
        if doctor_name:
            # This would need to join with Doctor table in a real implementation
            pass
        
        if appointment_type:
            query = query.filter(Appointment.appointment_type.ilike(f"%{appointment_type}%"))
        
        if status:
            query = query.filter(Appointment.status == status)
        
        if date_from:
            query = query.filter(Appointment.appointment_datetime >= date_from)
        
        if date_to:
            query = query.filter(Appointment.appointment_datetime <= date_to)
        
        return query.order_by(Appointment.appointment_datetime).all()
    
    def get_appointment_statistics(self) -> Dict[str, Any]:
        """Get appointment statistics."""
        total_appointments = self.db.query(Appointment).count()
        
        status_counts = {}
        for status in AppointmentStatus:
            count = self.db.query(Appointment).filter(Appointment.status == status).count()
            status_counts[status.value] = count
        
        today = datetime.utcnow().date()
        today_appointments = self.db.query(Appointment).filter(
            Appointment.appointment_datetime >= today,
            Appointment.appointment_datetime < today + timedelta(days=1)
        ).count()
        
        return {
            "total_appointments": total_appointments,
            "status_counts": status_counts,
            "today_appointments": today_appointments
        }
