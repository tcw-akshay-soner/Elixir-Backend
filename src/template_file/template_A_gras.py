import logging
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

from src.engine.pharma_data import fetch_product, fetch_declaration_data
from src.engine.strip_html_tags import strip_html_tags
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()

from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


async def create_template_gras(date, temp_dir, company, product_id):
    product_data = await fetch_product(product_id)
    # product_name = data[0]["product_name"] if data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

    file_name = f"{company}_{product_name_footer}_GRAS_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    declaration_data = await fetch_declaration_data(product_id)

    for row in declaration_data:
        if row["gras"] == "No":
            raise ValueError("File Generation Failed due to 'One or More Ingredient doesn't pass Food Safety.'")
        elif row["gras"] == "NA":
            raise ValueError("File Generation Failed due insufficent data")
    c = canvas.Canvas(file_path)  # Product Name From Database

    w, h = A4
    lineSpacing = 20
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date Section
    y = y - lineSpacing
    c.setFont("Cambria-Regular", 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Section
    # y = y - lineSpacing * 4
    # # c.setFont("Cambria-Bold", 30)
    # # c.drawRightString(w - 30, y, product_name)  # Placeholder for product name
    # if symbol_id == 0:
    #     c.setFont('Cambria-Bold', 30)
    #     c.drawRightString(w - 30, y, product_name.replace(chr(int(symbol_code, 16)), ''))
    # elif symbol_id == 1 or symbol_id == 4:
    #     c.setFont('Cambria-Bold', 30)
    #     c.drawRightString(w - 30, y, product_name)  # Placeholder for product name # Placeholder for symbol name
    # else:
    #     text = product_name
    #     width = c.stringWidth(text, "Cambria-Bold", 30)
    #     charSpace = 0
    #     wordSpace = None
    #     if charSpace:
    #         width += (len(text) - 1) * charSpace
    #     if wordSpace:
    #         width += (text.count(u' ') + text.count(u'\xa0') - 1) * wordSpace
    #     text_object = c.beginText(w - 30 - width, y)
    #     product_name = product_name.replace(chr(int(symbol_code, 16)), '')
    #     text_object.setFont("Cambria-Bold", 30)
    #     text_object.textOut(product_name)
    #     text_object.setRise(6)
    #     text_object.setFont("Cambria-Bold", 30)
    #     text_object.textOut(symbol)
    #     text_object.setRise(0)
    #     c.drawText(text_object)

    y -= lineSpacing * 3
    product_style = ParagraphStyle('product_style',
                                   fontName='Cambria-Bold',
                                   fontSize=30,
                                   alignment=TA_RIGHT)
    if symbol_id == 0:
        product_name = f"{product_name.replace(chr(int(symbol_code, 16)), '')}"
    elif symbol_id == 1 or symbol_id == 4:
        product_name = f"{product_name}"
    else:
        product_name = f"{product_name.replace(chr(int(symbol_code, 16)), '')}<sup>{symbol}</sup>"

    p = Paragraph(product_name, product_style)
    w, h = p.wrap(w, h)
    p.drawOn(c, w - 30 - w, y - h)

    y = y - h - lineSpacing * 2

    # y = y - lineSpacing
    c.setFont("Cambria-Regular", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 4
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "STATEMENT ON GRAS STATUS"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing

    ### BODY TEXT SECTION ###
    style_body = ParagraphStyle(
        "Body_Text",
        fontName="Cambria-Regular",
        fontSize=11,
        textColor=colors.black,
        alignment=TA_JUSTIFY,
        justifyBreaks=1,
        justifyLastLine=0,
        leftIndent=30,
        rightIndent=30,
    )

    text = (
        "The Company certifies that the above-listed product is Generally Recognized as Safe (“GRAS”)"
        " under the Federal Food, Drug and Cosmetic Act if used as directed by the Company. "
    )
    p = Paragraph(text, style_body)
    w, h = p.wrap(
        w, h
    )  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    # product_name_new = product_name.replace(" ","")
    c.setFont("Cambria-Regular", 8)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_GRAS_01A0")
    c.showPage()
    c.save()
    return file_path, file_name
