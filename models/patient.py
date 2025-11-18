"""Patient data models."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CommunicationChannel(str, Enum):
    """Preferred communication channels."""
    SMS = "sms"
    EMAIL = "email"
    IVR = "ivr"
    PHONE = "phone"


class InsuranceType(str, Enum):
    """Insurance/payer types."""
    MEDICARE = "medicare"
    MEDICARE_ADVANTAGE = "medicare_advantage"
    PPO = "ppo"
    HMO = "hmo"
    WORKERS_COMP = "workers_comp"
    CASH_PAY = "cash_pay"


@dataclass
class PatientPreferences:
    """Patient preferences for provider and scheduling."""
    gender_preference: Optional[str] = None  # "female", "male", "no_preference"
    preferred_days: List[str] = field(default_factory=list)  # ["monday", "tuesday", ...]
    preferred_times: List[str] = field(default_factory=list)  # ["morning", "afternoon", "evening"]
    location_preference: Optional[str] = None  # Clinic name or location
    max_distance_miles: float = 10.0
    language: str = "english"
    communication_channel_primary: CommunicationChannel = CommunicationChannel.SMS
    communication_channel_secondary: CommunicationChannel = CommunicationChannel.EMAIL
    telehealth_acceptable: bool = False


@dataclass
class PatientHistory:
    """Patient appointment and no-show history."""
    total_appointments: int = 0
    completed_appointments: int = 0
    no_shows: int = 0
    cancellations: int = 0
    no_show_rate: float = 0.0  # Calculated: no_shows / total_appointments
    last_appointment_date: Optional[datetime] = None
    prior_providers: List[str] = field(default_factory=list)  # Provider IDs


@dataclass
class Patient:
    """Patient model with complete profile."""
    patient_id: str
    name: str
    age: int
    gender: str
    
    # Contact information
    phone: str
    email: str
    address: Optional[str] = None
    
    # Insurance information
    insurance_type: InsuranceType = InsuranceType.CASH_PAY
    insurance_plan: Optional[str] = None
    insurance_id: Optional[str] = None
    
    # Clinical information
    condition: str = ""
    chief_complaint: Optional[str] = None
    diagnosis_code: Optional[str] = None
    
    # Plan of Care (POC) information
    poc_active: bool = False
    poc_expiration_date: Optional[datetime] = None
    poc_approved_providers: List[str] = field(default_factory=list)  # Provider IDs
    poc_remaining_visits: Optional[int] = None
    
    # History and risk
    history: PatientHistory = field(default_factory=PatientHistory)
    no_show_risk: float = 0.0  # 0.0-1.0 (calculated)
    
    # Preferences
    preferences: PatientPreferences = field(default_factory=PatientPreferences)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def calculate_no_show_risk(self) -> float:
        """Calculate no-show risk based on history."""
        if self.history.total_appointments == 0:
            return 0.3  # Default moderate risk for new patients
        
        # Base risk from no-show rate
        base_risk = self.history.no_show_rate
        
        # Adjust for recent activity
        if self.history.last_appointment_date:
            days_since_last = (datetime.now() - self.history.last_appointment_date).days
            if days_since_last > 180:
                base_risk += 0.1  # Increase risk if long time since last visit
        
        # Adjust for total appointments (more history = more reliable)
        if self.history.total_appointments < 5:
            base_risk += 0.1  # Less history = less predictable
        
        # Cap at 1.0
        return min(base_risk, 1.0)
    
    def is_poc_valid(self) -> bool:
        """Check if Plan of Care is active and not expired."""
        if not self.poc_active:
            return False
        if self.poc_expiration_date and datetime.now() > self.poc_expiration_date:
            return False
        if self.poc_remaining_visits is not None and self.poc_remaining_visits <= 0:
            return False
        return True
    
    def is_poc_urgent(self, days_threshold: int = 7) -> bool:
        """Check if POC is expiring soon."""
        if not self.poc_active or not self.poc_expiration_date:
            return False
        days_remaining = (self.poc_expiration_date - datetime.now()).days
        return 0 < days_remaining <= days_threshold

