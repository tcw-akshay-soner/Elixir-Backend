import logging
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.engine.pharma_data import fetch_product, fetch_declaration_data
from src.engine.strip_html_tags import strip_html_tags
from src.template_file import letterhead

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


async def create_template_gluten(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    # product_name = product_data[0]['product_name'] if product_data else "N/A"
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']

    product_name_footer = strip_html_tags(product_name.replace(' ', ''))
    if symbol_id:
        product_name_footer = product_name_footer.replace(chr(int(symbol_code, 16)), '')

    ## Declaration Data ##
    gluten_status = "Gluten free"
    declared_gluten = "No"
    allergen_ferm = "No"
    declaration_data = await fetch_declaration_data(product_id)
    for row in declaration_data:
        if row["gluten_status"] == 'Gluten containing':
            # gluten_status = 'Gluten containing'
            code = "01D0"
        elif row["gluten_status"] == 'Gluten free':
            code = "01A0"
            # if row["declared_allergen"] == "No" and (row["allergen_fermentation"] == "No" or row["allergen_fermentation"] == "NA"):
            #     declared_gluten = "No"
            #     allergen_ferm = "No"
            # code = "01A0"
            # elif row["declared_allergen"] == "No" and "Yes" in row["allergen_fermentation"]:
            #     declared_gluten = "No"
            #     allergen_ferm = "Yes"
            #     # code = "01C0"
    # if gluten_status == "Gluten containing":
    #     code = "01D0"
    # elif gluten_status == "Gluten free":
    #     if declared_gluten == "No" and allergen_ferm == "No":
    #         code = "01A0"
    #     elif declared_gluten == "No" and allergen_ferm == "Yes":
    #         code = "01C0"

    # c = canvas.Canvas(f"template/product_Gluten_{code}.pdf")  # Product Name From Database
    file_name = f"{company}_{product_name_footer}_Gluten_{code}.pdf"
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
    y -= lineSpacing * 3
    product_style = ParagraphStyle('product_style',
                                   fontName='Cambria-Bold',
                                   fontSize=30,
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

    y = y - h - lineSpacing * 2
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Non-GMO statements
    y = y - lineSpacing * 3

    ### Document Selection E.G. 01A0, 01B0 ...###
    if code == '01A0':
        text_data = [('GLUTEN FREE STATEMENT',
                      "The product listed above is to the best of our knowledge Gluten Free based on testing and/or "
                      "certifications by the manufacturer."
                      "<br/><br/><br/>* ‘Gluten Free’ is, as defined by the US FDA, less than 20 ppm using the "
                      "S-ELISA test methodology.")]
    # elif code == '01B0': text_data = [('FERMENTATION GLUTEN-FREE STATEMENT', "This product contains an ingredient
    # that has been produced by fermentation. To the best of our knowledge, " "gluten-containing grains were neither
    # used as a nutrient in the fermentation media, nor were they added to the product in its final form.")] elif
    # code == '01C0': text_data = [('STATEMENT ON GLUTEN', "This product contains an ingredient that has been
    # produced by fermentation. Although gluten-containing grains were not added to the product in its final form,
    # a gluten-containing grain was used as a nutrient in the fermentation media." " The gluten-containing grain is
    # understood to be substantially consumed during fermentation and removed through subsequent purification steps."
    # " When tested by an ELISA methodology, this product should result in less than 20 ppm of gluten. ")]
    elif code == '01D0':
        text_data = [('STATEMENT ON GLUTEN',
                      "The product listed above, to the best of our knowledge, may contain gluten. The company does "
                      "not add any gluten during the manufacturing of above-mentioned product(s)."
                      "However, the supplier of some components does declare that gluten may be present in the raw "
                      "material.")]

    for title, content in text_data:  # Iteration for title and content in text data according to the code provided
        # Set title font color to black
        c.setFont('Cambria-Bold', 14)
        c.setFillColorRGB(0, 0, 0, 1)  # Ensure black color for the title
        c.drawCentredString(w / 2, y, title)
        text_width = c.stringWidth(title, "Cambria-Bold", 14)
        x = (w / 2) - (text_width / 2)  # For Underline in the title
        c.setStrokeColorRGB(0, 0, 0, 1)
        c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)  # Underline in the title
        y -= 20

        # Add content paragraph
        style_normal = ParagraphStyle("Body_Text",
                                      fontName="Cambria-Regular",
                                      fontSize=11,
                                      textColor=colors.black,
                                      alignment=TA_JUSTIFY,
                                      justifyBreaks=1,
                                      justifyLastLine=0,
                                      leading=15,
                                      leftIndent=30,
                                      rightIndent=30)
        p = Paragraph(content, style_normal)
        p_width, p_height = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - p_height)  # Adjusting the Y-position to ensure proper alignment
        y -= (p_height + 40)

    # c.setFont('Cambria-Regular', 8)
    # # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    # c.setFillColorRGB(0, 0, 0, 1)
    # if code == '01D0':
    #     c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Gluten Status_01D0")
    # else:
    #     c.drawRightString(w - 30, pfh + 6, f'{product_name_footer}_Gluten Free_{code}')
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
    para_text = f"{product_name}_Microorganism_01A0"
    if code == '01D0':
        para_text = f"{product_name}_Gluten Status_01D0"
    else:
        para_text = f"{product_name}_Gluten Free_{code}"
    paragraph = Paragraph(para_text, style=para_style)

    # Wrap and draw
    w, h = paragraph.wrapOn(c, w, h)
    paragraph.drawOn(c, 0, pfh + 1)

    c.showPage()
    c.save()

    return file_path, file_name
