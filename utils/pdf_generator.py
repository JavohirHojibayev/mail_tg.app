from typing import Any
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_FONTS_DIR = PROJECT_ROOT / "fonts"

# Times New Roman shriftini ro'yxatga olish (Lokal, Windows va Linux tizimlari uchun)
font_candidates = [
    (str(LOCAL_FONTS_DIR / "times.ttf"), str(LOCAL_FONTS_DIR / "timesbd.ttf")),
    ("C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/timesbd.ttf"),
    ("/usr/share/fonts/truetype/msttcorefonts/times.ttf", "/usr/share/fonts/truetype/msttcorefonts/timesbd.ttf"),
    ("/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf", "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]

FONT_NAME = 'TimesNewRoman'
FONT_NAME_BOLD = 'TimesNewRoman-Bold'
font_registered = False

for font_path, bold_path in font_candidates:
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('TimesNewRoman', font_path))
            if os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', bold_path))
            else:
                pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', font_path))
            FONT_NAME = 'TimesNewRoman'
            FONT_NAME_BOLD = 'TimesNewRoman-Bold'
            font_registered = True
            break
        except Exception:
            pass

if not font_registered:
    FONT_NAME = 'Times-Roman'
    FONT_NAME_BOLD = 'Times-Bold'

def generate_employees_pdf(users: list, output_path: str | None = None, title: str = "DKZ AJ xodimlar ma'lumotlari") -> str:
    """
    PDF sarlavhasida berilgan sarlavha va xodim nomi, lavozimi, pochta manzili,
    mobil raqami, ofis raqami hamda ichki raqamidan iborat rasmiy jadval bo'ladi.
    Barcha shriftlar Times New Roman formatida yoziladi.
    """
    if not output_path:
        output_dir = PROJECT_ROOT / "generated_docs"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "DKZ_AJ_qidiruv" if "Qidiruv" in title or "Поиск" in title else "DKZ_AJ_xodimlar_malumotlari"
        output_path = str(output_dir / f"{prefix}_{timestamp}.pdf")

    # Albom (Landscape) formatda A4
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        leftMargin=35,
        rightMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    # Sarlavha stili
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0B3954"),
        alignment=1,  # Center
        spaceAfter=15
    )

    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1A202C")
    )

    pos_cell_style = ParagraphStyle(
        'PosCellText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2D3748")
    )

    email_cell_style = ParagraphStyle(
        'EmailCellText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0052CC")
    )

    phone_cell_style = ParagraphStyle(
        'PhoneCellText',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1A202C")
    )

    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=9.5,
        leading=13,
        textColor=colors.white,
        alignment=1  # Center
    )

    num_cell_style = ParagraphStyle(
        'NumCell',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
        alignment=1  # Center
    )

    elements: list[Any] = []

    # Sarlavha
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 10))

    is_ru = "Информация" in title or "Поиск" in title

    # Jadval sarlavhasi
    header_num = "<b>№</b>"
    header_name = "<b>Ф.И.О сотрудника</b>" if is_ru else "<b>Xodimning F.I.SH (Nomi)</b>"
    header_pos = "<b>Должность</b>" if is_ru else "<b>Lavozimi</b>"
    header_email = "<b>Корпоративная почта</b>" if is_ru else "<b>Korporativ Pochta Manzili</b>"
    header_phone = "<b>Мобильный номер</b>" if is_ru else "<b>Mobil raqam</b>"
    header_office = "<b>Офисный номер</b>" if is_ru else "<b>Ofis raqami</b>"
    header_ip = "<b>Внутренний номер</b>" if is_ru else "<b>Ichki raqam</b>"

    table_data = [
        [
            Paragraph(header_num, header_cell_style),
            Paragraph(header_name, header_cell_style),
            Paragraph(header_pos, header_cell_style),
            Paragraph(header_email, header_cell_style),
            Paragraph(header_phone, header_cell_style),
            Paragraph(header_office, header_cell_style),
            Paragraph(header_ip, header_cell_style),
        ]
    ]

    for idx, u in enumerate(users, start=1):
        name = u.get("name") or u.get("email", "").split("@")[0]
        pos = u.get("position", "—")
        email = u.get("email", "")
        phone = u.get("phone", "—")
        office_phone = u.get("office_phone", "—")
        ip_phone = u.get("ip_phone", "—")

        table_data.append([
            Paragraph(str(idx), num_cell_style),
            Paragraph(f"<b>{name}</b>", cell_style),
            Paragraph(pos, pos_cell_style),
            Paragraph(f"<b>{email}</b>", email_cell_style),
            Paragraph(phone, phone_cell_style),
            Paragraph(office_phone, phone_cell_style),
            Paragraph(ip_phone, phone_cell_style),
        ])

    # Ustun kengliklari (A4 Landscape = 842 pt; 772 pt jadval uchun)
    col_widths = [26, 175, 145, 165, 105, 86, 70]

    emp_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B3954")),
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
    doc.build(elements)
    return output_path
