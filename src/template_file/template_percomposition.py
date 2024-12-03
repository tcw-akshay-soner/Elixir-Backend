import os

import warnings
import logging

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_product, fetch_composition
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_template_percomposition(date, temp_dir, company, product_id):
    ## Product Data ##
    data = await fetch_product(product_id)
    product_name = data[0]['product_name'] if data else "N/A"

    ## Composition Data ##
    dataset = [['INGREDIENTS', '%COMPOSITION']]
    composition = await fetch_composition(product_id)
    maltodextrin = False
    fos = False
    for row in composition:
        if row['ing_name'] == 'Maltodextrin':
            maltodextrin = True
            continue
        elif row['ing_name'] == 'FOS':
            fos = True
            continue
        dataset.append([row['ing_name'], row['per_composition']])
    
    file_name = f"{company}_product_perComposition_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)
    w, h = A4
    lineSpacing = 20

    ## Date
    y = y - lineSpacing
    c.setFont("Cambria-Regular", 12)
    c.drawRightString(w - 30, y, date)

    ## Product Name Display
    y = y - lineSpacing * 4

    c.setFont('Cambria-Bold', 25)
    c.drawRightString(w - 30, y, product_name)

    y = y - lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    c.drawCentredString(w / 2, y, "COMPOSITION STATEMENT")
    text_width = c.stringWidth("COMPOSITION STATEMENT", "Cambria-Bold", 14)

    ## Title underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)

    ### BODY TEXT SECTION ###

    text_object = c.beginText()
    text_object.setTextOrigin(100, y - 30)
    text_object.setFont('Cambria-Bold', 10)
    text = "The above mentioned product typically contains following active components:"
    text_object.textOut(text)
    c.drawText(text_object)

    ##### This is for list of composition fetched from db#####
    #### Start ####

    y = y - lineSpacing*2
    table_style = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('GRID', (0, 0), (0, -1), 1, colors.black),
                            ('GRID', (-1, 0), (-1, -1), 1, colors.black),
                            ('FONTNAME', (0, 0), (1, 0), 'Cambria-Bold'),
                            ('FONTSIZE', (0, 0), (1, 0), 12, colors.black),
                            ('FONTNAME', (0, 1), (-1, -1), 'Cambria-Regular'),
                            ('FONTSIZE', (0, 1), (-1, -1), 10, colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                            ('TOPPADDING', (0, 0), (-1, -1), 3)])

    t = Table(dataset, style=table_style, colWidths=[200, 200], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, (w - tw) / 2, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y = y - th - 30
    ### END ###

    style_other = ParagraphStyle("Other_Text",
                                 fontName="Cambria-Italic",
                                 fontSize=8,
                                 textColor=colors.black,
                                 strikeColor=0.4,
                                 alignment=TA_JUSTIFY)

    if maltodextrin and fos:
        text = f"<b>Other ingredients:</b> Product standardized in a base of Maltodextrin (from CORN) and FOS"
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 100, y - h)  # Adjusting the Y-position to ensure proper alignment
    elif fos:
        text = f"<b>Other ingredients:</b> Product standardized in a base of FOS"
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 100, y - h)  # Adjusting the Y-position to ensure proper alignment
    elif maltodextrin:
        text = f"<b>Other ingredients:</b> Product standardized in a base of Maltodextrin (from CORN)"
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 100, y - h)  # Adjusting the Y-position to ensure proper alignment

    y = y - h - lineSpacing
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=9,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leftIndent=30,
                                rightIndent=30)
    text = "<b><u>Note:</u></b><br/>" \
        "The potency of enzymes and probiotics are measured by activity levels and CFU count respectively." \
        " Milligram amounts and percentage compositions can vary dependent on the starting raw material of each individual ingredient and are therefore not an accurate measure of efficacy."
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_%Composition_01A0")
    c.showPage()
    c.save()
    
    return file_path, file_name
