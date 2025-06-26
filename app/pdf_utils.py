# app/pdf_utils.py
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from io import BytesIO
import os
from .utils import format_inr, trim_text


def add_header_footer(canvas, doc):
    width, height = doc.pagesize
    canvas.saveState()

    # ✈️ Header
    canvas.setFont("NotoSans", 12)
    canvas.setFillColor(colors.darkblue)
    canvas.drawString(40, height - 30, "✈️ Procurement Monitoring Dashboard")

    # Page Footer
    canvas.setFont("NotoSans", 8)
    canvas.setFillColor(colors.grey)
    page_number_text = f"Page {canvas.getPageNumber()}"  # ✅ safe
    canvas.drawRightString(width - 40, 20, page_number_text)

    # Border
    canvas.setStrokeColor(colors.lightgrey)
    canvas.rect(25, 25, width - 50, height - 50, stroke=1)

    canvas.restoreState()



def generate_monthly_report_pdf(selected_month, report_df, total_inr, percent_75, exchange_info_line, highlight_rows=None):
    from reportlab.platypus import SimpleDocTemplate

    buffer = BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=landscape(A4), leftMargin=30, rightMargin=30, topMargin=50, bottomMargin=40)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='landscape')
    template = PageTemplate(id='landscape_template', frames=frame, onPage=add_header_footer)
    doc.addPageTemplates([template])

    # Font setup (required!)
    font_path = os.path.join(os.getcwd(), "NotoSans-Regular.ttf")
    pdfmetrics.registerFont(TTFont("NotoSans", font_path))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BlueTitle', parent=styles['Title'], textColor=colors.darkblue, fontName='NotoSans'))
    styles.add(ParagraphStyle(name='NormalNoto', parent=styles['Normal'], fontName='NotoSans'))

    content = [
        Paragraph(f"📅 Monthly Procurement Report – {selected_month}", styles['BlueTitle']),
        Spacer(1, 12),
        Paragraph(f"💰 Total Procurement Value: <b>{format_inr(total_inr)}</b>", styles['NormalNoto']),
        Paragraph(f"📌 7.5% Value: <b>{format_inr(percent_75)}</b>", styles['NormalNoto']),
        Paragraph(f"💱 {exchange_info_line}", styles['NormalNoto']),

        Spacer(1, 12),
    ]

    # Table header + data
    table_data = [list(report_df.columns)] + report_df.applymap(trim_text).values.tolist()

    table = Table(table_data, repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    if highlight_rows:
        for row in highlight_rows:
            style.add('BACKGROUND', (0, row + 1), (-1, row + 1), colors.orange)
    table.setStyle(style)
    content.append(table)

    doc.build(content)
    buffer.seek(0)
    return buffer


def generate_daily_activity_pdf(report_date, new_orders, shipped_items, grn_items, stock_in_items):
    buffer = BytesIO()




    # Font setup
    font_path = os.path.join(os.getcwd(), "NotoSans-Regular.ttf")
    pdfmetrics.registerFont(TTFont("NotoSans", font_path))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BlueTitle', parent=styles['Title'], textColor=colors.darkblue, fontName='NotoSans'))
    styles.add(ParagraphStyle(name='GreenHeading', parent=styles['Heading3'], textColor=colors.darkgreen, fontName='NotoSans'))
    styles['Normal'].fontName = 'NotoSans'

    # Doc + layout
    doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=50, bottomMargin=40)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='content', frames=frame, onPage=add_header_footer)
    doc.addPageTemplates([template])

    content = [Paragraph(f"📅 Daily Procurement Activity Report", styles['BlueTitle']), Spacer(1, 12),
               Paragraph(f"🗓️ Date: {report_date}", styles['Normal']), Spacer(1, 6)]

    # 🔹 Add Summary Page

    summary_items = [
        ("🆕 New Orders", len(new_orders)),
        ("🚚 Shipped Items", len(shipped_items)),
        ("✅ GRN Entries", len(grn_items)),
        ("📦 Stock-In Entries", len(stock_in_items)),
    ]
    for label, count in summary_items:
        content.append(Paragraph(f"- {label}: <b>{count}</b> rows", styles['Normal']))
        content.append(Spacer(1, 2))

    ####content.append(PageBreak())
# 🔹 Table Section Renderer (only if data exists)
    def add_table_section(title, data):
        if data.empty:
            return
    # ✅ Rename long MAWB column for PDF readability
        if "MAWB No. / Consignment No./  Bill of Lading No." in data.columns:
            data = data.rename(columns={"MAWB No. / Consignment No./  Bill of Lading No.": "MAWB/Consignment/BL No."})

        content.append(Paragraph(f"{title} (Total: {len(data)})", styles['GreenHeading']))
        content.append(Spacer(1, 6))

        headers = ["Sl No."] + list(data.columns)  # Sl No. becomes first column
        rows = data.values.tolist()

        # Add serial number to each row
        numbered_rows = [[str(i + 1)] + [trim_text(cell) for cell in row] for i, row in enumerate(rows)]

        trimmed_data = [headers] + numbered_rows  # Final data with Sl No.

        table = Table(trimmed_data, repeatRows=1)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3E9FF')),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        if 'PRIORITY' in data.columns:
            for idx, val in enumerate(data['PRIORITY'].astype(str).str.upper()):
                if val == 'AOG':
                    style.add('BACKGROUND', (0, idx + 1), (-1, idx + 1), colors.orange)
        table.setStyle(style)
        content.append(table)
        #######content.append(PageBreak())

    # 🔹 Conditional Rendering
    add_table_section("🆕 New Orders", new_orders)
    add_table_section("🚚 Shipped Items", shipped_items)
    add_table_section("✅ GRN Entries", grn_items)
    add_table_section("📦 Stock-In Entries", stock_in_items)

    # 🔹 Build final PDF
    doc.build(content)
    buffer.seek(0)
    return buffer
