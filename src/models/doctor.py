"""
Doctor model for the medical secretary system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Doctor(Base):
    """Doctor model representing clinic doctors."""
    
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), nullable=True)
    specialty = Column(String(255), nullable=True)
    license_number = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
    
    def __repr__(self):
        return f"<Doctor(id={self.id}, name='{self.name}', specialty='{self.specialty}')>"
