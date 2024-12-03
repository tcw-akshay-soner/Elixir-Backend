import logging, os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.engine.pharma_data import fetch_product, fetch_ingredient_data
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_template_COO2(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"

    combined_country_data = set()
    ingredient_data = await fetch_ingredient_data(product_id)
    for row in ingredient_data:
        combined_country_data.add(row['country_origin'])
    combined_country_data = " / ".join(sorted(combined_country_data))

    file_name = f"{company}_{product_name}_COO2_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)  # Product Name From Database
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

    c.setFont('Cambria-Bold', 30)
    c.drawRightString(w - 30, y, product_name)  # Placeholder for product name

    y = y - lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 4
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
                                alignment=TA_JUSTIFY,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leading=15,
                                leftIndent=30,
                                rightIndent=30
                                )

    # text = f"The Company certifies that the <b>Country of Origin</b> is <u><b>{combined_country_data}</b></u> and the <b>Country of Processing</b> is <u><b>USA</b></u> ."
    text = f"The Company certifies that the <b>Country of Origin</b> is <u><b>INDIA</b></u> and the <b>Country of Processing</b> is <u><b>USA</b></u> ."
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_COO2_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
