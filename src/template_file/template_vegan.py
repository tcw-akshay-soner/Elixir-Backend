import logging
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.engine.strip_html_tags import strip_html_tags
from src.template_file import letterhead
from src.engine.pharma_data import fetch_declaration_data, fetch_product

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


async def create_template_vegan(date, temp_dir, company, product_id):
    product_data = await fetch_product(product_id)
    # product_name = data[0]['product_name'] if data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

    file_name = f"{company}_{product_name_footer}_Vegan_02A0.pdf"
    file_path = os.path.join(temp_dir, file_name)

    ## Declaration Data ##
    vegan = "Yes"
    declaration_data = await fetch_declaration_data(product_id)
    for row in declaration_data:
        if row["vegan"] == 'No' or row["vegan"] == "":
            vegan = "No"
    if vegan == "No":
        raise ValueError("File generation failed: One or more ingredients contain non-vegan content.")

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
    y = y - 20

    # y -= lineSpacing * 3
    product_style = ParagraphStyle('product_style',
                                   fontName='Cambria-Bold',
                                   fontSize=25,
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

    y = y - h - lineSpacing * 1.5
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing*2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "VEGAN STATEMENT"
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
    content = "The term “vegan” is not consistently defined by current legislation, and " \
              "each individual customer may have its own interpretation of the term. " \
              "The Company considers “vegan” to mean a vegetarian product which also does not " \
              "contain animal-derived ingredients, like milk, honey and eggs."
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
    text_data = ["There are three potential categories of ingredients for the product:"
                 " (1) purified plant extracts, (2) products from the controlled fermentation of"
                 " microorganisms, and (3) purified animal tissues or animal organs.",
                 "The product is made from ingredients in Categories 1 and/or 2 above (purified plants and/or "
                 "products from the controlled fermentation of microorganisms). The product does not contain any "
                 "ingredients from Category 3 above (purified animal tissues or animal organs).",
                 "The Company is committed to a clean supply chain. We qualify our vendors to certify our ingredients "
                 "to be vegan. But control of every element of the supply chain is not feasible. It is difficult to "
                 "obtain complete assurance from our suppliers that all ingredients were not manufactured using "
                 "animal-derived starting materials. For example, fermented microorganisms may be isolated from "
                 "human, porcine, dairy, plant or unknown sources and may be fed animal-derived nutrients to grow. To "
                 "the extent that any animal-derived material is used, we understand that the science limits the "
                 "risk.  For example, the science does not allow for the carryover of the original components of the "
                 "strain. Animal-derived nutrients should be consumed during the fermentation process and the "
                 "ingredient further undergoes several processing steps to achieve a highly purified product.",
                 "Once the ingredients are in the Company’s control, the Company manufactures the product under the "
                 "strictest cGMP standards. The Company does not add any non-vegan products during the manufacture of "
                 "the product. The Company further maintains tight controls to prevent cross-contamination with "
                 "non-vegan products.",
                 "The Company does not now, nor does it intend to ever, conduct animal testing for the regular "
                 "quality release of the product. We do have a firm policy to conduct appropriate testing for the "
                 "safety and efficacy of the product for our employees, customers, the public and the environment, "
                 "as well as to meet regulatory standards worldwide. When necessary, this may include animal testing. "
                 "If we must conduct animal trials, we adhere to applicable legal and ethical standards for the "
                 "humane treatment of animals."]
    for text in text_data:
        pb = Paragraph(text, style_body, bulletText='•')
        pbw, pbh = pb.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        pb.drawOn(c, 0, y - pbh)  # Adjusting the Y-position to ensure proper alignment
        y = y - pbh

    # c.setFont('Cambria-Regular', 8)
    # # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    # c.setFillColorRGB(0, 0, 0, 1)
    #
    # c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Vegan_02A0")
    para_style = ParagraphStyle(
        name="RightAlign",
        fontName="Cambria-Regular",
        fontSize=8,
        textColor=colors.black,
        alignment=TA_RIGHT,
        rightIndent=30  # similar to w - 30
    )
    # c.setFillColorRGB(0, 0, 0, 1)
    product_name = product_name.replace(chr(int(symbol_code, 16)), '').replace(' ', '')
    para_text = f"{product_name}_Vegan_02A0"
    paragraph = Paragraph(para_text, style=para_style)

    # Wrap and draw
    w, h = paragraph.wrapOn(c, w, h)
    paragraph.drawOn(c, 0, pfh + 3)
    c.showPage()
    c.save()

    return file_path, file_name
