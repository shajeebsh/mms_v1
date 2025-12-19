import io
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch

def generate_membership_questionnaire():
    """Generates a blank PDF questionnaire form for data collection"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    title_style.alignment = 1  # Center
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10,
        fontWeight='bold'
    )
    
    elements.append(Paragraph("Membership Registration Questionnaire", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Please fill in the details below for each family member.", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))
    
    # Define form fields
    fields = [
        ("Full Name", "________________________________________________"),
        ("Date of Birth", "____________________  Gender: [ ] M  [ ] F  [ ] O"),
        ("Aadhaar Card No", "________________________________"),
        ("Marital Status", "[ ] Single  [ ] Married  [ ] Widowed  [ ] Divorced"),
        ("Phone Number", "____________________  WhatsApp: ____________________"),
        ("Email Address", "________________________________________________"),
        ("Head of Family", "[ ] Yes  [ ] No"),
        ("Current Address", "________________________________________________"),
        ("", "________________________________________________"),
        ("Postal Code", "____________________"),
    ]
    
    # Create a nice layout table
    # We'll actually just use Paragraphs for a better form look
    for label, line in fields:
        if label:
            elements.append(Paragraph(f"<b>{label}:</b> {line}", styles["Normal"]))
        else:
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{line}", styles["Normal"]))
        elements.append(Spacer(1, 0.15 * inch))
        
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Authorized Signature: ____________________", styles["Normal"]))
    elements.append(Paragraph("Date: ____________________", styles["Normal"]))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_membership_card(member):
    """Generates a membership card PDF with a QR code"""
    buffer = io.BytesIO()
    
    # ID card size roughly 85.6mm x 54mm (standard)
    card_width = 85.6 * mm
    card_height = 54 * mm
    
    doc = SimpleDocTemplate(buffer, pagesize=(card_width, card_height),
                            rightMargin=5*mm, leftMargin=5*mm,
                            topMargin=5*mm, bottomMargin=5*mm)
    elements = []
    
    styles = getSampleStyleSheet()
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontSize=10,
        fontWeight='bold',
        textColor=colors.blue,
        alignment=1  # Center
    )
    
    name_style = ParagraphStyle(
        'MemberName',
        parent=styles['Normal'],
        fontSize=9,
        fontWeight='bold'
    )
    
    detail_style = ParagraphStyle(
        'MemberDetail',
        parent=styles['Normal'],
        fontSize=7
    )
    
    # Header
    elements.append(Paragraph("MOSQUE MANAGEMENT SYSTEM", card_title_style))
    elements.append(Paragraph("MEMBERSHIP CARD", ParagraphStyle('Sub', parent=card_title_style, fontSize=6, textColor=colors.black)))
    elements.append(Spacer(1, 2*mm))
    
    # QR Code generation
    qr_data = f"MMS-M-{member.id}-{member.first_name}-{member.last_name}"
    qr = qrcode.QRCode(version=1, box_size=1, border=1) # Smaller box size for card
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to BytesIO for reportlab
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    qr_image = Image(qr_buffer, width=15*mm, height=15*mm)
    
    # Photo and QR layout
    photo_image = None
    if member.photo:
        try:
            # Wagtail images have a file property that points to the actual file
            photo_path = member.photo.file.path
            photo_image = Image(photo_path, width=20*mm, height=25*mm)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Could not load photo for card: {e}")

    # Info Table
    if photo_image:
        info_data = [
            [photo_image, Paragraph(f"<b>{member.full_name}</b>", name_style), qr_image],
            ["", Paragraph(f"ID: MMS-{member.id:04d}", detail_style), ""],
            ["", Paragraph(f"Family: {member.family.name}", detail_style), ""],
            ["", Paragraph(f"Phone: {member.phone}", detail_style), ""],
        ]
        table = Table(info_data, colWidths=[22*mm, 35*mm, 15*mm])
        table.setStyle(TableStyle([
            ('SPAN', (0, 0), (0, 3)), # Photo spans all rows
            ('SPAN', (2, 0), (2, 3)), # QR spans all rows
            ('ALIGN', (2, 0), (2, 3), 'CENTER'),
            ('VALIGN', (2, 0), (2, 3), 'MIDDLE'),
            ('VALIGN', (0, 0), (0, 3), 'TOP'),
            ('VALIGN', (1, 0), (1, 3), 'TOP'),
        ]))
    else:
        info_data = [
            [Paragraph(f"<b>{member.full_name}</b>", name_style), qr_image],
            [Paragraph(f"ID: MMS-{member.id:04d}", detail_style), ""],
            [Paragraph(f"Family: {member.family.name}", detail_style), ""],
            [Paragraph(f"Phone: {member.phone}", detail_style), ""],
        ]
        table = Table(info_data, colWidths=[55*mm, 15*mm])
        table.setStyle(TableStyle([
            ('SPAN', (1, 0), (1, 3)),
            ('ALIGN', (1, 0), (1, 3), 'CENTER'),
            ('VALIGN', (1, 0), (1, 3), 'MIDDLE'),
            ('VALIGN', (0, 0), (0, 3), 'TOP'),
        ]))
    
    elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
