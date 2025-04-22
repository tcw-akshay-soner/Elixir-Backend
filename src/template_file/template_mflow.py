import os.path
import logging
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_product
from src.template_file import letterhead

from rich.logging import RichHandler
import warnings

# Configure RichHandler
logging.basicConfig(
        level="DEBUG",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')


async def create_template_mflow(date, temp_dir, company, product_id):
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

    file_name = f"{company}_{product_name_footer}_MFlow chart_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    w, h = A4
    lineSpacing = 20
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date Section
    y = y - lineSpacing
    c.setFont('Cambria-Regular', 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    # Title
    y = y - lineSpacing * 2
    # Placeholder for product name
    if symbol_id == 0:
        product_name = product_name.replace(chr(int(symbol_code, 16)), '')
        text = f"{product_name} - Manufacturing Flow Chart"
        c.setFont('Cambria-Bold', 14)
        c.drawCentredString(w / 2, y, text)
    elif symbol_id == 1 or symbol_id == 4:
        text = f"{product_name} - Manufacturing Flow Chart"
        c.setFont('Cambria-Bold', 14)
        c.drawCentredString(w / 2, y, text)
    else:
        text = f"{product_name} - Manufacturing Flow Chart"
        width = c.stringWidth(text, "Cambria-Bold", 14)
        charSpace = 0
        wordSpace = None
        if charSpace:
            width += (len(text)-1)*charSpace
        if wordSpace:
            width += (text.count(u' ')+text.count(u'\xa0')-1)*wordSpace
        text_object = c.beginText(w/2 - 0.5*width, y)
        product_name = product_name.replace(chr(int(symbol_code, 16)), '')
        text_object.setFont("Cambria-Bold", 14)
        text_object.textOut(product_name)
        text_object.setRise(6)
        text_object.setFont("Cambria-Bold", 14)
        text_object.textOut(symbol)
        text_object.setRise(0)
        text_object.textOut("- Manufacturing Flow Chart")
        c.drawText(text_object)

    text_width = c.stringWidth(text, "Cambria-Bold", 14)
    # Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    # c.setFont("Cambria-Bold", 14)
    # title = f"{product_name} - Manufacturing Flow Chart"
    # c.drawCentredString(w / 2, y, title)
    # text_width = c.stringWidth(title, "Cambria-Bold", 14)
    y = y - lineSpacing * 3
    ### BODY TEXT SECTION ###
    logger.info(y)
    try:
        mask = [0, 2, 40, 42, 136, 139]
        c.drawImage("src/data/Mflowchart.png", 50, pfh + 100, mask=mask, height=500, width=500)
    except Exception as e:
        logger.error(f"Error drawing MFlow chart: {e}")

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_MFlow Chart_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
