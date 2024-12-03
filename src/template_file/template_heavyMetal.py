import logging, os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from src.engine.pharma_data import fetch_product

from src.template_file import letterhead

stylesheet = getSampleStyleSheet()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_template_heavymetal(date, temp_dir, company, product_id, temp):
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"

    if temp == "proposition 65":
        code = "01A0"
    elif temp == "heavy metal":
        code = "01B0"
    else:
        raise ValueError(f"Unknown template type: {temp}")

    file_name = f"{company}_{product_name}_Heavy Metal_{code}.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    w, h = A4
    lineSpacing = 20

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

    if code == '01A0':
        text_data = ('PROPOSITION 65: STATEMENT OF COMPLIANCE',
                     """Under the regulations set forth in the Safe Water and Toxic Enforcement Act [1986] (commonly known as Proposition 65),
                        Specialty Enzymes & Probiotics certifies that material listed above is compliant with the referenced standards released
                        by the Office of Environmental Health Hazard Assessment [March 28, 2014].""")
    elif code == '01B0':
        text_data = ('HEAVY METAL STATEMENT',
                     "")

    title, content = text_data

    ## Title
    y = y - lineSpacing * 4
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
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
                                leftIndent=30,
                                rightIndent=30)

    p = Paragraph(content, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    y = y - h - lineSpacing
    text = "These products contain less than <b>20 ppm (total)</b> of the following heavy metals;" \
           " <b>Pb: < 5 ppm, As: < 5 ppm, Cd: < 1 ppm and Hg: < 1 ppm.</b>"
    p = Paragraph(text,style_body)
    w, h = p.wrap(w, h)
    p.drawOn(c, 0, y - h)

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_Heavy Metal_{code}")
    c.showPage()
    c.save()

    return file_path, file_name
