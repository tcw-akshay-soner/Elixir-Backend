import logging
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.template_file import letterhead
from src.engine.pharma_data import fetch_product

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

async def create_template_lotcode(date, temp_dir, company, product_id):

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
    w, h = A4
    lineSpacing = 20

    file_name = f"{company}_{product_name_footer}_lotcode_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date Section
    y = y - lineSpacing
    c.setFont('Cambria-Regular', 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Section
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
    y = y - lineSpacing * 4
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "Lot Code Identification"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing

    ### BODY TEXT SECTION ###

    style_lot_code = ParagraphStyle("Lot_Text",
                                fontName="Cambria-Regular",
                                fontSize=12,
                                alignment=TA_JUSTIFY,
                                leading=15,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leftIndent=30,
                                rightIndent=30)

    lot_code = '<font color="blue">E</font><font color="red">2</font><font color="green">01</font><font color="purple">AN1001</font>'
    p = Paragraph(lot_code, style_lot_code)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)

    y = y - h - lineSpacing
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=11,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                leading=15,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                bulletFontSize=12,
                                bulletIndent=30,
                                leftIndent=50,
                                rightIndent=30)

    text_data = ['The first letter shown in blue indicates the type of product.',
                 'The first number shown in red provides the year of manufacturing; the number <font color="red">2</font> indicates that it was made in 202<font color="red">2</font>.',
                 'The second number shown in green provides the month of manufacturing; the number <font color="green">01</font> indicates that it was made in the 1st month (January).',
                 'The next two alphabets and the last 4 numbers, shown in purple, are internal specifications dealing with product classification and such.']

    for text in text_data:
        p = Paragraph(text, style_body, bulletText='•')
        w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment
        y = y - h - lineSpacing

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Lot Code_02A0")
    c.showPage()
    c.save()
    
    return file_path, file_name
