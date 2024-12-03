import logging,os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.engine.pharma_data import fetch_product, fetch_ingredient_data
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_template_bsetse(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"

    ## Ingredient Data ##
    combined_source_type = set()
    ingredient_data = await fetch_ingredient_data(product_id)
    for row in ingredient_data:
        combined_source_type.add(row['source_type'])
    combined_source_type = ",".join(combined_source_type)
    if "Plant" in combined_source_type:
        code = '01A0'  # 'Plant' is present
    else:
        code = '01B0'  # 'Plant' is not present at all

    w, h = A4
    lineSpacing = 20

    file_name = f"{company}_{product_name}_BSE_TSE_{code}.pdf"
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
    title = "BSE/ TSE STATEMENT"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing/2

    ### BODY TEXT SECTION ###
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=11,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leading=15,
                                leftIndent=40,
                                rightIndent=40)
    if code == "01A0":
        text = "The listed product is manufactured using components free of any animal sources and does not contain any animal origin materials."\
                " Thus this material is a BSE/TSE-free product."
    elif code == "01B0":
        text = "The raw materials used to produce the enzymes in this formulation are certified by the manufacturer to be collected from BSE/TSE free area."

    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_BSE_TSE_{code}")
    c.showPage()
    c.save()
    
    return file_path, file_name