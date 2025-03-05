import os.path
import warnings
import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, TableStyle, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.template_file import letterhead
from src.engine.pharma_data import fetch_declaration_data, fetch_product

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

    if symbol_id:
        product_name_footer = product_name.replace(' ', '').replace(chr(int(symbol_code, 16)), '')
    else:
        product_name_footer = product_name.replace(' ', '')

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
    y = y - lineSpacing * 4
    if symbol_id == 1 or symbol_id == 4:
        c.setFont('Cambria-Bold', 30)
        c.drawRightString(w - 30, y, product_name)  # Placeholder for product name # Placeholder for symbol name
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
