import os
import warnings
import logging
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_product, fetch_composition, fetch_ingredient_data
from src.template_file import letterhead
from src.engine.strip_html_tags import strip_html_tags

from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# Set up ReportLab
stylesheet = getSampleStyleSheet()
warnings.filterwarnings('ignore')


async def create_template_composition(date, temp_dir, company, product_id):
    ## Fetch Product Data ##
    product_data = await fetch_product(product_id)

    product_name, symbol_id, symbol_code, symbol = "N/A", None, None, ""
    if product_data:
        product_name = product_data[0]['product_name']
        symbol_id = product_data[0]['symbol_id']
        symbol_code = product_data[0]['symbol_code']
        symbol = product_data[0]['symbol']

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

    ## Fetch Composition Data ##
    ingredients = []
    # composition = await fetch_composition(product_id)
    ing_data = await fetch_ingredient_data(product_id)
    others = {}
    for row in ing_data:
        logger.info(f"Other Ingredient {row['other_ing']}")
        other_ingredient = row['other_ing']
        if other_ingredient:
            other_name = row['ing_name']
            others.setdefault(other_name, set()).add(row['source'])
            # logger.info(f'Adding {row["ing_name"]} to others')
            continue
        if row['ing_name'] not in ingredients:
            ingredients.append(row['ing_name'])
        logger.info(row['ing_name'])
    ingredients = ",".join(ingredients)
    logger.info(ingredients)
    other_data = {}
    # Fixing "Other Ingredients" Section
    other_data = {key: f"{key} (from {', '.join(sorted(value))})" for key, value in others.items()}
    others_data = list(other_data.values())

    w, h = A4
    line_spacing = 20
    file_name = f"{company}_{product_name_footer}_Composition_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date
    y -= line_spacing
    c.setFont("Cambria-Regular", 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Name Display
    y -= line_spacing * 3
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

    y = y - h - line_spacing * 2
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y -= line_spacing * 3
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "COMPOSITION STATEMENT"
    c.drawCentredString(w / 2, y, title)

    ## Body Text
    y -= line_spacing
    c.setFont('Cambria-Regular', 10)
    text = "The above-mentioned product typically contains the following active components:"
    c.drawString(100, y, text)

    ## Bullet List of Ingredients
    bullet_indent = 30
    line_spacing = 15
    x = 100
    y = 500
    if len(ingredients) > 1:
        ingredients = ingredients.split(',')
    maltodextrin = False
    fos = False

    style1 = ParagraphStyle("txt",
                            fontName="Cambria-Bold",
                            fontSize=10,
                            leading=12,
                            spaceBefore=10,
                            spaceAfter=4
                            )
    for i in ingredients:  # Iteration through ingredients list
        # if i == 'Maltodextrin':
        #     maltodextrin = True
        #     continue
        # elif i == 'FOS':
        #     fos = True
        #     continue
        p = Paragraph(i, style1, bulletText='•')  # Including Paragraph in canvas with bullet text
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, x + bullet_indent, y)  # Adjusting the Y-position to ensure proper alignment
        y -= line_spacing

    # Draw special ingredients section if present
    if others_data:
        text = f"<b>Other ingredients:</b> Product standardized in a base of {', '.join(others_data)}"
        style_other = ParagraphStyle("Other_Text",
                                     fontName="Cambria-Italic",
                                     fontSize=8,
                                     textColor=colors.black,
                                     alignment=TA_JUSTIFY)
        p = Paragraph(text, style_other)
        w, h = p.wrap(w, h)
        p.drawOn(c, x, y - h)

    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Composition_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
