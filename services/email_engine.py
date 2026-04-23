"""
Opnscale Email Engine
======================
Decoupled SMTP dispatch. The UI layer handles credential resolution
and passes them directly — this engine never reads from .env itself.
"""

from __future__ import annotations

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from models.schemas import TierName
from services.offer_factory import get_welcome_email_subject

# Sender registry: maps each sender email to display name and .env key.
SENDER_REGISTRY: dict[str, dict[str, str]] = {
    "priyanshuradia@opnscales.com": {
        "display_name": "Priyanshu - OPNSCALE",
        "env_key": "PRIYANSHU_SMTP_PASS",
    },
    "vedantopnscale@gmail.com": {
        "display_name": "Vedant - OPNSCALE",
        "env_key": "VEDANT_SMTP_PASS",
    },
    "shivamcorex@gmail.com": {
        "display_name": "Shivam - OPNSCALE",
        "env_key": "SHIVAM_SMTP_PASS",
    },
}


def _attach_pdf(msg: MIMEMultipart, pdf_path: Path, filename: str) -> None:
    """Attach a PDF file to the email message."""
    with open(pdf_path, "rb") as f:
        part = MIMEBase("application", "pdf")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        msg.attach(part)


def send_onboarding_email(
    client_name: str,
    client_email: str,
    tier: TierName,
    agreement_pdf: Path,
    invoice_pdf: Path,
    sender_email: str,
    smtp_password: str,
    email_body: str,
    cc: str | None = None,
    bcc: str | None = None,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    dry_run: bool = False,
) -> dict[str, bool | str]:
    """
    Send the tier-specific welcome email with PDF attachments.

    All credentials are passed explicitly by the UI layer.
    This engine never reads from os.getenv or .env directly.

    Args:
        client_name: Client's full name
        client_email: Client's email address
        tier: The selected TierName
        agreement_pdf: Path to the generated agreement PDF
        invoice_pdf: Path to the generated invoice PDF
        sender_email: The chosen sender email address
        smtp_password: The 16-digit Google App Password for the sender
        email_body: The full email body text (editable by the user in the UI)
        cc: Comma-separated CC email addresses (optional)
        bcc: Comma-separated BCC email addresses (optional)
        smtp_host: SMTP server hostname (default: Gmail)
        smtp_port: SMTP server port (default: 587 for STARTTLS)
        dry_run: If True, build the email but don't send

    Returns:
        Dict with status info: {"success": bool, "message": str, "subject": str}
    """
    sender_info = SENDER_REGISTRY.get(sender_email, {})
    sender_display = sender_info.get("display_name", "OPNSCALE")

    msg = MIMEMultipart()
    msg["From"] = f"{sender_display} <{sender_email}>"
    msg["To"] = client_email
    msg["Subject"] = get_welcome_email_subject(tier, client_name)

    msg.attach(MIMEText(email_body, "plain"))

    # CC header is visible; BCC is only added to the sendmail envelope.
    cc_list = [e.strip() for e in cc.split(",") if e.strip()] if cc else []
    bcc_list = [e.strip() for e in bcc.split(",") if e.strip()] if bcc else []
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    all_recipients = [client_email] + cc_list + bcc_list

    first_name_slug = client_name.split()[0]
    _attach_pdf(msg, agreement_pdf, f"OPNSCALE_{tier.value}_Agreement_{first_name_slug}.pdf")
    _attach_pdf(msg, invoice_pdf, f"OPNSCALE_{tier.value}_Invoice_{first_name_slug}.pdf")

    if dry_run:
        return {
            "success": True,
            "message": f"[DRY RUN] Email built for {client_email} from {sender_email} - not sent.",
            "subject": msg["Subject"],
        }

    if not smtp_password or not smtp_password.strip():
        return {
            "success": False,
            "message": f"No App Password provided for {sender_email}. Enter it in the Sender Config section.",
            "subject": msg["Subject"],
        }

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, smtp_password)
            server.sendmail(sender_email, all_recipients, msg.as_string())

        return {
            "success": True,
            "message": f"Email sent successfully to {client_email} from {sender_email}",
            "subject": msg["Subject"],
        }

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": f"SMTP authentication failed for {sender_email}. Check your App Password.",
            "subject": msg["Subject"],
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "message": f"SMTP error: {str(e)}",
            "subject": msg["Subject"],
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "subject": msg["Subject"],
        }
