"""
Company-related database models.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Date, DateTime, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class Company(Base):
    """Pharmaceutical company model."""

    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    ticker: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Company details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ceo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    employees: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Financial information
    market_cap: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True, index=True
    )
    revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    rd_spending: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(15, 2), nullable=True
    )

    # Business focus
    therapeutic_focus: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)), nullable=True, index=True
    )
    business_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # big_pharma, biotech, generic, etc.

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    drugs = relationship("Drug", foreign_keys="Drug.company_id", lazy="select")
    partnerships = relationship(
        "CompanyPartnership",
        foreign_keys="CompanyPartnership.company_id",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"


class CompanyPartnership(Base):
    """Company partnership and collaboration model."""

    __tablename__ = "company_partnerships"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    partner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )

    # Partnership details
    partnership_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # merger, acquisition, collaboration, etc.
    deal_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)

    # Partnership scope
    therapeutic_areas: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String(100)), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Important dates
    announcement_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active, completed, terminated

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    company = relationship(
        "Company", foreign_keys=[company_id], back_populates="partnerships"
    )
    partner = relationship("Company", foreign_keys=[partner_id])

    def __repr__(self):
        return f"<CompanyPartnership(company_id={self.company_id}, partner_id={self.partner_id}, type={self.partnership_type})>"


# Create indexes for performance
Index("idx_companies_name", Company.name)
Index("idx_companies_country", Company.country)
Index("idx_companies_ticker", Company.ticker)
Index("idx_companies_market_cap", Company.market_cap)
Index("idx_companies_therapeutic_focus", Company.therapeutic_focus)
