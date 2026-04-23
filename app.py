"""
Opnscale Onboarding Engine - Streamlit UI
==========================================
Vedant's dashboard for instantly onboarding new clients.
Select a tier, enter client details, generate PDFs, and dispatch via email.
"""

import os
import streamlit as st
from pathlib import Path

from dotenv import load_dotenv, set_key

from models.schemas import (
    ClientInfo,
    OnboardingRequest,
    TierName,
    TIER_REGISTRY,
)
from services.offer_factory import (
    build_onboarding_package,
    get_tier_config,
)
from services.pdf_engine import generate_all_pdfs
from services.email_engine import send_onboarding_email, SENDER_REGISTRY

# ---------------------------------------------------------------------------
# .env helpers
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

def _reload_env() -> None:
    """Force-reload .env so newly saved keys are visible."""
    load_dotenv(ENV_PATH, override=True)

def _get_saved_password(env_key: str) -> str:
    """Check if a password exists in .env for the given key."""
    _reload_env()
    return os.getenv(env_key, "").strip()

def _save_password_to_env(env_key: str, password: str) -> None:
    """Persist a password to the local .env file."""
    if not ENV_PATH.exists():
        ENV_PATH.touch()
    set_key(str(ENV_PATH), env_key, password)


# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="OPNSCALE - Onboarding Engine",
    page_icon="*",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Global */
.stApp {
    background: #0A0A08;
    color: #EDE9E2;
    font-family: 'Inter', sans-serif;
}

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}

/* Header */
.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0 20px 0;
    border-bottom: 1px solid #252525;
    margin-bottom: 32px;
}
.main-logo {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 6px;
    color: #FF6A00;
}
.main-sub {
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #555;
}

/* Section Labels */
.section-label {
    font-size: 9px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #FF6A00;
    font-weight: 700;
    margin-bottom: 12px;
}

/* Input overrides */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #111111 !important;
    border: 1px solid #252525 !important;
    color: #EDE9E2 !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #FF6A00 !important;
    box-shadow: 0 0 0 1px #FF6A00 !important;
}

/* Labels */
.stTextInput > label, .stTextArea > label, .stRadio > label, .stSelectbox > label, .stCheckbox > label {
    color: #9A9488 !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* Button */
div.stButton > button {
    background: #FF6A00 !important;
    color: #000 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
    padding: 14px 32px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
div.stButton > button:hover {
    background: #E05E00 !important;
    transform: translateY(-1px) !important;
}

/* Success/Error boxes */
.success-box {
    background: rgba(90, 173, 120, 0.08);
    border: 1px solid rgba(90, 173, 120, 0.25);
    border-radius: 8px;
    padding: 20px 24px;
    margin: 16px 0;
}
.success-title {
    color: #5AAD78;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.success-detail {
    color: #9A9488;
    font-size: 12px;
    line-height: 1.6;
}

.error-box {
    background: rgba(220, 80, 60, 0.08);
    border: 1px solid rgba(220, 80, 60, 0.25);
    border-radius: 8px;
    padding: 20px 24px;
    margin: 16px 0;
}
.error-title {
    color: #DC503C;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Radio buttons */
div[role="radiogroup"] > label {
    background: #111111 !important;
    border: 1px solid #252525 !important;
    border-radius: 6px !important;
    padding: 10px 16px !important;
    margin-right: 8px !important;
    color: #9A9488 !important;
    transition: all 0.2s !important;
}
div[role="radiogroup"] > label[data-checked="true"] {
    border-color: #FF6A00 !important;
    color: #FF6A00 !important;
}

/* Divider */
.custom-divider {
    height: 1px;
    background: #252525;
    margin: 28px 0;
}

/* Preview card */
.preview-card {
    background: #111111;
    border: 1px solid #252525;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
}
.preview-label {
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #FF6A00;
    font-weight: 600;
    margin-bottom: 12px;
}
.preview-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #1A1A18;
    font-size: 12px;
}
.preview-key { color: #6B6860; }
.preview-val { color: #EDE9E2; font-weight: 500; }
.preview-total {
    display: flex;
    justify-content: space-between;
    padding: 12px 0 0 0;
    margin-top: 4px;
    border-top: 1px solid #333;
    font-size: 16px;
    font-weight: 700;
}
.preview-total .price { color: #FF6A00; }

.feat-item { display: flex; align-items: flex-start; gap: 6px; margin-bottom: 3px; }
.feat-dot { color: #FF6A00; font-size: 8px; margin-top: 3px; flex-shrink: 0; }

/* Saved badge */
.saved-badge {
    display: inline-block;
    background: rgba(90, 173, 120, 0.12);
    color: #5AAD78;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid rgba(90, 173, 120, 0.25);
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div>
        <div class="main-logo">OPNSCALE</div>
        <div class="main-sub">Onboarding Engine</div>
    </div>
    <div class="main-sub">Vedant x Priyanshu</div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tier Selection
# ---------------------------------------------------------------------------
st.markdown('<div class="section-label">Select Client Tier</div>', unsafe_allow_html=True)

tier_options = list(TIER_REGISTRY.keys())
tier_labels = {
    TierName.PLAYBOOK: "PLAYBOOK",
    TierName.PRESENCE: "PRESENCE",
    TierName.LEVERAGE: "LEVERAGE",
}

selected_tier = st.radio(
    "Tier",
    options=tier_options,
    format_func=lambda t: tier_labels[t],
    horizontal=True,
    label_visibility="collapsed",
)

tier_config = get_tier_config(selected_tier)

# Tier detail card
tier_colors = {
    TierName.PLAYBOOK: "#555",
    TierName.PRESENCE: "#888",
    TierName.LEVERAGE: "#FF6A00",
}

st.markdown(f"""
<div class="preview-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
        <div>
            <div style="font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{tier_colors[selected_tier]};margin-bottom:4px">{tier_config.level.value}</div>
            <div style="font-size:22px;font-weight:800;letter-spacing:3px;{'color:#FF6A00;' if selected_tier == TierName.LEVERAGE else ''}">OPNSCALE {tier_config.name.value}</div>
        </div>
        <div style="text-align:right">
            <div style="font-size:22px;font-weight:800;color:#FF6A00">${tier_config.total_price:,}</div>
            <div style="font-size:11px;color:#6B6860">{tier_config.duration_months}-Month Engagement</div>
        </div>
    </div>
    <div style="font-size:12px;color:#6B6860;font-style:italic;line-height:1.5;padding-bottom:12px;border-bottom:1px solid #252525;margin-bottom:12px">{tier_config.description}</div>
    <div style="font-size:11px;color:#9A9488;line-height:1.8">
        <div class="feat-item"><span class="feat-dot">*</span> Identity Excavation - {tier_config.deliverables.identity_excavation}</div>
        <div class="feat-item"><span class="feat-dot">*</span> Content Strategy - {tier_config.deliverables.content_strategy}</div>
        <div class="feat-item"><span class="feat-dot">*</span> Brand Identity - {tier_config.deliverables.brand_identity}</div>
        <div class="feat-item"><span class="feat-dot">*</span> Priyanshu Calls - {tier_config.deliverables.priyanshu_calls}</div>
        <div class="feat-item"><span class="feat-dot">*</span> Team Execution - {tier_config.deliverables.team_execution}</div>
        <div class="feat-item"><span class="feat-dot">*</span> Duration - {tier_config.duration_months} months</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Client Details
# ---------------------------------------------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Client Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Client Name", placeholder="e.g. Harshit Kumar")
    client_company = st.text_input("Company / Brand (optional)", placeholder="e.g. Acme Corp")
with col2:
    client_email = st.text_input("Client Email", placeholder="e.g. harshit@example.com")
    client_phone = st.text_input("Phone (optional)", placeholder="e.g. +91 98765 43210")

notes = st.text_area("Internal Notes (optional)", placeholder="Any notes for this client...", height=80)

col_cc, col_bcc = st.columns(2)
with col_cc:
    cc_emails = st.text_input("CC (optional)", placeholder="e.g. vedant@opnscale.com, team@opnscale.com")
with col_bcc:
    bcc_emails = st.text_input("BCC (optional)", placeholder="e.g. records@opnscale.com")


# ---------------------------------------------------------------------------
# Sender Configuration (Dynamic SMTP)
# ---------------------------------------------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Sender Configuration</div>', unsafe_allow_html=True)

sender_emails = list(SENDER_REGISTRY.keys())
selected_sender = st.selectbox(
    "Send From",
    options=sender_emails,
    format_func=lambda e: f"{SENDER_REGISTRY[e]['display_name']}  ({e})",
)

# Resolve password state for the selected sender
sender_info = SENDER_REGISTRY[selected_sender]
env_key = sender_info["env_key"]
saved_password = _get_saved_password(env_key)
has_saved_password = bool(saved_password)

# Dynamic password UI
session_password = ""
save_password_checked = False

if has_saved_password:
    # Password exists in .env -- show green badge, no input needed
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin:8px 0 4px 0">
        <span class="saved-badge">Password Saved</span>
        <span style="font-size:11px;color:#6B6860">App Password for <strong style="color:#EDE9E2">{selected_sender}</strong> is stored in .env ({env_key})</span>
    </div>
    """, unsafe_allow_html=True)
    session_password = saved_password
else:
    # No password saved -- render input field
    session_password = st.text_input(
        f"Google App Password for {selected_sender}",
        type="password",
        placeholder="Enter 16-digit App Password",
        help="Generate this from Google Account > Security > App Passwords",
    )
    save_password_checked = st.checkbox(
        "Save password locally for future use",
        value=False,
        help=f"If checked, the password will be written to .env as {env_key} when you click Generate & Send.",
    )


# ---------------------------------------------------------------------------
# Email Draft (Editable)
# ---------------------------------------------------------------------------
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">Email Draft (Editable)</div>', unsafe_allow_html=True)

# Default email draft
_draft_name = client_name if client_name else "{client name}"
_default_body = f"""Hey {_draft_name},

Welcome to OPNSCALE LEVERAGE. This is the full system.

Over the next 6 months, we\u2019re not just building your brand \u2014 we\u2019re building your entire business architecture. The identity, the content, the offer, the team, the backend. I\u2019m working on this directly with you.

Here\u2019s the immediate play:
\u2022 I\u2019m booking our first 1:1 call within 48 hours \u2014 you\u2019ll get the Calendly link shortly.
\u2022 Your Notion portal is fully activated \u2014 journey tracker, offer architecture section, weekly call notes, the works.
\u2022 You have direct access to me via Discord + WhatsApp. Use it. Async feedback, anytime.
\u2022 The team is already assigned and ready to execute alongside you.

This isn\u2019t a course. This isn\u2019t consulting. This is build mode.

The arc: Build \u2192 Execute \u2192 Monetize \u2192 Scale. We start now.

Let\u2019s go.

Priyanshu
OPNSCALE

---
Attached: Your OPNSCALE Service Agreement and Invoice."""

email_draft = st.text_area(
    "Email Body",
    value=_default_body,
    height=300,
    label_visibility="collapsed",
    help="This is the exact text that will be sent to the client. Edit freely before sending.",
)


# Action buttons
col_gen, col_send = st.columns(2)

with col_gen:
    generate_clicked = st.button("*  Generate PDFs", use_container_width=True)

with col_send:
    send_clicked = st.button("Generate & Send Email", use_container_width=True)


# ---------------------------------------------------------------------------
# Pipeline Execution
# ---------------------------------------------------------------------------
def run_pipeline(send_email: bool = False):
    """Execute the onboarding pipeline."""

    # Validate inputs
    if not client_name or not client_email:
        st.markdown("""
        <div class="error-box">
            <div class="error-title">Missing Information</div>
            <div style="color:#9A9488;font-size:12px">Please fill in at least the Client Name and Email.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Build the Pydantic request
    try:
        request = OnboardingRequest(
            client=ClientInfo(
                name=client_name,
                email=client_email,
                company=client_company if client_company else None,
                phone=client_phone if client_phone else None,
            ),
            tier=selected_tier,
            notes=notes if notes else None,
        )
    except Exception as e:
        st.markdown(f"""
        <div class="error-box">
            <div class="error-title">Validation Error</div>
            <div style="color:#9A9488;font-size:12px">{str(e)}</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Build the onboarding package
    with st.spinner("Building onboarding package..."):
        package = build_onboarding_package(request)

    # Generate PDFs
    with st.spinner("Generating PDFs..."):
        try:
            pdf_paths = generate_all_pdfs(package["template_context"])
        except Exception as e:
            st.markdown(f"""
            <div class="error-box">
                <div class="error-title">PDF Generation Error</div>
                <div style="color:#9A9488;font-size:12px">{str(e)}</div>
            </div>
            """, unsafe_allow_html=True)
            return

    # Show success
    st.markdown(f"""
    <div class="success-box">
        <div class="success-title">PDFs Generated Successfully</div>
        <div class="success-detail">
            * Agreement: {pdf_paths['agreement'].name}<br>
            * Invoice: {pdf_paths['invoice'].name}<br>
            * Location: {pdf_paths['agreement'].parent}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Offer downloads
    for doc_type, path in pdf_paths.items():
        with open(path, "rb") as f:
            st.download_button(
                label=f"Download {doc_type.title()} PDF",
                data=f.read(),
                file_name=path.name,
                mime="application/pdf",
                use_container_width=True,
            )

    # Send email if requested
    if send_email:
        # Validate password is available
        if not session_password:
            st.markdown(f"""
            <div class="error-box">
                <div class="error-title">No App Password</div>
                <div style="color:#9A9488;font-size:12px">Enter the Google App Password for {selected_sender} in the Sender Configuration section above.</div>
            </div>
            """, unsafe_allow_html=True)
            return

        # Save to .env if user checked the box
        if save_password_checked and session_password:
            _save_password_to_env(env_key, session_password)
            st.markdown(f"""
            <div class="success-box">
                <div class="success-title">Password Saved</div>
                <div class="success-detail">
                    App Password for {selected_sender} saved to .env as {env_key}. It will auto-load next time.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Dispatch email
        with st.spinner("Sending email..."):
            result = send_onboarding_email(
                client_name=client_name,
                client_email=client_email,
                tier=selected_tier,
                agreement_pdf=pdf_paths["agreement"],
                invoice_pdf=pdf_paths["invoice"],
                sender_email=selected_sender,
                smtp_password=session_password,
                email_body=email_draft,
                cc=cc_emails if cc_emails else None,
                bcc=bcc_emails if bcc_emails else None,
            )

        if result["success"]:
            st.markdown(f"""
            <div class="success-box">
                <div class="success-title">Email Sent</div>
                <div class="success-detail">
                    * To: {client_email}<br>
                    * From: {selected_sender}<br>
                    * Subject: {result['subject']}<br>
                    * {result['message']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="error-box">
                <div class="error-title">Email Failed</div>
                <div style="color:#9A9488;font-size:12px">{result['message']}</div>
            </div>
            """, unsafe_allow_html=True)


# Run on button click
if generate_clicked:
    run_pipeline(send_email=False)

if send_clicked:
    run_pipeline(send_email=True)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("""
<div style="margin-top:60px;padding-top:16px;border-top:1px solid #252525;display:flex;justify-content:space-between">
    <div style="font-size:10px;letter-spacing:2px;color:#555">OPNSCALE ONBOARDING ENGINE</div>
    <div style="font-size:10px;letter-spacing:2px;color:#555">INTERNAL - CONFIDENTIAL</div>
</div>
""", unsafe_allow_html=True)
