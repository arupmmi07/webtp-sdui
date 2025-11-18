"""Workflow state and result models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from .appointment import Appointment
from .patient import Patient
from .provider import Provider


class WorkflowStage(str, Enum):
    """Workflow stages."""
    TRIGGER = "trigger"
    FILTERING = "filtering"
    SCORING = "scoring"
    CONSENT = "consent"
    BACKFILL = "backfill"
    AUDIT = "audit"
    COMPLETE = "complete"


class WorkflowStatus(str, Enum):
    """Overall workflow status."""
    IN_PROGRESS = "in_progress"
    BOOKED = "booked"
    RESCHEDULED = "rescheduled"
    HOD_ASSIGNED = "hod_assigned"
    MANUAL_REVIEW = "manual_review"
    FAILED = "failed"


@dataclass
class Candidate:
    """Provider candidate with score."""
    provider: Provider
    score: float
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    rank: int = 0


@dataclass
class TriggerResult:
    """Result from trigger stage."""
    therapist_id: str
    therapist_name: str
    affected_appointments: List[Appointment] = field(default_factory=list)
    total_count: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FilterResult:
    """Result from filtering stage."""
    appointment_id: str
    candidates_initial: int = 0
    candidates_qualified: int = 0
    qualified_provider_ids: List[str] = field(default_factory=list)
    filters_applied: Dict[str, Dict[str, int]] = field(default_factory=dict)  # filter_name -> {passed, failed}
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScoringResult:
    """Result from scoring stage."""
    appointment_id: str
    ranked_candidates: List[Candidate] = field(default_factory=list)
    scoring_model_version: str = "v1.0"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConsentResult:
    """Result from consent stage."""
    appointment_id: str
    offered_provider_id: str
    offered_provider_name: str
    communication_channel: str
    message_id: str
    response: Optional[str] = None  # "YES", "NO", "INFO", "TIMEOUT"
    response_time_minutes: Optional[int] = None
    final_provider_id: Optional[str] = None
    status: str = "pending"  # "booked", "declined", "timeout"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BackfillResult:
    """Result from backfill stage."""
    appointment_id: str
    freed_slot_date: Optional[datetime] = None
    freed_slot_filled: bool = False
    filled_with_patient_id: Optional[str] = None
    original_patient_rescheduled: bool = False
    new_appointment_date: Optional[datetime] = None
    new_provider_id: Optional[str] = None
    hod_assigned: bool = False
    manual_review_required: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowState:
    """State that flows through the workflow."""
    session_id: str
    appointment: Appointment
    patient: Patient
    available_providers: List[Provider] = field(default_factory=list)
    
    # Stage results
    trigger_result: Optional[TriggerResult] = None
    filter_result: Optional[FilterResult] = None
    scoring_result: Optional[ScoringResult] = None
    consent_result: Optional[ConsentResult] = None
    backfill_result: Optional[BackfillResult] = None
    
    # Current state
    current_stage: WorkflowStage = WorkflowStage.TRIGGER
    status: WorkflowStatus = WorkflowStatus.IN_PROGRESS
    
    # Workflow control
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    
    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def get_duration_minutes(self) -> Optional[int]:
        """Get workflow duration in minutes."""
        if self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() / 60)
        return None
    
    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.current_stage == WorkflowStage.COMPLETE
    
    def mark_complete(self, status: WorkflowStatus):
        """Mark workflow as complete."""
        self.current_stage = WorkflowStage.COMPLETE
        self.status = status
        self.completed_at = datetime.now()


@dataclass
class AuditLogEntry:
    """Single audit log entry."""
    timestamp: datetime
    stage: WorkflowStage
    event_type: str
    appointment_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    duration_seconds: Optional[float] = None


@dataclass
class AuditLog:
    """Complete audit log for a session."""
    session_id: str
    session_start: datetime
    session_end: Optional[datetime] = None
    total_duration_minutes: Optional[int] = None
    
    # Trigger information
    trigger: Dict[str, Any] = field(default_factory=dict)
    
    # Per-appointment logs
    appointments: List[Dict[str, Any]] = field(default_factory=list)
    
    # Session summary
    summary: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance
    compliance_audit: Dict[str, Any] = field(default_factory=dict)
    
    def add_entry(self, entry: AuditLogEntry):
        """Add an entry to the appropriate appointment log."""
        # Find or create appointment entry
        appt_log = next(
            (a for a in self.appointments if a.get("appointment_id") == entry.appointment_id),
            None
        )
        if not appt_log:
            appt_log = {
                "appointment_id": entry.appointment_id,
                "workflow_stages": []
            }
            self.appointments.append(appt_log)
        
        # Add stage entry
        stage_entry = {
            "stage": entry.stage.value,
            "timestamp": entry.timestamp.isoformat(),
            "event_type": entry.event_type,
            "data": entry.data
        }
        if entry.duration_seconds is not None:
            stage_entry["duration_seconds"] = entry.duration_seconds
        
        appt_log["workflow_stages"].append(stage_entry)
    
    def finalize(self):
        """Finalize the audit log with summary statistics."""
        self.session_end = datetime.now()
        if self.session_start:
            duration = (self.session_end - self.session_start).total_seconds() / 60
            self.total_duration_minutes = int(duration)
        
        # Calculate summary stats
        total = len(self.appointments)
        booked = sum(1 for a in self.appointments if a.get("final_status") == "BOOKED")
        rescheduled = sum(1 for a in self.appointments if a.get("final_status") == "RESCHEDULED")
        hod = sum(1 for a in self.appointments if a.get("final_status") == "HOD_ASSIGNED")
        manual = sum(1 for a in self.appointments if a.get("manual_intervention_required"))
        
        self.summary = {
            "total_appointments": total,
            "outcomes": {
                "booked": booked,
                "rescheduled": rescheduled,
                "hod_assigned": hod,
                "pending": total - booked - rescheduled - hod
            },
            "success_rate": (booked + rescheduled) / total if total > 0 else 0,
            "manual_interventions_required": manual
        }

