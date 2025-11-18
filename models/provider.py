"""Provider data models."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, time
from enum import Enum


class ProviderSpecialty(str, Enum):
    """Provider specializations."""
    ORTHOPEDIC = "orthopedic"
    SPORTS_MEDICINE = "sports_medicine"
    NEUROLOGICAL = "neurological"
    PEDIATRIC = "pediatric"
    GERIATRIC = "geriatric"
    GENERAL = "general"


@dataclass
class ProviderSkills:
    """Provider certifications and skills."""
    specializations: List[ProviderSpecialty] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)  # e.g., ["Board Certified", "Manual Therapy"]
    license_number: str = ""
    license_states: List[str] = field(default_factory=list)
    license_active: bool = True
    hospital_privileges: bool = False
    npi_number: Optional[str] = None  # National Provider Identifier
    years_experience: int = 0


@dataclass
class ProviderAvailability:
    """Provider schedule and availability."""
    available_days: List[str] = field(default_factory=list)  # ["monday", "tuesday", ...]
    available_times: Dict[str, List[tuple[time, time]]] = field(default_factory=dict)  # day -> [(start, end), ...]
    telehealth_available: bool = False
    in_person_available: bool = True
    clinic_locations: List[str] = field(default_factory=list)


@dataclass
class Provider:
    """Provider model with complete profile."""
    provider_id: str
    name: str
    age: int
    gender: str
    
    # Skills and qualifications
    skills: ProviderSkills = field(default_factory=ProviderSkills)
    
    # Availability and schedule
    availability: ProviderAvailability = field(default_factory=ProviderAvailability)
    
    # Capacity and load
    current_patient_load: int = 0
    max_patient_capacity: int = 25
    
    # Accepted insurances
    accepted_insurances: List[str] = field(default_factory=list)  # Insurance types accepted
    medicare_approved: bool = False
    medicaid_approved: bool = False
    
    # Contact and location
    email: str = ""
    phone: str = ""
    primary_location: str = ""
    
    # Status
    active: bool = True
    available_for_new_patients: bool = True
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def is_at_capacity(self) -> bool:
        """Check if provider is at or over capacity."""
        return self.current_patient_load >= self.max_patient_capacity
    
    def get_capacity_utilization(self) -> float:
        """Get capacity utilization as percentage (0.0-1.0)."""
        if self.max_patient_capacity == 0:
            return 1.0
        return min(self.current_patient_load / self.max_patient_capacity, 1.0)
    
    def has_specialty(self, specialty: ProviderSpecialty) -> bool:
        """Check if provider has a specific specialty."""
        return specialty in self.skills.specializations
    
    def accepts_insurance(self, insurance_type: str) -> bool:
        """Check if provider accepts a specific insurance type."""
        return insurance_type.lower() in [ins.lower() for ins in self.accepted_insurances]
    
    def is_available_on_day(self, day: str) -> bool:
        """Check if provider is available on a specific day."""
        return day.lower() in [d.lower() for d in self.availability.available_days]

