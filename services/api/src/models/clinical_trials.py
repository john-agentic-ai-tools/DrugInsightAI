"""
Clinical trial-related database models.
"""

import enum
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Date, DateTime, Enum, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class TrialPhaseEnum(enum.Enum):
    """Clinical trial phase enumeration."""

    PRECLINICAL = "preclinical"
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"


class TrialStatusEnum(enum.Enum):
    """Clinical trial status enumeration."""

    NOT_YET_RECRUITING = "not_yet_recruiting"
    RECRUITING = "recruiting"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"


class ClinicalTrial(Base):
    """Clinical trial information model."""

    __tablename__ = "clinical_trials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nct_id: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, unique=True, index=True
    )  # NCT number
    title: Mapped[str] = mapped_column(Text, nullable=False)

    # Trial classification
    phase: Mapped[TrialPhaseEnum] = mapped_column(
        Enum(TrialPhaseEnum), nullable=False, index=True
    )
    status: Mapped[TrialStatusEnum] = mapped_column(
        Enum(TrialStatusEnum), nullable=False, index=True
    )

    # Associated entities
    drug_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    sponsor: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Study details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    indication: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    study_type: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # interventional, observational
    study_design: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Enrollment
    enrollment_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enrollment_actual: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timeline
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    primary_completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Geographic information
    locations: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(200)), nullable=True
    )
    countries: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)), nullable=True
    )

    # Study objectives
    primary_endpoints: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    secondary_endpoints: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )

    # Eligibility criteria
    inclusion_criteria: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    exclusion_criteria: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    min_age: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    max_age: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Additional data as JSON for flexibility
    additional_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    drug = relationship("Drug", back_populates="clinical_trials")
    investigators = relationship(
        "TrialInvestigator", back_populates="trial", cascade="all, delete-orphan"
    )
    results = relationship(
        "TrialResult", back_populates="trial", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<ClinicalTrial(id={self.id}, nct_id={self.nct_id}, phase={self.phase})>"
        )


class TrialInvestigator(Base):
    """Trial investigator information model."""

    __tablename__ = "trial_investigators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Investigator details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # principal_investigator, sub_investigator, etc.
    institution: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Contact information
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Location
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    trial = relationship("ClinicalTrial", back_populates="investigators")

    def __repr__(self):
        return f"<TrialInvestigator(trial_id={self.trial_id}, name={self.name})>"


class TrialResult(Base):
    """Trial results and outcomes model."""

    __tablename__ = "trial_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Results overview
    results_posted: Mapped[bool] = mapped_column(nullable=False, default=False)
    results_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Primary outcome results
    primary_outcome_met: Mapped[Optional[bool]] = mapped_column(nullable=True)
    primary_outcome_description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Safety data
    adverse_events_reported: Mapped[Optional[bool]] = mapped_column(nullable=True)
    serious_adverse_events: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    # Efficacy data
    efficacy_endpoints: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    statistical_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Publications
    publications: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )

    # Complete results data as JSON for flexibility
    full_results_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    trial = relationship("ClinicalTrial", back_populates="results")

    def __repr__(self):
        return f"<TrialResult(trial_id={self.trial_id}, results_posted={self.results_posted})>"


# Create indexes for performance
Index("idx_clinical_trials_nct_id", ClinicalTrial.nct_id)
Index("idx_clinical_trials_drug_id", ClinicalTrial.drug_id)
Index("idx_clinical_trials_phase", ClinicalTrial.phase)
Index("idx_clinical_trials_status", ClinicalTrial.status)
Index("idx_clinical_trials_sponsor", ClinicalTrial.sponsor)
Index("idx_clinical_trials_start_date", ClinicalTrial.start_date)
