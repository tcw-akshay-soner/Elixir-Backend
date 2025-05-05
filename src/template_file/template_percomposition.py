import os
import warnings
import logging
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_product, fetch_composition, fetch_ingredient_data
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

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

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
    ing_style = ParagraphStyle('ing_style',
                               fontName='Cambria-Regular',
                               fontSize=10,
                               alignment=TA_LEFT)
    others = {}

    ingredients_compositions = {}
    for row in ing_data:
        # other_ingredient = row['other_ing']
        ingredient_name = row['ing_name']
        ing_symbol_id = row['symbol_id']       ## Ingredient Symbol details
        ing_symbol_code = row['symbol_code']
        ing_symbol = row['symbol']
        if ing_symbol_id == 0:
            # Directly use the product name with HTML tags for bold and symbols
            ingredient_name = f"{ingredient_name.replace(chr(int(ing_symbol_code, 16)), '')}"
        elif ing_symbol_id == 1:
            # Use bold and plain product name (without modifications)
            ingredient_name = f"{ingredient_name}"
        else:
            # Combine product name and symbol using HTML tags for styling
            ingredient_name = f"{ingredient_name.replace(chr(int(ing_symbol_code, 16)), f'<sup>{ing_symbol}</sup>')}"
        # if other_ingredient:
        #     other_name = row['ing_name']
        #     soup = BeautifulSoup(row['source'], "html.parser")
        #             if soup.find('br'):
        #                 logger.info("Found it")
        #                 source = row['source'].replace('<p><br></p>', "")
        #                 logger.info(source)
        #                 others.setdefault(other_name, set()).add(source)
        #             else:
        #                 others.setdefault(other_name, set()).add(row['source'])
        #     continue
        if ingredient_name in ingredients_compositions:
            ingredients_compositions[ingredient_name].add(row['alpha_composition'])
        else:
            ingredients_compositions[ingredient_name] = {row['alpha_composition']}

    ## Iterate Through the Collected Data
    combined_composition_data = set()
    for ingredient, compositions in ingredients_compositions.items():
        combined_composition_data = "/".join(compositions)
        dataset.append([Paragraph(ingredient, ing_style), combined_composition_data])

    # other_data = {}
    # "Other Ingredients" Section
    #     other_data = {
    #         key: f"{key} (from {', '.join(sorted({v.strip() for v in value if v.strip()}))})"
    #         if any(v.strip() for v in value) else f"{key}"
    #         for key, value in others.items()
    #     }
    # others_data = list(other_data.values())

    file_name = f"{company}_{product_name_footer}_%Composition_01A0.pdf"
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
    y -= lineSpacing
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
        product_name = f"{product_name.replace(chr(int(symbol_code, 16)), f'<sup>{symbol}</sup>')}"

    p = Paragraph(product_name, product_style)
    w, h = p.wrap(w, h)
    p.drawOn(c, w - 30 - w, y - h)

    y = y - h - lineSpacing*2
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    c.drawCentredString(w / 2, y, "COMPOSITION STATEMENT")
    text_width = c.stringWidth("COMPOSITION STATEMENT", "Cambria-Bold", 14)

    ## Title underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)

    ### BODY TEXT SECTION ###
    y -= lineSpacing*0.5
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
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
                              ('TOPPADDING', (0, 0), (-1, -1), 1.5)])

    t = Table(dataset, style=table_style, colWidths=[250, 150], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, tw / 3, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y = y - th - 20
    ### END ###
    # Draw special ingredients section if present
    # style_other = ParagraphStyle("Other_Text",
    #                              fontName="Cambria-Italic",
    #                              fontSize=8,
    #                              textColor=colors.black,
    #                              strikeColor=0.4,
    #                              alignment=TA_CENTER)
    #
    # if others_data:
    #     text = "<b>Other ingredients:</b> Product standardized in a base of " + ", ".join(others_data)
    #     p = Paragraph(text.strip(), style_other)
    #     p.wrapOn(c, w, h)
    #     p.drawOn(c, 0, y - h)

    # y = y - lineSpacing
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

    para_style = ParagraphStyle(
        name="RightAlign",
        fontName="Cambria-Regular",
        fontSize=8,
        textColor=colors.black,
        alignment=TA_RIGHT,
        rightIndent=30  # similar to w - 30
    )

    product_name = product_name.replace(chr(int(symbol_code, 16)), '').replace(' ', '')
    para_text = f"{product_name}_%Composition_01A0"
    paragraph = Paragraph(para_text, style=para_style)

    # Wrap and draw
    w, h = paragraph.wrapOn(c, w, h)
    paragraph.drawOn(c, 0, pfh + 1)
    c.showPage()
    c.save()

    return file_path, file_name
