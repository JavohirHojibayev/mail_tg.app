import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime

# Unicode qo'llab-quvvatlash uchun shriftlar
FONT_NAME = 'Helvetica'
FONT_NAME_BOLD = 'Helvetica-Bold'

for font_path, bold_path in [
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('CustomUnicode', font_path))
            FONT_NAME = 'CustomUnicode'
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont('CustomUnicode-Bold', bold_path))
                FONT_NAME_BOLD = 'CustomUnicode-Bold'
            else:
                FONT_NAME_BOLD = 'CustomUnicode'
            break
        except Exception:
            pass

def generate_employees_pdf(users: list, output_path: str = None) -> str:
    """
    Faqat xodim nomi va pochta manzilidan iborat toza, rasmiy PDF hujjat yaratadi.
    Bo'lim, lavozim va telefon ustunlari talabga binoan olib tashlangan.
    """
    if not output_path:
        output_dir = Path(__file__).resolve().parent.parent / "generated_docs"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = str(output_dir / f"UZ_Potash_Xodimlar_Royxati_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0B3954"),
        alignment=1, # Center
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=18
    )

    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1A202C")
    )

    email_cell_style = ParagraphStyle(
        'EmailCellText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0052CC")
    )

    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=10,
        leading=13,
        textColor=colors.white,
        alignment=1 # Center
    )

    num_cell_style = ParagraphStyle(
        'NumCell',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#4A5568"),
        alignment=1 # Center
    )

    elements = []

    # Sarlavha
    elements.append(Paragraph("UZ-POTASH (DEHQONOBOD KALIY ZAVODI)", title_style))
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    elements.append(Paragraph(f"Korporativ Pochta Xodimlari Katalogi &bull; Sana: {current_date}", subtitle_style))

    # Jadval — FAQAT 3 TA USTUN: №, Xodim F.I.SH, Pochta Manzili
    table_data = [
        [
            Paragraph("<b>№</b>", header_cell_style),
            Paragraph("<b>Xodimning F.I.SH (Nomi)</b>", header_cell_style),
            Paragraph("<b>Korporativ Pochta Manzili</b>", header_cell_style),
        ]
    ]

    for idx, u in enumerate(users, start=1):
        name = u.get("name") or u.get("email", "").split("@")[0]
        email = u.get("email", "")

        table_data.append([
            Paragraph(str(idx), num_cell_style),
            Paragraph(f"<b>{name}</b>", cell_style),
            Paragraph(f"<b>{email}</b>", email_cell_style),
        ])

    # Ustunlar kengligi: A4 kengligi 595 - marginlar (70) = 525 pt
    col_widths = [40, 265, 220]

    emp_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B3954")), # Korporativ to'q ko'k rang
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
        ('TOPPADDING', (0, 0), (-1, 0), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
    ]))

    elements.append(emp_table)
    elements.append(Spacer(1, 15))

    footer_style = ParagraphStyle(
        'FooterText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#718096"),
        alignment=2 # Right
    )
    elements.append(Paragraph(f"Jami xodimlar: {len(users)} nafar &bull; Rasmiy domen: @uz-potash.uz", footer_style))

    doc.build(elements)
    return output_path
