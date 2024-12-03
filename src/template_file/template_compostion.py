import os
import random
import re

import warnings
import logging

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_product, fetch_composition
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_template_composition(date, temp_dir, company, product_id):
    ## Product Data ##
    data = await fetch_product(product_id)
    product_name = data[0]['product_name'] if data else "N/A"

    ## Composition Data ##
    ingredients = set()
    composition = await fetch_composition(product_id)
    for row in composition:
        ingredients.add(row['ing_name'])
    ingredients = ",".join(ingredients)

    w, h = A4
    lineSpacing = 20
    file_name = f"{company}_{product_name}_Composition_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date
    y = y - lineSpacing
    c.setFont("Cambria-Regular", 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Name Display
    y = y - lineSpacing * 4

    c.setFont('Cambria-Bold', 30)
    c.drawRightString(w - 30, y, product_name)

    y = y - lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 3
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "COMPOSITION STATEMENT"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing / 2

    ### BODY TEXT SECTION ###

    # ingredients = re.split(r':|;',dataset.ingredient)
    text_object = c.beginText()
    text_object.setTextOrigin(100, y - 40)
    text_object.setFont('Cambria-Bold', 10)

    text = "The above mentioned product typically contains following active components:"
    text_object.textOut(text)
    c.drawText(text_object)

    ##### This is for list of composition fetched from db#####
    #### Start ####

    bullet_indent = 30
    line_spacing = 15
    x = 100
    y = 470
    if len(ingredients) > 1:
        ingredients = ingredients.split(',')
    maltodextrin = False
    fos = False
    for i in ingredients:  # Iteration through ingredients list
        if i == 'Maltodextrin':
            maltodextrin = True
            continue
        elif i == 'FOS':
            fos = True
            continue
        p = Paragraph(i, stylesheet['Heading4'], bulletText='•')  # Including Paragraph in canvas with bullet text
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, x + bullet_indent, y)  # Adjusting the Y-position to ensure proper alignment
        y -= line_spacing
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

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_Composition_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
