"""Abstract risk calculator interface."""

from abc import ABC, abstractmethod
from models.patient import Patient, PatientHistory
from models.appointment import Appointment


class RiskCalculator(ABC):
    """
    Abstract base class for risk calculation.
    
    Calculates no-show risk and other risk metrics for patients.
    """
    
    @abstractmethod
    def calculate_no_show_risk(self, patient: Patient, appointment: Appointment) -> float:
        """
        Calculate no-show risk for a patient and appointment.
        
        Args:
            patient: Patient data
            appointment: Appointment data
        
        Returns:
            Risk score between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def calculate_priority_score(
        self,
        appointment: Appointment,
        patient: Patient,
        no_show_risk: float
    ) -> float:
        """
        Calculate priority score for appointment reassignment.
        
        Args:
            appointment: Appointment data
            patient: Patient data
            no_show_risk: Pre-calculated no-show risk
        
        Returns:
            Priority score (higher = more urgent)
        """
        pass
    
    @abstractmethod
    def get_priority_level(self, priority_score: float) -> str:
        """
        Convert priority score to level (high/medium/low).
        
        Args:
            priority_score: Calculated priority score
        
        Returns:
            Priority level string
        """
        pass

