import os
import warnings
import logging
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_product, fetch_composition, fetch_ingredient_data
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
warnings.filterwarnings('ignore')


async def create_template_percomposition(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    # product_name = data[0]['product_name'] if data else "N/A"
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

    header_style = ParagraphStyle('header_text',
                                fontName='Cambria-Bold',
                                fontSize=10,
                                alignment=TA_LEFT)
    ingredient = Paragraph('<u>INGREDIENTS</u>', style=header_style)
    composition = Paragraph('<u>% COMPOSITION</u>', style=header_style)
    ## Composition Data ##
    dataset = [[ingredient, composition]]
    # composition = await fetch_composition(product_id)
    ing_data = await fetch_ingredient_data(product_id)

    others = {}
    for row in ing_data:
        other_ingredient = row['other_ing']
        if other_ingredient:
            other_name = row['ing_name']
            others.setdefault(other_name, set()).add(row['source'])
            # logger.info(f'Adding {row["ing_name"]} to others')
            continue
        # if row['ing_name'] == 'Maltodextrin':
        #     maltodextrin = True
        #     continue
        # elif row['ing_name'] == 'FOS':
        #     fos = True
        #     continue
        dataset.append([row['ing_name'], row['alpha_composition']])

    other_data = {}
    # Fixing "Other Ingredients" Section
    other_data = {key: f"{key} (from {', '.join(sorted(value))})" for key, value in others.items()}
    others_data = list(other_data.values())

    file_name = f"{company}_{product_name_footer}_perComposition_01A0.pdf"
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
    # Placeholder for product name
    if symbol_id == 0:
        c.setFont('Cambria-Bold', 30)
        c.drawRightString(w - 30, y, product_name.replace(chr(int(symbol_code, 16)), ''))
    elif symbol_id == 1 or symbol_id == 4:
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
    y -= lineSpacing
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=11,
                                textColor=colors.black,
                                alignment=TA_CENTER,
                                justifyBreaks=1,
                                justifyLastLine=0)
    text = "The above mentioned product typically contains following active components:"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    ##### This is for list of composition fetched from db#####
    #### Start ####
    table_style = TableStyle([('FONTNAME', (0, 1), (-1, -1), 'Cambria-Regular'),
                              ('FONTSIZE', (0, 1), (-1, -1), 10, colors.black),
                              ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                              ('LEFTPADDING', (0, 0), (-1, -1), 10),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                              ('TOPPADDING', (0, 0), (-1, -1), 3)])

    t = Table(dataset, style=table_style, colWidths=[150, 200], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, tw / 2, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y = y - th - 30
    ### END ###

    style_other = ParagraphStyle("Other_Text",
                                fontName="Cambria-Italic",
                                fontSize=8,
                                textColor=colors.black,
                                strikeColor=0.4,
                                alignment=TA_CENTER)

    if others_data:
        text = "<b>Other ingredients:</b> Product standardized in a base of " + ", ".join(others_data)
        p = Paragraph(text.strip(), style_other)
        p.wrapOn(c, w, h)
        p.drawOn(c, 0, y - h)

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

    product_name = product_name.replace(" ", "")
    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_%Composition_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
