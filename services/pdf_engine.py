"""
Opnscale PDF Engine — fpdf2
============================
Generates professional Agreement and Invoice PDFs programmatically.
Pure Python — no system dependencies required.
"""
from __future__ import annotations

from pathlib import Path
from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

# Brand colors (RGB)
C_BLACK = (26, 26, 24)
C_ACCENT = (255, 106, 0)
C_GRAY = (107, 104, 96)
C_MUTED = (154, 151, 144)
C_BORDER = (232, 229, 223)
C_BG = (245, 244, 240)
C_WHITE = (255, 255, 255)
C_GREEN = (61, 139, 88)


def _ensure_output_dir() -> None:
    """Create the output directory if it doesn't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize(name: str) -> str:
    """Convert a name to a filesystem-safe slug."""
    return "".join(
        c if c.isalnum() or c in (" ", "-", "_") else ""
        for c in name
    ).strip().replace(" ", "_")


class OpnscalePDF(FPDF):
    """Base PDF class with Opnscale branding helpers."""

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.add_page()

    def _set_font_color(self, color: tuple[int, int, int]) -> None:
        self.set_text_color(*color)

    def brand_header(self, doc_type: str, meta_lines: list[str]):
        self.set_font("Helvetica", "B", 18)
        self._set_font_color(C_BLACK)
        self.cell(90, 8, "OPNSCALE", new_x="RIGHT", new_y="TOP")
        self.set_font("Helvetica", "", 8)
        self._set_font_color(C_MUTED)
        for line in meta_lines:
            self.cell(0, 4, line, new_x="LMARGIN", new_y="NEXT", align="R")
        self.ln(2)
        self.set_draw_color(*C_BLACK)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)
        self.set_font("Helvetica", "B", 16)
        self._set_font_color(C_BLACK)
        self.cell(0, 8, doc_type, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def section_label(self, num: str, title: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 7)
        self._set_font_color(C_ACCENT)
        self.cell(0, 4, f"SECTION {num}", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "B", 11)
        self._set_font_color(C_BLACK)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.3)
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(4)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 9)
        self._set_font_color(C_GRAY)
        self.multi_cell(0, 4.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def table_row(self, col1: str, col2: str, header: bool = False) -> None:
        self.set_draw_color(*C_BORDER)
        if header:
            self.set_font("Helvetica", "B", 7)
            self._set_font_color(C_MUTED)
        else:
            self.set_font("Helvetica", "", 9)
        w1, w2 = 70, 120
        y_start = self.get_y()
        x_start = self.get_x()
        if header:
            self._set_font_color(C_MUTED)
            self.cell(w1, 6, col1, new_x="RIGHT", new_y="TOP")
            self.cell(w2, 6, col2, new_x="LMARGIN", new_y="NEXT")
        else:
            self._set_font_color(C_BLACK)
            self.cell(w1, 5.5, col1, new_x="RIGHT", new_y="TOP")
            self._set_font_color(C_GRAY)
            self.cell(w2, 5.5, col2, new_x="LMARGIN", new_y="NEXT")
        self.set_line_width(0.15)
        self.line(10, self.get_y() + 0.5, 200, self.get_y() + 0.5)
        self.ln(1)

    def term_item(self, text: str):
        self.set_font("Helvetica", "", 9)
        self._set_font_color(C_GRAY)
        x = self.get_x()
        self.cell(5, 4.5, "--", new_x="RIGHT", new_y="TOP")
        self.multi_cell(175, 4.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def brand_footer_line(self, left: str, right: str):
        self.ln(6)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_font("Helvetica", "", 7)
        self._set_font_color(C_MUTED)
        self.cell(95, 4, left)
        self.cell(95, 4, right, align="R", new_x="LMARGIN", new_y="NEXT")


def render_agreement_pdf(ctx: dict) -> Path:
    """Render the service agreement PDF from a template context dict."""
    _ensure_output_dir()
    pdf = OpnscalePDF()

    # Header
    pdf.brand_header("Service Agreement", [
        f"Date: {ctx['agreement_date']}",
        f"Tier: OPNSCALE {ctx['tier_name']}",
        f"Duration: {ctx['duration_months']} Months",
    ])
    pdf.body_text("This agreement outlines the scope of work, deliverables, terms, and payment structure between OPNSCALE and the Client.")

    # Parties
    pdf.section_label("01", "Parties")
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_ACCENT)
    pdf.cell(95, 4, "SERVICE PROVIDER", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, "CLIENT", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf._set_font_color(C_BLACK)
    pdf.cell(95, 5, "OPNSCALE", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 5, ctx["client_name"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf._set_font_color(C_GRAY)
    pdf.cell(95, 4, "Represented by Priyanshu", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, ctx["client_email"], new_x="LMARGIN", new_y="NEXT")
    if ctx["client_company"] not in ("--", "-"):
        pdf.cell(95, 4, "Brand, Content & Business Architecture", new_x="RIGHT", new_y="TOP")
        pdf.cell(95, 4, ctx["client_company"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Tier Banner
    pdf.set_fill_color(*C_BLACK)
    pdf.rect(10, pdf.get_y(), 190, 16, "F")
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_ACCENT)
    y_b = pdf.get_y() + 3
    pdf.set_xy(14, y_b)
    pdf.cell(80, 4, "SELECTED TIER")
    pdf.set_font("Helvetica", "B", 13)
    pdf._set_font_color(C_WHITE)
    pdf.set_xy(14, y_b + 4)
    pdf.cell(80, 6, f"OPNSCALE {ctx['tier_name']}")
    pdf.set_font("Helvetica", "B", 13)
    pdf._set_font_color(C_ACCENT)
    pdf.set_xy(130, y_b + 2)
    pdf.cell(66, 6, f"${ctx['total_price']:,}", align="R")
    pdf.set_font("Helvetica", "", 7)
    pdf._set_font_color(C_MUTED)
    pdf.set_xy(130, y_b + 9)
    dur_text = f"{ctx['duration_months']}-Month Engagement"
    if ctx["has_results_payment"]:
        dur_text += " | Split Payment"
    pdf.cell(66, 4, dur_text, align="R")
    pdf.set_y(pdf.get_y() + 8)
    pdf.ln(2)

    # Scope
    pdf.section_label("02", "Scope of Work")
    pdf.body_text(ctx["tier_description"])
    pdf.body_text(f"The engagement period is {ctx['duration_months']} months from the date of this agreement.")

    # Deliverables
    pdf.section_label("03", "Deliverables")
    pdf.table_row("DELIVERABLE", "SPECIFICATION", header=True)
    rows = [
        ("Identity Excavation", ctx["identity_excavation"]),
        ("Content Strategy", ctx["content_strategy"]),
        ("Brand Identity / Visual", ctx["brand_identity"]),
        ("Script Writing", ctx["script_writing"]),
        ("Priyanshu 1:1 Calls", ctx["priyanshu_calls"]),
        ("WhatsApp Access", ctx["whatsapp_access"]),
        ("Discord Access", ctx["discord_access"]),
        ("Community Calls", "Included"),
        ("Notion Portal", "Included"),
        ("Team Execution", ctx["team_execution"]),
    ]
    if ctx["is_leverage"]:
        rows += [
            ("Offer Architecture", "Built with Priyanshu"),
            ("Business Positioning", "ICP, pricing, messaging"),
            ("Team Building + Training", "Setters, editors, ops"),
            ("Backend Systems", "SOPs + systems built"),
        ]
    for r in rows:
        pdf.table_row(r[0], r[1])

    # Payment
    pdf.section_label("04", "Payment Structure")
    pdf.set_font("Helvetica", "B", 9)
    pdf._set_font_color(C_BLACK)
    pdf.cell(95, 5, f"Upfront: ${ctx['upfront_amount']:,}", new_x="RIGHT", new_y="TOP")
    if ctx["has_results_payment"]:
        pdf.cell(95, 5, f"On Results: ${ctx['on_results_amount']:,}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(95, 5, "One-time payment", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf._set_font_color(C_GRAY)
    pdf.cell(0, 5, f"Total investment: {ctx['formatted_price']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Terms
    pdf.section_label("05", "Terms & Conditions")
    terms = [
        f"Effective from {ctx['agreement_date']} for {ctx['duration_months']} months.",
        f"Deliverables are specific to OPNSCALE {ctx['tier_name']} and cannot be exchanged without formal upgrade.",
        "Client agrees to provide timely feedback and materials within the engagement timeline.",
        "Upfront payment is non-refundable once work has commenced.",
        "OPNSCALE may use anonymized results for marketing unless Client opts out in writing.",
        "Proprietary frameworks and internal tools remain OPNSCALE intellectual property.",
        "Either party may terminate with 30 days written notice.",
    ]
    if ctx["is_leverage"]:
        terms.append("LEVERAGE clients agree to mutual NDA covering business architecture and internal systems.")
    for t in terms:
        pdf.term_item(t)

    # Signatures
    pdf.ln(6)
    pdf.set_draw_color(*C_BLACK)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_ACCENT)
    pdf.cell(95, 4, "SERVICE PROVIDER", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, "CLIENT", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(14)
    pdf.set_draw_color(*C_BORDER)
    pdf.set_line_width(0.3)
    x = pdf.get_x()
    y = pdf.get_y()
    pdf.line(10, y, 95, y)
    pdf.line(105, y, 200, y)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf._set_font_color(C_BLACK)
    pdf.cell(95, 4, "Priyanshu - OPNSCALE", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, ctx["client_name"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf._set_font_color(C_MUTED)
    pdf.cell(95, 4, f"Date: {ctx['agreement_date']}", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, "Date: _______________", new_x="LMARGIN", new_y="NEXT")

    pdf.brand_footer_line("OPNSCALE - Service Agreement", f"Confidential - {ctx['current_year']}")

    slug = _sanitize(ctx["client_name"])
    out = OUTPUT_DIR / f"{slug}_agreement.pdf"
    pdf.output(str(out))
    return out


def render_invoice_pdf(ctx: dict) -> Path:
    """Render the invoice PDF from a template context dict."""
    _ensure_output_dir()
    pdf = OpnscalePDF()

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf._set_font_color(C_BLACK)
    pdf.cell(90, 8, "OPNSCALE", new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 8, "INVOICE", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf._set_font_color(C_MUTED)
    pdf.cell(90, 4, "Media Agency", new_x="RIGHT", new_y="TOP")
    pdf.set_font("Helvetica", "B", 9)
    pdf._set_font_color(C_ACCENT)
    pdf.cell(0, 4, ctx["invoice_number"], align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*C_BLACK)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # Billed To / From
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_ACCENT)
    pdf.cell(95, 4, "BILLED TO", new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, "FROM", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 10)
    pdf._set_font_color(C_BLACK)
    pdf.cell(95, 5, ctx["client_name"], new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 5, "OPNSCALE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf._set_font_color(C_GRAY)
    pdf.cell(95, 4, ctx["client_email"], new_x="RIGHT", new_y="TOP")
    pdf.cell(95, 4, "Priyanshu", new_x="LMARGIN", new_y="NEXT")
    if ctx["client_company"] not in ("--", "-"):
        pdf.cell(95, 4, ctx["client_company"], new_x="RIGHT", new_y="TOP")
        pdf.cell(95, 4, "Brand, Content & Business Architecture", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Info boxes
    pdf.set_fill_color(*C_BG)
    box_w = 60
    gap = 5
    y_box = pdf.get_y()
    for i, (label, val) in enumerate([
        ("INVOICE DATE", ctx["invoice_date"]),
        ("SERVICE TIER", f"OPNSCALE {ctx['tier_name']}"),
        ("DURATION", f"{ctx['duration_months']} Months"),
    ]):
        x_box = 10 + i * (box_w + gap)
        pdf.set_xy(x_box, y_box)
        pdf.rect(x_box, y_box, box_w, 14, "F")
        pdf.set_xy(x_box + 4, y_box + 2)
        pdf.set_font("Helvetica", "B", 7)
        pdf._set_font_color(C_MUTED)
        pdf.cell(box_w - 8, 4, label)
        pdf.set_xy(x_box + 4, y_box + 7)
        pdf.set_font("Helvetica", "B", 9)
        pdf._set_font_color(C_BLACK)
        pdf.cell(box_w - 8, 5, val)
    pdf.set_y(y_box + 20)

    # Line items
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_ACCENT)
    pdf.cell(0, 4, "INCLUDED DELIVERABLES", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Table header
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_MUTED)
    pdf.cell(12, 5, "#")
    pdf.cell(148, 5, "DESCRIPTION")
    pdf.cell(30, 5, "STATUS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*C_BORDER)
    pdf.set_line_width(0.4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(1)

    for i, item in enumerate(ctx["line_items"], 1):
        pdf.set_font("Helvetica", "", 8)
        pdf._set_font_color(C_MUTED)
        pdf.cell(12, 5, f"{i:02d}")
        pdf._set_font_color(C_GRAY)
        pdf.cell(148, 5, item["description"][:80])
        pdf.set_font("Helvetica", "B", 9)
        pdf._set_font_color(C_GREEN)
        pdf.cell(30, 5, "Y", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(*C_BORDER)
        pdf.set_line_width(0.1)
        pdf.line(10, pdf.get_y() + 0.3, 200, pdf.get_y() + 0.3)
        pdf.ln(0.5)

    # Totals
    pdf.ln(4)
    x_total = 130
    w_total = 70
    if ctx["has_results_payment"]:
        pdf.set_xy(x_total, pdf.get_y())
        pdf.set_font("Helvetica", "", 9)
        pdf._set_font_color(C_GRAY)
        pdf.cell(40, 5, "Upfront Payment")
        pdf.cell(30, 5, f"${ctx['upfront_amount']:,}", align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_xy(x_total, pdf.get_y())
        pdf.cell(40, 5, "On Results")
        pdf.cell(30, 5, f"${ctx['on_results_amount']:,}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_draw_color(*C_BLACK)
    pdf.set_line_width(0.5)
    pdf.line(x_total, pdf.get_y() + 1, 200, pdf.get_y() + 1)
    pdf.ln(3)
    pdf.set_xy(x_total, pdf.get_y())
    pdf.set_font("Helvetica", "B", 12)
    pdf._set_font_color(C_BLACK)
    pdf.cell(40, 6, "Total")
    pdf._set_font_color(C_ACCENT)
    pdf.cell(30, 6, f"${ctx['total_price']:,}", align="R", new_x="LMARGIN", new_y="NEXT")

    # Payment note
    pdf.ln(6)
    pdf.set_fill_color(*C_BG)
    y_note = pdf.get_y()
    pdf.rect(10, y_note, 190, 16, "F")
    pdf.set_xy(14, y_note + 2)
    pdf.set_font("Helvetica", "B", 7)
    pdf._set_font_color(C_ACCENT)
    pdf.cell(0, 4, "PAYMENT TERMS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 8)
    pdf._set_font_color(C_GRAY)
    if ctx["has_results_payment"]:
        note = f"${ctx['upfront_amount']:,} due on signing. ${ctx['on_results_amount']:,} due within 14 days of results delivery. Payment via Stripe or Razorpay."
    else:
        note = f"${ctx['total_price']:,} due in full upon signing. Payment via Stripe or Razorpay."
    pdf.multi_cell(178, 4, note, new_x="LMARGIN", new_y="NEXT")
    pdf.set_y(y_note + 20)

    pdf.brand_footer_line(f"OPNSCALE - Invoice {ctx['invoice_number']}", f"Confidential - {ctx['current_year']}")

    slug = _sanitize(ctx["client_name"])
    out = OUTPUT_DIR / f"{slug}_invoice.pdf"
    pdf.output(str(out))
    return out


def generate_all_pdfs(template_context: dict) -> dict[str, Path]:
    """Generate both agreement and invoice PDFs."""
    return {
        "agreement": render_agreement_pdf(template_context),
        "invoice": render_invoice_pdf(template_context),
    }
