"""
Drug-related database models.
"""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class DrugStatusEnum(enum.Enum):
    """Drug development status enumeration."""

    DISCOVERY = "discovery"
    PRECLINICAL = "preclinical"
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    APPROVED = "approved"
    WITHDRAWN = "withdrawn"
    DISCONTINUED = "discontinued"


class NewDrugEntryTypeEnum(enum.Enum):
    """New drug entry type enumeration."""

    NEW_CHEMICAL_ENTITY = "new_chemical_entity"
    NEW_FORMULATION = "new_formulation"
    NEW_ROUTE = "new_route"
    NEW_DOSAGE = "new_dosage"
    NEW_GENERIC = "new_generic"
    NEW_COMBINATION = "new_combination"
    NEW_INDICATION = "new_indication"


class Drug(Base):
    """Main drug information model."""

    __tablename__ = "drugs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    generic_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, index=True
    )
    status: Mapped[DrugStatusEnum] = mapped_column(
        Enum(DrugStatusEnum), nullable=False, index=True
    )
    therapeutic_area: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    indication: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Company relationship
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )

    # Drug details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mechanism_of_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    dosage_form: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    route_of_administration: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    target_population: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Market information
    market_size: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    approval_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    regulatory_statuses = relationship(
        "DrugRegulatoryStatus", back_populates="drug", cascade="all, delete-orphan"
    )
    patents = relationship(
        "DrugPatent", back_populates="drug", cascade="all, delete-orphan"
    )
    new_entries = relationship(
        "NewDrugEntry", back_populates="drug", cascade="all, delete-orphan"
    )
    analytics = relationship(
        "DrugAnalytics", back_populates="drug", cascade="all, delete-orphan"
    )
    adverse_events = relationship(
        "AdverseEvent", back_populates="drug", cascade="all, delete-orphan"
    )
    clinical_trials = relationship(
        "ClinicalTrial", back_populates="drug", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Drug(id={self.id}, name={self.name}, status={self.status})>"


class DrugRegulatoryStatus(Base):
    """Drug regulatory status by different authorities."""

    __tablename__ = "drug_regulatory_status"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, index=True
    )
    authority: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # FDA, EMA, PMDA, etc.
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    approval_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    application_number: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    drug = relationship("Drug", back_populates="regulatory_statuses")

    def __repr__(self):
        return f"<DrugRegulatoryStatus(drug_id={self.drug_id}, authority={self.authority})>"


class DrugPatent(Base):
    """Drug patent information."""

    __tablename__ = "drug_patents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, index=True
    )
    patent_number: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    patent_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # composition, method, formulation, etc.
    filing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    grant_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # active, expired, pending
    jurisdiction: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # US, EU, etc.

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    drug = relationship("Drug", back_populates="patents")

    def __repr__(self):
        return (
            f"<DrugPatent(drug_id={self.drug_id}, patent_number={self.patent_number})>"
        )


class NewDrugEntry(Base):
    """Tracks new drug entries and changes."""

    __tablename__ = "new_drug_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, index=True
    )
    entry_type: Mapped[NewDrugEntryTypeEnum] = mapped_column(
        Enum(NewDrugEntryTypeEnum), nullable=False, index=True
    )
    entry_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # approved, pending, investigational

    # Change details as JSON
    changes: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    regulatory_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    market_impact: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    drug = relationship("Drug", back_populates="new_entries")

    def __repr__(self):
        return f"<NewDrugEntry(drug_id={self.drug_id}, entry_type={self.entry_type})>"


class DrugAnalytics(Base):
    """Drug analytics and performance metrics."""

    __tablename__ = "drug_analytics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    drug_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drugs.id"), nullable=False, index=True
    )

    # Time period for this analytics record
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Market performance metrics
    revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    market_share: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True
    )  # Percentage as decimal
    growth_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True
    )  # Percentage as decimal

    # Clinical metrics
    active_trials_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    success_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 4), nullable=True
    )  # Percentage as decimal
    patient_population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Competitive data as JSON
    competitive_landscape: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Additional metrics as JSON for flexibility
    additional_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
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
    drug = relationship("Drug", back_populates="analytics")

    def __repr__(self):
        return f"<DrugAnalytics(drug_id={self.drug_id}, period={self.period_start}-{self.period_end})>"


# Create indexes for performance
Index("idx_drugs_name", Drug.name)
Index("idx_drugs_generic_name", Drug.generic_name)
Index("idx_drugs_status", Drug.status)
Index("idx_drugs_therapeutic_area", Drug.therapeutic_area)
Index("idx_drugs_company_id", Drug.company_id)
Index("idx_drugs_approval_date", Drug.approval_date)
Index("idx_new_drug_entries_drug_id", NewDrugEntry.drug_id)
Index("idx_new_drug_entries_type", NewDrugEntry.entry_type)
Index("idx_new_drug_entries_date", NewDrugEntry.entry_date)
Index("idx_new_drug_entries_status", NewDrugEntry.status)
Index("idx_drug_regulatory_status_drug_id", DrugRegulatoryStatus.drug_id)
Index("idx_drug_regulatory_status_authority", DrugRegulatoryStatus.authority)
Index("idx_drug_patents_drug_id", DrugPatent.drug_id)
Index("idx_drug_patents_expiration", DrugPatent.expiration_date)
Index("idx_drug_analytics_drug_id", DrugAnalytics.drug_id)
Index("idx_drug_analytics_period", DrugAnalytics.period_start, DrugAnalytics.period_end)
