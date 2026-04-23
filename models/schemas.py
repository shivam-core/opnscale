"""
Opnscale Onboarding Engine - Pydantic Schemas
===============================================
Strict data validation for all three Opnscale tiers.
Any mismatch between tier name and pricing/deliverables is blocked at the schema level.

Tiers (from opnscale-os.html):
  - PLAYBOOK  → $500   | 12 months | Self-paced, no Priyanshu
  - PRESENCE  → $2,000 | 3 months  | Team-built brand, Priyanshu oversees
  - LEVERAGE  → $4,000 | 6 months  | Full system with Priyanshu direct
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TierName(str, Enum):
    """The three Opnscale service tiers."""
    PLAYBOOK = "PLAYBOOK"
    PRESENCE = "PRESENCE"
    LEVERAGE = "LEVERAGE"


class TierLevel(str, Enum):
    """Ticket classification for each tier."""
    LOW = "Entry - Low Ticket"
    MID = "Mid Ticket"
    HIGH = "High Ticket - Flagship"


# ---------------------------------------------------------------------------
# Payment & Pricing
# ---------------------------------------------------------------------------

class PaymentStructure(BaseModel):
    """How the total price is split between upfront and results-based payment."""
    upfront_amount: int = Field(..., ge=0, description="Amount due on signing (USD)")
    on_results_amount: int = Field(0, ge=0, description="Amount due on results delivery (USD)")

    @property
    def total_price(self) -> int:
        return self.upfront_amount + self.on_results_amount


# ---------------------------------------------------------------------------
# Deliverables - granular per-tier capability flags
# ---------------------------------------------------------------------------

class TierDeliverables(BaseModel):
    """
    Every deliverable across all three tiers.
    Boolean fields indicate inclusion; string fields provide specifics.
    """

    # Identity Excavation
    identity_excavation: str = Field(
        ...,
        description="Level of Identity Excavation included"
    )

    # Content Strategy
    content_strategy: str = Field(
        ...,
        description="Scope of content strategy provided"
    )

    # Brand Identity / Visual System
    brand_identity: str = Field(
        ...,
        description="How brand identity/visual system is delivered"
    )

    # Script Writing
    script_writing: str = Field(
        ...,
        description="How script writing is handled"
    )

    # Priyanshu 1:1 Calls
    priyanshu_calls: str = Field(
        ...,
        description="Level of direct Priyanshu call access"
    )

    # WhatsApp Access
    whatsapp_access: str = Field(
        ...,
        description="WhatsApp access level"
    )

    # Discord Access
    discord_access: str = Field(
        ...,
        description="Discord access level"
    )

    # Community Calls
    community_calls: bool = Field(
        True,
        description="Access to community calls (included in all tiers)"
    )

    # Notion Portal
    notion_portal: bool = Field(
        True,
        description="Notion portal + database access (included in all tiers)"
    )

    # Team Execution
    team_execution: str = Field(
        ...,
        description="Level of team execution support"
    )

    # --- LEVERAGE-only deliverables ---

    offer_architecture: bool = Field(
        False,
        description="Info offer / productized service built with Priyanshu (LEVERAGE only)"
    )

    business_positioning: bool = Field(
        False,
        description="ICP, pricing, messaging - business positioning (LEVERAGE only)"
    )

    team_building_training: bool = Field(
        False,
        description="Setters, editors, ops - trained (LEVERAGE only)"
    )

    backend_structure_systems: bool = Field(
        False,
        description="SOPs + systems built (LEVERAGE only)"
    )


# ---------------------------------------------------------------------------
# Tier Configuration - the complete definition of a single tier
# ---------------------------------------------------------------------------

class TierConfig(BaseModel):
    """
    Full configuration for one Opnscale tier.
    This is the single source of truth for pricing, duration, and deliverables.
    """
    name: TierName
    level: TierLevel
    description: str = Field(..., description="One-line tier description")
    duration_months: int = Field(..., gt=0, description="Engagement duration in months")
    payment: PaymentStructure
    deliverables: TierDeliverables

    @property
    def total_price(self) -> int:
        return self.payment.total_price

    @property
    def formatted_price(self) -> str:
        """Human-readable price string."""
        if self.payment.on_results_amount > 0:
            return (
                f"${self.payment.total_price:,} "
                f"(${self.payment.upfront_amount:,} upfront + "
                f"${self.payment.on_results_amount:,} on results)"
            )
        return f"${self.payment.upfront_amount:,}"


# ---------------------------------------------------------------------------
# Pre-built Tier Configurations (locked to opnscale-os.html data)
# ---------------------------------------------------------------------------

PLAYBOOK_CONFIG = TierConfig(
    name=TierName.PLAYBOOK,
    level=TierLevel.LOW,
    description=(
        "The self-paced system. Course + community + team access. "
        "For the ICP who needs the method before the full investment."
    ),
    duration_months=12,
    payment=PaymentStructure(upfront_amount=500, on_results_amount=0),
    deliverables=TierDeliverables(
        identity_excavation="Framework only (modules)",
        content_strategy="Frameworks + templates",
        brand_identity="Template access",
        script_writing="Frameworks only",
        priyanshu_calls="None",
        whatsapp_access="None",
        discord_access="Community + 1:1 team chat",
        community_calls=True,
        notion_portal=True,
        team_execution="Self-paced",
        offer_architecture=False,
        business_positioning=False,
        team_building_training=False,
        backend_structure_systems=False,
    ),
)

PRESENCE_CONFIG = TierConfig(
    name=TierName.PRESENCE,
    level=TierLevel.MID,
    description=(
        "Personal brand built by the team, overseen by Priyanshu. "
        "Identity first, content second. Brand only - no offer layer."
    ),
    duration_months=3,
    payment=PaymentStructure(upfront_amount=1000, on_results_amount=1000),
    deliverables=TierDeliverables(
        identity_excavation="Full 6-layer positioning framework",
        content_strategy="Brand only - team built",
        brand_identity="Built for them [Observation Board]",
        script_writing="Done with team [Claude Project system]",
        priyanshu_calls="Bi-weekly - bottlenecks only",
        whatsapp_access="Discord + WhatsApp team channel",
        discord_access="Community + 1:1 team chat (same as Playbook)",
        community_calls=True,
        notion_portal=True,
        team_execution="Team executes",
        offer_architecture=False,
        business_positioning=False,
        team_building_training=False,
        backend_structure_systems=False,
    ),
)

LEVERAGE_CONFIG = TierConfig(
    name=TierName.LEVERAGE,
    level=TierLevel.HIGH,
    description=(
        "Full system - brand, offer, business architecture. "
        "The only tier where you get Priyanshu building it with you directly."
    ),
    duration_months=6,
    payment=PaymentStructure(upfront_amount=2000, on_results_amount=2000),
    deliverables=TierDeliverables(
        identity_excavation="Full 6-layer positioning framework",
        content_strategy="Brand + business - with Priyanshu",
        brand_identity="Done FOR them",
        script_writing="Done with Priyanshu",
        priyanshu_calls="Weekly - direct",
        whatsapp_access="Direct to Priyanshu",
        discord_access="Direct async",
        community_calls=True,
        notion_portal=True,
        team_execution="Team alongside client",
        offer_architecture=True,
        business_positioning=True,
        team_building_training=True,
        backend_structure_systems=True,
    ),
)

# Master registry - keyed by TierName for instant lookup
TIER_REGISTRY: dict[TierName, TierConfig] = {
    TierName.PLAYBOOK: PLAYBOOK_CONFIG,
    TierName.PRESENCE: PRESENCE_CONFIG,
    TierName.LEVERAGE: LEVERAGE_CONFIG,
}


# ---------------------------------------------------------------------------
# Client Info
# ---------------------------------------------------------------------------

class ClientInfo(BaseModel):
    """Client details captured by Vedant during onboarding."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Client's full name"
    )
    email: EmailStr = Field(..., description="Client's email address")
    company: Optional[str] = Field(
        None,
        max_length=200,
        description="Client's company or brand name (optional)"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Client's phone number (optional)"
    )


# ---------------------------------------------------------------------------
# Onboarding Request - the validated payload that triggers the pipeline
# ---------------------------------------------------------------------------

class OnboardingRequest(BaseModel):
    """
    The top-level request model. Vedant selects a client + tier in the UI,
    and this model validates everything before any documents are generated.
    """
    client: ClientInfo
    tier: TierName
    agreement_date: date = Field(
        default_factory=date.today,
        description="Date of the agreement (defaults to today)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional internal notes from Vedant"
    )

    @property
    def tier_config(self) -> TierConfig:
        """Retrieve the full tier configuration for the selected tier."""
        return TIER_REGISTRY[self.tier]

    @model_validator(mode="after")
    def validate_tier_integrity(self) -> "OnboardingRequest":
        """
        Ensure the selected tier exists in the registry.
        This is a safety net - the enum already constrains valid names,
        but this confirms the registry is in sync.
        """
        if self.tier not in TIER_REGISTRY:
            raise ValueError(
                f"Tier '{self.tier}' is not registered. "
                f"Valid tiers: {list(TIER_REGISTRY.keys())}"
            )
        return self


# ---------------------------------------------------------------------------
# Invoice Model
# ---------------------------------------------------------------------------

class InvoiceData(BaseModel):
    """All data needed to render an invoice PDF."""
    invoice_number: str = Field(..., description="Unique invoice identifier (e.g. OPN-2026-0001)")
    invoice_date: date = Field(default_factory=date.today)
    client: ClientInfo
    tier_config: TierConfig
    due_date: Optional[date] = Field(None, description="Payment due date (if applicable)")

    @property
    def line_items(self) -> list[dict]:
        """Generate invoice line items from tier deliverables."""
        items = []
        d = self.tier_config.deliverables

        # Core deliverables (always present)
        items.append({
            "description": f"Identity Excavation - {d.identity_excavation}",
            "included": True,
        })
        items.append({
            "description": f"Content Strategy - {d.content_strategy}",
            "included": True,
        })
        items.append({
            "description": f"Brand Identity / Visual System - {d.brand_identity}",
            "included": True,
        })
        items.append({
            "description": f"Script Writing - {d.script_writing}",
            "included": True,
        })

        # Communication access
        if d.priyanshu_calls != "None":
            items.append({
                "description": f"Priyanshu 1:1 Calls - {d.priyanshu_calls}",
                "included": True,
            })
        if d.whatsapp_access != "None":
            items.append({
                "description": f"WhatsApp Access - {d.whatsapp_access}",
                "included": True,
            })
        items.append({
            "description": f"Discord Access - {d.discord_access}",
            "included": True,
        })
        if d.community_calls:
            items.append({"description": "Community Calls Access", "included": True})
        if d.notion_portal:
            items.append({"description": "Notion Portal + Database", "included": True})

        # Team execution
        if d.team_execution != "Self-paced":
            items.append({
                "description": f"Team Execution - {d.team_execution}",
                "included": True,
            })

        # LEVERAGE-only
        if d.offer_architecture:
            items.append({
                "description": "Offer Architecture - Info offer / productized service built with Priyanshu",
                "included": True,
            })
        if d.business_positioning:
            items.append({
                "description": "Business Positioning - ICP, pricing, messaging",
                "included": True,
            })
        if d.team_building_training:
            items.append({
                "description": "Team Building + Training - Setters, editors, ops",
                "included": True,
            })
        if d.backend_structure_systems:
            items.append({
                "description": "Backend Structure + Systems - SOPs + systems built",
                "included": True,
            })

        return items


# ---------------------------------------------------------------------------
# Agreement Model
# ---------------------------------------------------------------------------

class AgreementData(BaseModel):
    """All data needed to render an agreement PDF."""
    client: ClientInfo
    tier_config: TierConfig
    agreement_date: date = Field(default_factory=date.today)
    duration_months: int = Field(..., gt=0)

    @model_validator(mode="after")
    def sync_duration(self) -> "AgreementData":
        """Ensure duration matches the tier's defined duration."""
        expected = self.tier_config.duration_months
        if self.duration_months != expected:
            raise ValueError(
                f"Duration mismatch: {self.tier_config.name.value} tier "
                f"requires {expected} months, got {self.duration_months}"
            )
        return self
