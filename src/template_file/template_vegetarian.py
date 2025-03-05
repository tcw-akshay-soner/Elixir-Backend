import logging
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.template_file import letterhead
from src.engine.pharma_data import fetch_product, fetch_declaration_data

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

stylesheet = getSampleStyleSheet()
warnings.filterwarnings('ignore')


async def create_template_vegetarian(date, temp_dir, company, product_id):

    product_data = await fetch_product(product_id)
    # product_name = data[0]['product_name'] if data else "N/A"
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

    file_name = f"{company}_{product_name_footer}_Vegetarian_02A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    
    ## Declaration Data ##
    vegetarian = "Yes"
    declaration_data = await fetch_declaration_data(product_id)
    for row in declaration_data:
        if row["vegetarian"] == 'No' or row["vegetarian"] == "":
            vegetarian = "No"
    if vegetarian == "No":
        raise ValueError("File generation failed: One or more ingredients contain non-vegetarian content.")
    
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
    y = y - 40
    # c.setFont('Cambria-Bold', 25)
    # c.drawRightString(w - 30, y, product_name)  # Placeholder for product name
    # Placeholder for product name
    if symbol_id == 1 or symbol_id == 4:
        c.setFont('Cambria-Bold', 25)
        c.drawRightString(w - 30, y, product_name)
    else:
        text = product_name
        width = c.stringWidth(text, "Cambria-Bold", 25)
        charSpace = 0
        wordSpace = None
        if charSpace:
            width += (len(text) - 1) * charSpace
        if wordSpace:
            width += (text.count(u' ') + text.count(u'\xa0') - 1) * wordSpace
        text_object = c.beginText(w - 30 - width, y)
        product_name = product_name.replace(chr(int(symbol_code, 16)), '')
        text_object.setFont("Cambria-Bold", 25)
        text_object.textOut(product_name)
        text_object.setRise(6)
        text_object.setFont("Cambria-Bold", 25)
        text_object.textOut(symbol)
        text_object.setRise(0)
        c.drawText(text_object)

    y = y - lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing*2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "VEGETARIAN STATEMENT"
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
                                fontSize=12,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                leading=15,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leftIndent=30,
                                rightIndent=30)
    content = ("The term “vegetarian” is not consistently defined by current legislation, and each individual customer "
                "may have its own interpretation of the term. The Company considers “vegetarian” to mean a product "
                "which may contain plant-derived ingredients and/or certain animal-derived ingredients, like milk, "
                "honey and eggs.")
    p = Paragraph(content, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    y = y - h - lineSpacing
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=12,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                leading=15,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                bulletFontSize=12,
                                bulletIndent=30,
                                leftIndent=50,
                                rightIndent=30)
    text_data = ["There are three potential categories of ingredients for the product: (1) purified plant extracts, "
                    "(2) products from the controlled fermentation of microorganisms, and (3) purified animal tissues or "
                    "animal organs.",
                    "The product is made from ingredients in Categories 1 and 2 above (purified plants and/or products "
                    "from the controlled fermentation of microorganisms). Your Product does not contain any ingredients "
                    "from Category 3 above (purified animal tissue or animal organs)",
                    "The Company is committed to a clean supply chain. We qualify our vendors to certify our ingredients "
                    "to be vegetarian. But control of every element of the supply chain is not feasible. We cannot "
                    "obtain complete assurance from all our suppliers that ingredients from the controlled fermentation "
                    "of microorganisms were not manufactured using starting materials that may be derived from animals. "
                    "For example, fermented microorganisms may be isolated from human, porcine, dairy, plant or unknown "
                    "sources or may be fed animal-derived nutrients to grow. To the extent that any animal-derived "
                    "material is used, we are confident the science does not allow for the carryover of the original "
                    "components of the strain and/or the said material is consumed during the fermentation process and "
                    "the resultant product is further highly purified.",
                    "Once the ingredients are in the Company’s control, the Company manufactures the product under the "
                    "strictest cGMP standards. The Company does not add any non-vegetarian ingredients in its "
                    "manufacture of the product. The Company further maintains tight controls to prevent "
                    "cross-contamination with ingredients/substances that may not be vegetarian.",
                    "The Company does not now, nor does it intend to ever, conduct animal testing for the regular "
                    "quality release of the product. The Company does have a firm policy to conduct appropriate testing "
                    "for the safety and efficacy of the product for our employees, customers, the public and the "
                    "environment, as well as to meet regulatory standards worldwide. When necessary, this may include "
                    "animal testing. If we must conduct animal trials, we adhere to applicable legal and ethical "
                    "standards for the humane treatment of animals."]
    for text in text_data:
        pb = Paragraph(text, style_body, bulletText='•')
        pbw, pbh = pb.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        pb.drawOn(c, 0, y - pbh)  # Adjusting the Y-position to ensure proper alignment
        y = y - pbh

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)

    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Vegetarian_02A0")
    c.showPage()
    c.save()
    
    return file_path, file_name
