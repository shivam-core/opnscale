# OPNSCALE Onboarding Engine

A fully automated, modular onboarding and contract generation system built for OPNSCALE. This application powers the internal dashboard used by the OPNSCALE team to instantly onboard new clients, generate strictly-typed legal agreements and invoices, and dispatch tier-specific welcome emails.

## 🏗️ Architecture

The system is built on a highly decoupled, modular Python architecture:

*   **UI Layer (`app.py`):** A Streamlit dashboard for data entry, tier selection, and pipeline orchestration. Features a dynamic email draft editor and secure local SMTP credential management.
*   **Validation Layer (`models/schemas.py`):** Strict Pydantic models ensuring absolute precision. Ties OPNSCALE tiers (PLAYBOOK, PRESENCE, LEVERAGE) to immutable pricing and deliverable logic.
*   **Factory Layer (`services/offer_factory.py`):** The business logic brain. Generates comprehensive template contexts based on the selected tier.
*   **Document Engine (`services/pdf_engine.py` & `templates/`):** Utilizes `fpdf2` and `Jinja2` to render professional, strictly branded PDF agreements and invoices.
*   **Email Engine (`services/email_engine.py`):** A decoupled SMTP dispatcher supporting dynamic sender credentials, customizable email bodies, PDF attachments, and CC/BCC headers.

## 🚀 Features

*   **Tier-Based Automation:** Automatically populates pricing, engagement duration, and specific deliverables based on the selected tier.
*   **Dynamic Email Dispatch:** Select between authorized OPNSCALE senders. Supports secure saving of Google App Passwords via local `.env` injection.
*   **Editable Drafts:** Pre-populates high-conversion welcome email templates that can be freely edited in the UI before dispatch.
*   **Zero-Dependency PDF Generation:** Renders pixel-perfect OPNSCALE branded PDFs without requiring heavy system dependencies (like wkhtmltopdf).

## 🛠️ Local Development & Setup

### Prerequisites
*   Python 3.10+
*   Google Workspace App Passwords (for SMTP dispatch)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shivam-core/opnscale.git
   cd opnscale
# opnscale
