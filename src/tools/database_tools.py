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
