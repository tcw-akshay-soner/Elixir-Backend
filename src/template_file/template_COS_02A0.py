import logging
import os
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

# Set up logging
from rich.logging import RichHandler

# Configure RichHandler
logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

stylesheet = getSampleStyleSheet()


async def create_template_COS(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    # product_name = product_data[0]['product_name'] if product_data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    if symbol_id:
        product_name_footer = product_name.replace(' ', '').replace(chr(int(symbol_code, 16)), '')
    else:
        product_name_footer = product_name.replace(' ', '')

    ingredient_data = await fetch_ingredient_data(product_id)

    header_style = ParagraphStyle('header_text',
                                  fontName='Cambria-Bold',
                                  fontSize=10,
                                  alignment=TA_LEFT)
    ingredient = Paragraph('<u>INGREDIENT</u>', style=header_style)
    source = Paragraph('<u>SOURCE</u>', style=header_style)
    dataset = [[ingredient, source]]  ## Initialization of Data

    ingredient_source = {}
    source_style = ParagraphStyle('ingredient_source',
                                  fontName='Cambria-Regular',
                                  fontSize=10,
                                  alignment=TA_LEFT)

    # maltodextrin = any(row['ing_name'] == 'Maltodextrin' for row in ingredient_data)
    # fos = any(row['ing_name'] == 'FOS' for row in ingredient_data)
    others = set()
    for row in ingredient_data:
        # logger.info(f"Other Ingredient {row['other_ing']}")
        other_ingredient = row['other_ing']
        ingredient_name = row['ing_name']
        if other_ingredient:
            others.add(row['ing_name'])
            # logger.info(f'Adding {row["ing_name"]} to others')
            continue
        # if ingredient_name in ['Maltodextrin', 'FOS']:
        #     continue
        # row['source'] = row['source'].replace('<em>', '<i>').replace('</em>', '</i>')

        if ingredient_name in ingredient_source:
            ingredient_source[ingredient_name].add(row['source'])
        else:
            ingredient_source[ingredient_name] = {row['source']}

    for ingredient, sources in ingredient_source.items():
        combined_source_data = " / ".join(sorted(sources))
        dataset.append([ingredient, Paragraph(combined_source_data, source_style)])

    w, h = A4
    lineSpacing = 20
    file_name = f"{company}_{product_name_footer}_COS_02A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    y -= lineSpacing
    c.setFont('Cambria-Regular', 11)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    y -= lineSpacing * 4
    # Placeholder for product name
    if symbol_id == 1 or symbol_id == 4:
        c.setFont('Cambria-Bold', 30)
        c.drawRightString(w - 30, y, product_name)
    else:
        text = product_name
        width = c.stringWidth(text, "Cambria-Bold", 30)
        charSpace = 0
        wordSpace = None
        if charSpace:
            width += (len(text) - 1) * charSpace
        if wordSpace:
            width += (text.count(u' ') + text.count(u'\xa0') - 1) * wordSpace
        text_object = c.beginText(w - 30 - width, y)
        product_name = product_name.replace(chr(int(symbol_code, 16)), '')
        text_object.setFont("Cambria-Bold", 30)
        text_object.textOut(product_name)
        text_object.setRise(6)
        text_object.setFont("Cambria-Bold", 30)
        text_object.textOut(symbol)
        text_object.setRise(0)
        c.drawText(text_object)

    y -= lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    y -= lineSpacing * 2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "CERTIFICATE OF SOURCE"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line((w / 2) - (text_width / 2), y - 16 * 0.2, (w / 2) + (text_width / 2), y - 16 * 0.2)
    y -= lineSpacing

    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=11,
                                textColor=colors.black,
                                alignment=TA_CENTER,
                                justifyBreaks=1,
                                justifyLastLine=0)

    text = "The Company certifies that <b>Source</b> of this product is as follows:"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    # y -= lineSpacing
    table_style = TableStyle([
        ('FONTNAME', (0, 1), (0, -1), 'Cambria-Regular'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (-1, 0), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3)])

    t = Table(dataset, style=table_style, colWidths=[150, 200], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)
    t.drawOn(c, tw / 2, (y - th - 20))
    y -= th + 30

    style_other = ParagraphStyle("Other_Text",
                                 fontName="Cambria-Italic",
                                 fontSize=8,
                                 textColor=colors.black,
                                 alignment=TA_CENTER,
                                 liftindent=0)

    if others:
        text = "<b>Other ingredients:</b> Product standardized in a base of " + ", ".join(others)
        p = Paragraph(text.strip(), style_other)
        p.wrapOn(c, w, h)
        p.drawOn(c, 0, y - h)


    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_COS_02A0")
    c.showPage()
    c.save()

    return file_path, file_name