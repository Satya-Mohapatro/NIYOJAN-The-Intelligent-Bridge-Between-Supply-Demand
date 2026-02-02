from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
import os

# Register your custom font (DejaVu Sans supports Unicode)
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))

# ============================
# Emoji → Icon auto-replacement setup
# ============================
def replace_emojis_with_icons(text):
    """
    Automatically replace emojis in text with inline <img> tags for ReportLab.
    Works only if corresponding PNG icons exist in utils/icons/.
    """
    emoji_map = {
        "⚠️": "warning",
        "✅": "check",
        "📈": "growth",
        "🧠": "brain",
        "🕒": "clock",
        "📊": "chart",
        "🧩": "puzzle",
        "🏆": "trophy",
    }

    for emoji, icon_name in emoji_map.items():
        icon_path = os.path.join(os.path.dirname(__file__), "icons", f"{icon_name}.png")
        if os.path.exists(icon_path):
            img_tag = f'<img src="{icon_path}" width="14" height="14" valign="middle"/>'
            text = text.replace(emoji, img_tag)
    return text

# ============================
# Emoji → Icon auto-replacement setup - for ranks
# ============================
def get_rank_icon(rank):
    """Return the correct medal icon path based on product rank (1, 2, 3)."""
    icon_files = {
        1: "first.png",
        2: "second.png",
        3: "third.png"
    }
    file_name = icon_files.get(rank)
    if not file_name:
        return None
    icon_path = os.path.join(os.path.dirname(__file__), "icons", file_name)
    if os.path.exists(icon_path):
        return icon_path
    return None

# ============================
# PDF Generator
# ============================
def generate_pdf_report(output_path, overview, categories, top_products, alerts):
    """
    Generates a stylized PDF report with icons replacing emojis.
    """

    # Setup document
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Heading1Centered', parent=styles['Heading1'], alignment=1))
    styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, leading=16, spaceAfter=10, textColor=colors.HexColor("#333")))
    styles.add(ParagraphStyle(name='BodyTextSmall', fontSize=10, leading=13, textColor=colors.black))
    styles.add(ParagraphStyle(name='Emphasis', fontSize=11, textColor=colors.HexColor("#2a7f62")))

    elements = []

    # ===== HEADER =====
    title = Paragraph(replace_emojis_with_icons("🧠 <b>Niyojan Forecast Report</b>"), styles['Heading1Centered'])
    subtitle = Paragraph("<i>AI-Generated Weekly Insights</i>", styles['BodyText'])
    date = Paragraph(replace_emojis_with_icons(f"📅 Generated on: {datetime.now().strftime('%d %B %Y, %H:%M')}"), styles['BodyTextSmall'])
    elements += [title, subtitle, date, Spacer(1, 12)]

    # ===== OVERVIEW =====
    elements.append(Paragraph(replace_emojis_with_icons("📊 Overview"), styles['SectionTitle']))
    overview_data = [
        ["📦 Products Analyzed", str(overview.get("products", "N/A"))],
        ["⏱️ Forecast Horizon", f"{overview.get('horizon', 'N/A')} weeks"],
        ["📈 Total Forecast", f"{overview.get('forecast_total', 0):,} units"],
        ["📊 Avg Weekly Growth", f"{overview.get('avg_growth', 0):.2f}%"],
    ]
    overview_table = Table(overview_data, colWidths=[200, 200])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d9f7e6")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements += [overview_table, Spacer(1, 12)]

    # ===== CATEGORY-WISE FORECAST =====
    elements.append(Paragraph(replace_emojis_with_icons("🧩 Category-wise Forecast"), styles['SectionTitle']))
    cat_data = [["Category", "Products", "Total Forecast", "Avg per Product"]]
    for c in categories:
        cat_data.append([c['category'], str(c['products']), str(c['total']), str(c['avgPerProduct'])])

    cat_table = Table(cat_data, colWidths=[150, 80, 100, 100])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#cbe8ff")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements += [cat_table, Spacer(1, 12)]

    # ===== TOP PRODUCT INSIGHTS =====
    elements.append(Paragraph(replace_emojis_with_icons("🏆 Top Product Insights"), styles['SectionTitle']))
    for idx, prod in enumerate(top_products, start=1):
        rank_icon = get_rank_icon(idx)
        if rank_icon:
            text = f'<img src="{rank_icon}" width="18" height="18" valign="middle"/> ' \
                f'<b>{prod["name"]} ({prod["id"]})</b> — {prod["trend"]}'
        else:
            text = f"💡 <b>{prod['name']} ({prod['id']})</b> — {prod['trend']}"
        elements.append(Paragraph(replace_emojis_with_icons(text), styles['BodyTextSmall']))
    elements.append(Spacer(1, 12))


    # ===== ALERTS =====
    elements.append(Paragraph(replace_emojis_with_icons("⚠️ Alerts Summary"), styles['SectionTitle']))

    if alerts:
        alert_data = [["Product", "Forecast", "Alert", "Created"]]
        for a in alerts:
            alert_data.append([
                a["product"],
                str(a["forecast"]),
                a["alert"],
                a["created_at"]
            ])

        # ✅ Create and style the table AFTER appending all rows
        alert_table = Table(alert_data, colWidths=[110, 60, 250, 100])
        alert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ffe8d6")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        # ✅ Optional: highlight high-demand rows in red
        for row_idx, row in enumerate(alert_data[1:], start=1):
            if "high demand" in row[2].lower():
                alert_table.setStyle([
                    ('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.HexColor("#d90429"))
                ])

        elements.append(alert_table)

    else:
        elements.append(Paragraph(
            replace_emojis_with_icons("✅ No alerts for this forecast period."),
            styles['BodyTextSmall']
        ))


    # ===== FOOTER =====
    elements.append(Spacer(1, 24))
    footer_text = "🕒 Generated automatically by <b>Niyojan AI Forecast System</b><br/>" \
                  f"© {datetime.now().year} Niyojan Team"
    footer = Paragraph(replace_emojis_with_icons(footer_text), styles['Emphasis'])
    elements.append(footer)

    # Build and save
    doc.build(elements)
    return output_path
