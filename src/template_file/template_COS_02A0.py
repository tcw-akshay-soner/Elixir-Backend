import logging, os
import re

# import structureddatastore as sds
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

from src.engine.pharma_data import fetch_product, fetch_ingredient_data
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_template_COS(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"
    combined_source_data = set()
    ingredient_data = await fetch_ingredient_data(product_id)
    dataset = [['INGREDIENTS', 'SOURCE']]  ## Initialization of Data

    maltodextrin = False
    fos = False
    ## Create a Dictionary for ingredient name
    ingredient_countries = {}
    for row in ingredient_data:
        ingredient_name = row['ing_name']
        if ingredient_name == 'Maltodextrin':
            maltodextrin = True
            continue
        elif ingredient_name == 'FOS':
            fos = True
            continue
        if ingredient_name in ingredient_countries:
            ingredient_countries[ingredient_name].add(row['source'])
        else:
            ingredient_countries[ingredient_name] = {row['source']}

    ## Iterate Through the Collected Data
    for ingredient, countries in ingredient_countries.items():
        combined_source_data = "/".join(sorted(countries))
        dataset.append([ingredient, combined_source_data])

    w, h = A4
    lineSpacing = 20
    
    file_name = f"{company}_{product_name}_COS_02A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)


    ## Date Section
    y = y - lineSpacing
    c.setFont('Cambria-Regular', 11)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Section
    y = y - lineSpacing * 4
    c.setFont('Cambria-Bold', 30)
    c.drawRightString(w - 30, y, product_name)  # Placeholder for product name

    y = y - lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "CERTIFICATE OF SOURCE"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing

    ### BODY TEXT SECTION ###
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=12,
                                textColor=colors.black,
                                alignment=TA_LEFT,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leftIndent=30)

    text = "The Company certifies that <b>Source</b> of this product is as follows:"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    ### INGREDIENTS AND COUNTRY OF ORIGIN TABLE ###
    y = y - lineSpacing
    table_style = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('GRID', (0, 0), (0, -1), 1, colors.black),
                            ('GRID', (-1, 0), (-1, -1), 1, colors.black),
                            ('FONTNAME', (0, 0), (1, 0), 'Cambria-Bold'),
                            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                            ('FONTSIZE', (0, 0), (1, 0), 12, colors.black),
                            ('FONTNAME', (0, 1), (0, -1), 'Cambria-Regular'),
                            ('FONTSIZE', (0, 1), (-1, -1), 10, colors.black),
                            ('FONTNAME', (1, 1), (-1, -1), 'Cambria-Italic'),
                            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                            ('TOPPADDING', (0, 0), (-1, -1), 3)])

    # For Automatic column widths
    t = Table(dataset, style=table_style, splitByRow=1, repeatRows=1)
    # t = Table(dataset, style=table_style, colWidths=[200, 200], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, (w - tw) / 2, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y = y - th - 30
    ### END TABLE ###
    #
    style_other = ParagraphStyle("Other_Text",
                                fontName="Cambria-Italic",
                                fontSize=8,
                                textColor=colors.black,
                                strikeColor=0.4,
                                alignment=TA_CENTER,
                                leftIndent=0)

    if maltodextrin and fos:
        text = f"<b>Other ingredients:</b> Product standardized in a base of Maltodextrin (from CORN) and FOS"
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment
    elif fos:
        text = f"<b>Other ingredients:</b> Product standardized in a base of FOS"
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment
    elif maltodextrin:
        text = f"<b>Other ingredients:</b> Product standardized in a base of Maltodextrin (from CORN)"
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    product_name = product_name.replace(" ", "")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_COS_02A0")
    c.showPage()
    c.save()
    
    return file_path, file_name