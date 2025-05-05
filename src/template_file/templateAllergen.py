import os.path
import re

import warnings
import logging

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, TableStyle, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)
async def create_template_allergen(date, temp_dir, company, product_id):
    
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

    declaration_data = await fetch_declaration_data(product_id)
    allergen_map = {
        "wheat": "No",
        "eggs": "No",
        "crustaceans_shell_fish": "No",
        "fish": "No",
        "milk": "No",
        "tree_nuts": "No",
        "peanuts": "No",
        "soy": "No",
        "sesame_seeds": "No",
        "celery": "No",
        "barley_oats_rye_spelt": "No",
        "orange_kiwi_peaches_apples": "No",
        "mushrooms": "No",
        "mustard": "No",
        "lupin": "No",
        "molluscs": "No",
        "sulfur": "No"
    }

    # Update allergen values based on declaration data
    for row in declaration_data:
        for allergen in allergen_map:
            if row.get(allergen) == 'Yes':
                allergen_map[allergen] = "Yes"

    # Determine code based on sulfur content
    # code = '02B0' if allergen_map['sulfur'] == 'Yes' else '02A0'

    code = '02A0'  # Default code
    if allergen_map['eggs'] == 'Yes':
        code = '02C0'
        if allergen_map['milk'] == 'Yes':
            code = '02D0'
    elif allergen_map['crustaceans_shell_fish'] == 'Yes':
        code = '02E0'
    elif allergen_map['wheat'] == 'Yes':
        code = '02F0'
    elif allergen_map['barley_oats_rye_spelt'] == 'Yes':
        code = '02G0'

    file_name = f"{company}_{product_name_footer}_Allergen_{code}.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)
    w, h = A4
    lineSpacing = 20

    ### HEADER ###
    ## Logo
    mask = [0, 2, 40, 42, 136, 139]

    if company == 'SEB':
        c.drawImage('src/data/sebLogo.jpg', 30, 750, mask=mask, height=65, width=190)
        y = h - 70 - lineSpacing
        c.setFont('Cambria-Regular', 14)
        c.setFillColorRGB(0.7, 0.7, 0.7, 0.7)
        c.drawRightString(w - 50, y, "Proprietary and Confidential")
        y = y - lineSpacing
        ## Header Line
        c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
        c.line(30, y, 565, y)
    elif company == 'EI':
        c.drawImage('src/data/eiLogo.png', 30, 730, mask=mask, height=90, width=270)
        y = h - 80 - lineSpacing
        c.setFont('Cambria-Regular', 14)
        c.setFillColorRGB(0.7, 0.7, 0.7, 0.7)
        c.drawRightString(w - 50, y, "Proprietary and Confidential")
        y = y - lineSpacing
    ### HEADER ###

    ## Title
    y = y - lineSpacing
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    c.drawCentredString(w / 2, y, "Allergen Information")
    text_width = c.stringWidth("Allergen Information", "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)

    ## Date
    y = y - lineSpacing * 2
    c.setFont("Cambria-Regular", 12)
    c.drawRightString(w - 50, y, date)

    ### BODY TEXT SECTION ###
    ## TABLE ##
    ## Allergen alphabet table according to code '01A0', '01B0'...

    para_style = ParagraphStyle(
        'ProductStyle',
        fontName='Cambria-Bold',
        fontSize=12,
        textColor=colors.black,
        leading=14,
    )

    # Format HTML-based text
    if symbol_id == 0:
        product_name_clean = product_name.replace(chr(int(symbol_code, 16)), '')
        text_html = f"Product: {product_name_clean}"
    elif symbol_id == 1 or symbol_id == 4:
        text_html = f"Product: {product_name}"
    else:
        product_name_clean = product_name.replace(chr(int(symbol_code, 16)), f'<super>{symbol}</super>')
        text_html = f"Product: {product_name_clean}"

    # Create and draw Paragraph
    p = Paragraph(text_html, para_style)
    pw, ph = p.wrapOn(c, w - 100, y)
    p.drawOn(c, 50, y)  # 50 is x, adjust y accordingly

    y = y - ph
    style = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('GRID', (0, 0), (0, -1), 1, colors.black),
                        ('GRID', (-1, 0), (-1, -1), 1, colors.black),
                        ('FONTNAME', (0, 0), (-1, -1), 'Cambria-Regular'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10, colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                        ('TOPPADDING', (0, 0), (-1, -1), 5)])

    style_text = ParagraphStyle("text",
                                fontName="Cambria-Regular",
                                fontSize=10,
                                alignment=TA_LEFT)
    ## Alphabet Template 'A'
    # Shared allergen data template
    wheat = Paragraph('<b>Wheat</b> and products thereof;', style_text)
    eggs = Paragraph('<b>Egg</b> and products thereof;', style_text)
    crustaceans_shell_fish = Paragraph('<b>Crustaceans</b> or <b>Shell-Fish</b>', style_text)
    fish = Paragraph('<b>Fish</b> and products thereof;', style_text)
    milk = Paragraph('<b>Milk</b> and products thereof;', style_text)
    tree_nuts = Paragraph('''<b>Tree Nuts</b> \nAlmonds (<i>Amygdalus communis</i> L.), Brazil nut (<i>Bertholletia 
    excelsa</i>), Cashew (<i>Anacardium occidentale</i>), \nHazelnut (<i>Corylus avellana</i>), Macadamia nut and 
    Queensland nut (<i>Macadamia ternifolia</i>), \nPecan nut (<i>Carya illinoiesis</i>), Pistachio nut (<i>Pistaca 
    vera</i>), Walnut (<i>Juglans regia</i>)''', style_text)
    peanuts = Paragraph('<b>Peanuts</b>', style_text)
    soybean_and_products = Paragraph('<b>Soybean</b> and products thereof;', style_text)
    sesame_seeds = Paragraph('<b>Sesame seed</b>', style_text)
    celery = Paragraph('Celery', style_text)
    barley_and_products = Paragraph('Barley \nOats \nRye \nSpelt', style_text)
    orange_kiwi_peaches_apples = Paragraph('Orange \nKiwi \nPeaches \nApples', style_text)
    mushrooms = Paragraph('Mushrooms', style_text)
    mustard = Paragraph('Mustard', style_text)
    lupin = Paragraph('Lupin', style_text)
    molluscs = Paragraph('Molluscs', style_text)
    data1 = [wheat, eggs, crustaceans_shell_fish, fish, milk, tree_nuts, peanuts, soybean_and_products, sesame_seeds,
             celery, barley_and_products, orange_kiwi_peaches_apples, mushrooms, mustard, lupin, molluscs]

    # Copy allergen values to `data2` based on `allergen_map`
    data2 = [
        allergen_map["wheat"], allergen_map["eggs"], allergen_map["crustaceans_shell_fish"],
        allergen_map["fish"], allergen_map["milk"], allergen_map["tree_nuts"],
        allergen_map["peanuts"], allergen_map["soy"], allergen_map["sesame_seeds"],
        allergen_map["celery"], allergen_map["barley_oats_rye_spelt"], allergen_map["orange_kiwi_peaches_apples"],
        allergen_map["mushrooms"], allergen_map["mustard"], allergen_map["lupin"],
        allergen_map["molluscs"]
    ]

    # If sulfur is present, append specific statement to both data1 and data2
    if code == '02B0':
        data1.insert(-1, 'Sulfur at concentrations of more than 10 mg/kg - expressed as SO2')
        data2.insert(-1, allergen_map["sulfur"])

    ## For Table Creation
    data = [[item1, item2] for item1, item2 in zip(data1, data2)]
    t = Table(data, style=style, colWidths= [450, 50])  # Creating Table with the available data
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, (w - tw) / 2, y - th)  # Adjusting the Y-position to ensure proper alignment


    y = y - th - lineSpacing
    point_style = ParagraphStyle("point_Text",
                                 fontName="Cambria-Regular",
                                 fontSize=8,
                                 textColor=colors.black,
                                 alignment=TA_JUSTIFY,
                                 justifyBreaks=1,
                                 justifyLastLine=0,
                                 leading=14,
                                 leftIndent=70,
                                 rightIndent=70)

    text_data = [("1.",
                  " For certain fermentation-derived ingredients, soy, milk and gluten-containing grains may be used in the fermentation media but are not an added ingredient to the product in its final form."),
                 ("2.",
                  " For certain products, soy, milk, egg (lysozyme), crustacean and gluten-containing grain products may be processed in the same facility and on the same machines.")]

    for number, text in text_data:
        c.setFont("Cambria-Regular", 8)
        c.drawString(60, y + 6, number)
        text = f"{text}"
        p = Paragraph(text, point_style)
        bw, bh = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - bh / 2)  # Adjusting the Y-position to ensure proper alignment
        y -= bh

    ### FOOTER ###
    if company == 'SEB':
        c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
        c.line(30, 100, 565, 100)
    elif company == 'EI':
        mask = [0, 2, 40, 42, 136, 139]
        c.drawImage('src/data/EI_footer.jpg', 330, -105, mask=None, height=250, width=250)
        c.setFillColorRGB(0, 0, 0, 1)

    style_footer = ParagraphStyle("footer",
                                  fontName="Cambria-Regular",
                                  fontSize=8,
                                  textColor=colors.black,
                                  alignment=TA_JUSTIFY,
                                  justifyBreaks=1,
                                  justifyLastLine=0,
                                  leftIndent=30,
                                  rightIndent=30)

    footer_text = """The information is presented in good faith as of the date set forth herein and valid for one 
    year, and we assume no obligation to update this statement. Nothing herein is intended as legal or regulatory 
    advice. The information herein is presented solely for your independent consideration, review and 
    verification. This statement does not constitute a representation or warranty regarding the product, and we shall 
    have no liability regarding this statement or your use of the information contained herein."""

    p = Paragraph(footer_text, style_footer)
    pfw, pfh = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, pfh)  # Adjusting the Y-position to ensure proper alignment

    # c.setFont('Cambria-Regular', 8)
    # # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    # c.setFillColorRGB(0, 0, 0, 1)
    # c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Allergen_{code}")
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
    para_text = f"{product_name}_Allergen_{code}"
    paragraph = Paragraph(para_text, style=para_style)

    # Wrap and draw
    w, h = paragraph.wrapOn(c, w, h)
    paragraph.drawOn(c, 0, pfh + 1)
    c.showPage()
    c.save()

    return file_path, file_name
