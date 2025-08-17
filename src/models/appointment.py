"""
Appointment model for the medical secretary system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import Base


class AppointmentStatus(enum.Enum):
    """Appointment status enumeration."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base):
    """Appointment model representing medical appointments."""
    
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_datetime = Column(DateTime, nullable=False, index=True)
    appointment_type = Column(String(255), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, datetime='{self.appointment_datetime}')>"
