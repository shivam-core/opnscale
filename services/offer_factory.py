"""
Opnscale Offer Factory
=======================
Business logic brain. Given a TierName, instantly returns the correct
pricing, duration, and specific deliverables. Merges client data with
tier config into template-ready dictionaries for the PDF engine.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from models.schemas import (
    AgreementData,
    ClientInfo,
    InvoiceData,
    OnboardingRequest,
    TierConfig,
    TierName,
    TIER_REGISTRY,
)


def get_tier_config(tier: TierName) -> TierConfig:
    """
    Retrieve the full tier configuration for a given tier name.
    Raises KeyError if the tier doesn't exist (shouldn't happen with enum).
    """
    if tier not in TIER_REGISTRY:
        raise KeyError(f"Unknown tier: {tier}. Valid: {list(TIER_REGISTRY.keys())}")
    return TIER_REGISTRY[tier]


def get_all_tiers() -> dict[TierName, TierConfig]:
    """Return the full tier registry for UI display."""
    return TIER_REGISTRY


def generate_invoice_number(tier: TierName, sequence: int = 1) -> str:
    """
    Generate a formatted invoice number.
    Format: OPN-{YEAR}-{TIER_PREFIX}-{SEQUENCE}
    Example: OPN-2026-PB-0001
    """
    prefix_map = {
        TierName.PLAYBOOK: "PB",
        TierName.PRESENCE: "PR",
        TierName.LEVERAGE: "LV",
    }
    year = date.today().year
    prefix = prefix_map[tier]
    return f"OPN-{year}-{prefix}-{sequence:04d}"


def build_onboarding_package(
    request: OnboardingRequest,
    invoice_sequence: int = 1,
) -> dict:
    """
    Build the complete onboarding package from a validated OnboardingRequest.
    Returns a dictionary with all data needed for PDF generation and email dispatch.

    Keys:
        - client: ClientInfo
        - tier_config: TierConfig
        - agreement_data: AgreementData
        - invoice_data: InvoiceData
        - template_context: dict (flat dict for Jinja2 rendering)
    """
    tier_config = get_tier_config(request.tier)

    # Build Agreement data
    agreement_data = AgreementData(
        client=request.client,
        tier_config=tier_config,
        agreement_date=request.agreement_date,
        duration_months=tier_config.duration_months,
    )

    # Build Invoice data
    invoice_data = InvoiceData(
        invoice_number=generate_invoice_number(request.tier, invoice_sequence),
        invoice_date=request.agreement_date,
        client=request.client,
        tier_config=tier_config,
    )

    # Build a flat template context for Jinja2 rendering
    template_context = _build_template_context(
        client=request.client,
        tier_config=tier_config,
        agreement_data=agreement_data,
        invoice_data=invoice_data,
        notes=request.notes,
    )

    return {
        "client": request.client,
        "tier_config": tier_config,
        "agreement_data": agreement_data,
        "invoice_data": invoice_data,
        "template_context": template_context,
    }


def _build_template_context(
    client: ClientInfo,
    tier_config: TierConfig,
    agreement_data: AgreementData,
    invoice_data: InvoiceData,
    notes: Optional[str] = None,
) -> dict:
    """
    Flatten all data into a single dict for Jinja2 template rendering.
    This is the bridge between Pydantic models and HTML templates.
    """
    d = tier_config.deliverables

    return {
        # Client
        "client_name": client.name,
        "client_email": client.email,
        "client_company": client.company or "-",
        "client_phone": client.phone or "-",

        # Tier info
        "tier_name": tier_config.name.value,
        "tier_level": tier_config.level.value,
        "tier_description": tier_config.description,
        "duration_months": tier_config.duration_months,

        # Pricing
        "total_price": tier_config.total_price,
        "formatted_price": tier_config.formatted_price,
        "upfront_amount": tier_config.payment.upfront_amount,
        "on_results_amount": tier_config.payment.on_results_amount,
        "has_results_payment": tier_config.payment.on_results_amount > 0,

        # Agreement
        "agreement_date": agreement_data.agreement_date.strftime("%B %d, %Y"),
        "agreement_date_iso": agreement_data.agreement_date.isoformat(),

        # Invoice
        "invoice_number": invoice_data.invoice_number,
        "invoice_date": invoice_data.invoice_date.strftime("%B %d, %Y"),
        "line_items": invoice_data.line_items,

        # Deliverables (granular)
        "identity_excavation": d.identity_excavation,
        "content_strategy": d.content_strategy,
        "brand_identity": d.brand_identity,
        "script_writing": d.script_writing,
        "priyanshu_calls": d.priyanshu_calls,
        "whatsapp_access": d.whatsapp_access,
        "discord_access": d.discord_access,
        "community_calls": d.community_calls,
        "notion_portal": d.notion_portal,
        "team_execution": d.team_execution,
        "offer_architecture": d.offer_architecture,
        "business_positioning": d.business_positioning,
        "team_building_training": d.team_building_training,
        "backend_structure_systems": d.backend_structure_systems,

        # Leverage-only flags (for conditional template rendering)
        "is_leverage": tier_config.name == TierName.LEVERAGE,
        "is_presence": tier_config.name == TierName.PRESENCE,
        "is_playbook": tier_config.name == TierName.PLAYBOOK,

        # Notes
        "notes": notes or "",

        # Current year (for footer/copyright)
        "current_year": date.today().year,
    }


def get_welcome_email_subject(tier: TierName, client_name: str) -> str:
    """Generate the tier-specific email subject line."""
    subjects = {
        TierName.PLAYBOOK: f"Welcome to OPNSCALE PLAYBOOK, {client_name} — Let's Build",
        TierName.PRESENCE: f"Welcome to OPNSCALE PRESENCE, {client_name} — Your Brand Starts Now",
        TierName.LEVERAGE: f"Welcome to OPNSCALE LEVERAGE, {client_name} — The Full System Starts Here",
    }
    return subjects[tier]


def get_welcome_email_body(tier: TierName, client_name: str) -> str:
    """
    Generate the tier-specific welcome email body in Priyanshu's voice.
    Tone: warm authority, not corporate.
    """
    first_name = client_name.split()[0]

    bodies = {
        TierName.PLAYBOOK: f"""Hey {first_name},

Welcome to OPNSCALE PLAYBOOK.

You just made a decision most people put off for months. The system is in your hands now — the Identity Excavation framework, the content mechanics, the templates, the community. Everything you need to go from invisible to undeniable.

Here's what happens next:
• Your Notion portal is being activated — you'll get the link shortly.
• Jump into the Discord community — introduce yourself. The team and I are there.
• Start with Module 1. Don't skip the Identity Excavation pre-work. That's where the real clarity comes from.

This is self-paced, but not solo. You have team access via Discord for any questions. Use it.

The only thing that separates the people who transform their brand from the ones who don't — is they actually start. You've already started.

Let's build.

Priyanshu
OPNSCALE""",

        TierName.PRESENCE: f"""Hey {first_name},

Welcome to OPNSCALE PRESENCE. You just made the right call.

Here's the truth — your real-world credibility already exists. What we're doing over the next 3 months is making sure the internet knows it too. Identity first, content second. That's the order.

Here's what's happening:
• Your Notion portal is live — scripts, strategy, timelines, everything lives there.
• The team is already prepping your Identity Excavation — the 6-layer deep-dive that becomes the foundation of your entire brand.
• Your onboarding call with the team is being booked this week. Come with clarity on who you are — we'll do the rest.
• Discord + WhatsApp access is set up. Use it for async questions, feedback, anything.

I'll be joining bi-weekly to review progress and clear any bottlenecks personally.

You're not posting content for attention. You're building a brand that compounds. Let's get it done.

Priyanshu
OPNSCALE""",

        TierName.LEVERAGE: f"""Hey {first_name},

Welcome to OPNSCALE LEVERAGE. This is the full system.

Over the next 6 months, we're not just building your brand — we're building your entire business architecture. The identity, the content, the offer, the team, the backend. I'm working on this directly with you.

Here's the immediate play:
• I'm booking our first 1:1 call within 48 hours — you'll get the Calendly link shortly.
• Your Notion portal is fully activated — journey tracker, offer architecture section, weekly call notes, the works.
• You have direct access to me via Discord + WhatsApp. Use it. Async feedback, anytime.
• The team is already assigned and ready to execute alongside you.

This isn't a course. This isn't consulting. This is build mode.

The arc: Build → Execute → Monetize → Scale. We start now.

Let's go.

Priyanshu
OPNSCALE""",
    }

    return bodies[tier]
