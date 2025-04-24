import logging
import os
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

from src.engine.pharma_data import fetch_product, fetch_ingredient_data
from src.engine.strip_html_tags import strip_html_tags
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


async def create_template_COO3(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    # product_name = product_data[0]['product_name'] if product_data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

    combined_country_data = set()
    ingredient_data = await fetch_ingredient_data(product_id)

    header_style = ParagraphStyle('header_text',
                                  fontName='Cambria-Bold',
                                  fontSize=10,
                                  alignment=TA_LEFT)
    ingredient = Paragraph('<u>INGREDIENT</u>', style=header_style)
    coo = Paragraph('<u>COUNTRY OF ORIGIN</u>', style=header_style)
    dataset = [[ingredient, coo]]  ## Initialization of Data

    # maltodextrin = any(row['ing_name'] == 'Maltodextrin' for row in ingredient_data)
    # fos = any(row['ing_name'] == 'FOS' for row in ingredient_data)
    # others = {}
    ing_style = ParagraphStyle('ing_style',
                               fontName='Cambria-Regular',
                               fontSize=10,
                               alignment=TA_LEFT)
    ## Create a Dictionary for ingredient name
    ingredient_countries = {}
    for row in ingredient_data:
        # logger.info(f"Other Ingredient {row['other_ing']}")
        # other_ingredient = row['other_ing']
        ingredient_name = row['ing_name']
        # if other_ingredient:
        #     other_name = row['ing_name']
        #     others.setdefault(other_name, set()).add(row['source'])
        #     # logger.info(f'Adding {row["ing_name"]} to others')
        #     continue
        # if ingredient_name in ['Maltodextrin', 'FOS']:
        #     continue
        if ingredient_name in ingredient_countries:
            ingredient_countries[ingredient_name].add(row['country_origin'])
        else:
            ingredient_countries[ingredient_name] = {row['country_origin']}

    ## Iterate Through the Collected Data
    for ingredient, countries in ingredient_countries.items():
        combined_country_data = "/".join(countries)
        dataset.append([Paragraph(ingredient, ing_style), combined_country_data])

    # other_data = {}
    # # Fixing "Other Ingredients" Section
    # other_data = {key: f"{key} (from {', '.join(sorted(value))})" for key, value in others.items()}
    # others_data = list(other_data.values())
    # logger.info(f'others {others}')
    w, h = A4
    lineSpacing = 20

    file_name = f"{company}_{product_name_footer}_COO3_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date Section
    y = y - lineSpacing
    c.setFont('Cambria-Regular', 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Section
    y -= lineSpacing * 3
    product_style = ParagraphStyle('product_style',
                                   fontName='Cambria-Bold',
                                   fontSize=30,
                                   alignment=TA_RIGHT)
    if symbol_id == 0:
        # Directly use the product name with HTML tags for bold and symbols
        product_name = f"{product_name.replace(chr(int(symbol_code, 16)), '')}"
    elif symbol_id == 1 or symbol_id == 4:
        # Use bold and plain product name (without modifications)
        product_name = f"{product_name}"
    else:
        # Combine product name and symbol using HTML tags for styling
        product_name = f"{product_name.replace(chr(int(symbol_code, 16)), '')}<sup>{symbol}</sup>"

    p = Paragraph(product_name, product_style)
    w, h = p.wrap(w, h)
    p.drawOn(c, w - 30 - w, y - h)

    y = y - h - lineSpacing * 2
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "CERTIFICATE OF ORIGIN"
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
                                fontSize=11,
                                textColor=colors.black,
                                alignment=TA_CENTER,
                                justifyBreaks=1,
                                justifyLastLine=0)

    text = "The Company certifies that the <b>Country of Origin</b> of the ingredients in this product is as follows:"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    ### INGREDIENTS AND COUNTRY OF ORIGIN TABLE ###
    table_style = TableStyle([('FONTNAME', (0, 0), (1, 0), 'Cambria-Bold'),
                              ('FONTSIZE', (0, 0), (1, 0), 12, colors.black),
                              ('FONTNAME', (0, 1), (-1, -1), 'Cambria-Regular'),
                              ('FONTSIZE', (0, 1), (-1, -1), 10, colors.black),
                              ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                              ('LEFTPADDING', (0, 0), (-1, -1), 10),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                              ('TOPPADDING', (0, 0), (-1, -1), 3)])
    # y = y - lineSpacing
    t = Table(dataset, style=table_style, colWidths=[150, 200], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, tw / 2, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y -= th + 30

    ### END TABLE ###
    style_other = ParagraphStyle("Other_Text",
                                 fontName="Cambria-Italic",
                                 fontSize=8,
                                 textColor=colors.black,
                                 alignment=TA_CENTER,
                                 leftIndent=0)

    # if others_data:
    #     text = "<b>Other ingredients:</b> Product standardized in a base of " + ", ".join(others_data)
    #     p = Paragraph(text.strip(), style_other)
    #     p.wrapOn(c, w, h)
    #     p.drawOn(c, 0, y - h)

    # y = y - lineSpacing

    style_other = ParagraphStyle("Other_Text",
                                 fontName="Cambria-Regular",
                                 fontSize=11,
                                 textColor=colors.black,
                                 strikeColor=0.4,
                                 alignment=TA_LEFT,
                                 leftIndent=40)
    text = "<b>Country of Processing</b> is <u>USA</u>."
    p = Paragraph(text, style_other)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 30, y - h)  # Adjusting the Y-position to ensure proper alignment

    # c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0, 0, 0, 1)
    # c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_COO3_01A0")
    para_style = ParagraphStyle(
        name="RightAlign",
        fontName="Cambria-Regular",
        fontSize=8,
        textColor=colors.black,
        alignment=TA_RIGHT,
        rightIndent=30  # similar to w - 30
    )
    # c.setFillColorRGB(0, 0, 0, 1)
    product_name = product_name.replace(chr(int(symbol_code, 16)), '').replace(' ', '')
    para_text = f"{product_name}_COO3_01A0"
    paragraph = Paragraph(para_text, style=para_style)

    # Wrap and draw
    w, h = paragraph.wrapOn(c, w, h)
    paragraph.drawOn(c, 0, pfh + 1)
    c.showPage()
    c.save()

    return file_path, file_name
