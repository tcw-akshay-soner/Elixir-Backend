import os.path
import warnings
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, TableStyle, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.template_file import letterhead
from src.engine.pharma_data import fetch_declaration_data, fetch_product
from src.engine.strip_html_tags import strip_html_tags

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
warnings.filterwarnings("ignore")

# async def check_compliance(declaration_data, field):
#         for row in declaration_data:
#                 if row[field] in ["No", ""]:
#                         return True
#         return False

async def create_template_birradiation(date, temp_dir, company, product_id):
    # Fetch product data
    product_data = await fetch_product(product_id)
    # product_name = product_data[0]["product_name"] if product_data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

    # Fetch declaration data
    file_name = f"{company}_{product_name_footer}_Irradiated_01B0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    declaration_data = await fetch_declaration_data(product_id)

    # if temp == 'b_irradiated':
    #         b_irradiated = await check_compliance(declaration_data, 'irradiated')
    #         if b_irradiated:
    #                 raise ValueError("File generation failed due to The listed product's ingredients may not be irradiated.")

    w, h = A4
    lineSpacing = 20
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    # Date
    y = y - lineSpacing / 2
    c.setFont("Cambria-Regular", 11)
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
    c.setFont("Cambria-Regular", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.7)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 4
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "IRRADIATION STATEMENT"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing * 2

    ### BODY TEXT SECTION ###
    style_body = ParagraphStyle(
        "Body_Text",
        fontName="Cambria-Regular",
        fontSize=11,
        textColor=colors.black,
        alignment=TA_JUSTIFY,
        justifyBreaks=1,
        justifyLastLine=0,
        leading=15,
        leftIndent=40,
        rightIndent=40,
    )

    text = (
        "The above listed product(s) is not subjected to irradiation during the manufacturing process. The vendor("
        "s) of the ingredients used in the above listed product certify that the ingredient(s) may have been "
        "irradiated. The above listed product may be an irradiated product."
    )
    p = Paragraph(text, style_body)
    w, h = p.wrap(
        w, h
    )  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    ## FOOTER TAG ###
    c.setFont("Cambria-Regular", 8)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Irradiated_01B0")
    c.showPage()
    c.save()

    return file_path, file_name
