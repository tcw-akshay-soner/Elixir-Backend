import logging
import os
# import structureddatastore as sds
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

from src.template_file import letterhead
from src.engine.pharma_data import fetch_product, fetch_declaration_data
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

async def generate_file_name(company, temp, product_id):
    
    product_data = await fetch_product(product_id)
    # product_name = product_data[0]['product_name'] if product_data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']

    if symbol_id:
        product_name_footer = product_name.replace(' ', '').replace(chr(int(symbol_code, 16)), '')
    else:
        product_name_footer = product_name.replace(' ', '')

    if temp == 'packaging':
        return f"{company}_{product_name_footer}_Packaging_01A0.pdf", product_data, product_name_footer
    elif temp == 'preservative':
        return f"{company}_{product_name_footer}_Preservative_01A0.pdf", product_data, product_name_footer
    elif temp == 'residual solvent':
        return f"{company}_{product_name_footer}_Residual Solvent_02A0.pdf", product_data, product_name_footer
    elif temp == 'wada':
        return f"{company}_{product_name_footer}_WADA_01A0.pdf", product_data, product_name_footer
    else:
        raise ValueError(f"Invalid template type {temp}.")

async def check_compliance(declaration_data, field):
    for row in declaration_data:
        if row[field] in ['Yes']:
            return True
    return False

async def create_template_ppr(date, temp_dir, company, product_id, temp):
    # Validate input and create the file path
    if not os.path.exists(temp_dir):
        raise FileNotFoundError(f"Directory {temp_dir} does not exist.")
    
    file_name, product_data, product_name_footer = await generate_file_name(company, temp, product_id)
    file_path = os.path.join(temp_dir, file_name)
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    logger.info(f"Generating {temp} template for product: {product_name}")

    # Fetch declaration data for compliance checks
    declaration_data = await fetch_declaration_data(product_id)

    # Check residual solvent compliance
    if temp == 'residual solvent':
        residual_solvent = await check_compliance(declaration_data, 'residual_solvent')
        if residual_solvent:
            raise ValueError("File generation failed due to residual solvent presence.")
    elif temp == 'wada':
    # Check WADA compliance
        wada_compliance = await check_compliance(declaration_data, 'wada_compliance')
        if not wada_compliance:
            raise ValueError("File generation failed due to WADA non-compliance.")
    elif temp == 'preservative':
        # Check preservative compliance
        preservative = await check_compliance(declaration_data, 'preservative')
        if preservative:
            raise ValueError("Data Not Provided by the Vendor")
    # elif temp == 'packaging':
    #     packaging = await check_compliance(declaration_data, 'packaging')
    #     if packaging:
    #         raise ValueError("File generation failed due to packaging presence.")

    c = canvas.Canvas(file_path)
    
    w, h = A4
    lineSpacing = 20

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
    if temp == 'packaging':
        text_data = ("PACKAGING DECLARATION",
                        "The primary packaging is 25 kg polyethylene bags. Bags are certified by the manufacturer to be compliant with 21 CFR 177.1520 (c) (2.1).")
    if temp == 'preservative':
        text_data = ("PRESERVATIVE FREE STATEMENT",
                        "The company certifies that no preservatives are used in the manufacturing of the listed product.")
    if temp == 'residual solvent':
        text_data = ("RESIDUAL SOLVENT STATEMENT",
                        "The company does not employ the use of solvents during the manufacturing of above-mentioned product(s). However, the supplier of some components does declare that solvents are used in the processing and isolation of these raw materials. During the manufacturing of the above-mentioned product(s), these ingredients are only added in minor amounts – the presence of solvents is dramatically diminished and are therefore not tested for in the final blend.")
    if temp == 'wada':
        text_data = ("WADA STATEMENT",
                        "The company certifies that to the best of our knowledge above mentioned product(s) is not on prohibited substance list published by World Anti-Doping agency (WADA).")

    y = y - lineSpacing * 4
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title, content = text_data
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
                                alignment=TA_JUSTIFY,
                                leading=15,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leftIndent=30,
                                rightIndent=30)

    p = Paragraph(content, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    if temp == "packaging":
        c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Packaging_01A0")
    elif temp == "preservative":
        c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Preservative_01A0")
    elif temp == "residual solvent":
        c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Residual Solvent_02A0")
    elif temp == "wada":
        c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_WADA_01A0")
    c.showPage()
    c.save()
    logger.info(f"PDF generated successfully: {file_path}")
    return file_path, file_name