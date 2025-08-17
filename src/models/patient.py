"""
Patient model for the medical secretary system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Patient(Base):
    """Patient model representing clinic patients."""
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), nullable=False, unique=True)
    date_of_birth = Column(DateTime, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name='{self.name}', phone='{self.phone}')>"
