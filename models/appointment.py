"""Appointment data models."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment statuses."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELED = "canceled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, Enum):
    """Types of appointments."""
    INITIAL_EVALUATION = "initial_evaluation"
    FOLLOW_UP = "follow_up"
    RE_EVALUATION = "re_evaluation"


@dataclass
class Appointment:
    """Appointment model."""
    appointment_id: str
    patient_id: str
    provider_id: str
    
    # Scheduling
    appointment_date: datetime
    duration_minutes: int = 60
    appointment_type: AppointmentType = AppointmentType.FOLLOW_UP
    
    # Status
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    
    # Clinical
    condition: str = ""
    treatment_type: Optional[str] = None
    notes: str = ""
    
    # Location
    clinic_location: str = ""
    is_telehealth: bool = False
    
    # Insurance/Authorization
    insurance_authorization_number: Optional[str] = None
    insurance_authorization_required: bool = False
    insurance_authorized: bool = False
    
    # Revenue
    estimated_revenue: float = 0.0
    copay_amount: float = 0.0
    
    # Priority (calculated during trigger)
    priority_score: float = 0.0
    priority_level: str = "standard"  # "high", "medium", "low", "standard"
    
    # Original provider (for reassignment tracking)
    original_provider_id: Optional[str] = None
    reassignment_reason: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    def get_day_of_week(self) -> str:
        """Get day of week for appointment."""
        return self.appointment_date.strftime("%A").lower()
    
    def get_time_of_day(self) -> str:
        """Get time of day category."""
        hour = self.appointment_date.hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
    
    def is_within_days(self, days: int) -> bool:
        """Check if appointment is within specified number of days."""
        days_until = (self.appointment_date - datetime.now()).days
        return 0 <= days_until <= days

