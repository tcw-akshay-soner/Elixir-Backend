import warnings
import logging
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from src.engine.pharma_data import fetch_product, fetch_ingredient_data
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
warnings.filterwarnings('ignore')


async def create_template_nutritional(date, temp_dir, company, product_id):
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"
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

    total_calories = total_protein = total_fat = total_carbohydrates = total_moisture = total_ash = 0
    ingredient_data = await fetch_ingredient_data(product_id)
    for row in ingredient_data:
        per_composition = row['per_composition'] / 100  # Precompute percentage factor

        total_calories += per_composition * row['calories']
        total_protein += per_composition * row['protein']  # Fixed incorrect accumulation
        total_fat += per_composition * row['fat']
        total_carbohydrates += per_composition * row['carbohydrates']
        total_moisture += per_composition * row['moisture']
        total_ash += per_composition * row['ash']

    w, h = A4
    lineSpacing = 20
    file_name = f"{company}_{product_name_footer}_Nutritional_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date
    y = y - lineSpacing
    c.setFont("Cambria-Regular", 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Name Display
    y = y - lineSpacing * 4
    # Placeholder for product name
    if symbol_id == 1 or symbol_id == 4:
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
    y = y - lineSpacing * 2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title = "NUTRITIONAL STATEMENT"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)

    ### BODY TEXT SECTION ###

    ##### This is for list of composition fetched from db#####
    #### Start ####

    header_style = ParagraphStyle('header_text',
                                  fontName='Cambria-Regular',
                                  fontSize=11,
                                  alignment=TA_CENTER)
    nutrient = Paragraph('<b>Nutrient</b>', style=header_style)
    amount_per_100g = Paragraph('<b>Amount</b><br/>Per 100g', header_style)
    amount_per_serving = Paragraph('<b>Amount</b><br/>Per Serving(1gm)', header_style)
    ## Composition Data ##
    data = [[nutrient, amount_per_100g, amount_per_serving],  # Header row
            ["Calories", f"{total_calories:.2f}", f"{total_calories / 100:.2f}"],
            ["Fat – Total (g)", f"{total_fat:.2f}", f"{total_fat / 100:.2f}"],
            ["Carbohydrates (g)", f"{total_carbohydrates:.2f}", f"{total_carbohydrates / 100:.2f}"],
            ["Dietary Fiber (g)", "negligible", "negligible"],  # Fixed Value
            ["Added Sugars (g)", "N/A", "N/A"],  # Fixed Value
            ["Protein (g)", f"{total_protein:.2f}", f"{total_protein / 100:.2f}"],
            ["Moisture (g)", f"{total_moisture:.2f}", f"{total_moisture / 100:.2f}"],
            ["Ash (g)", f"{total_ash:.2f}", f"{total_ash / 100:.2f}"], ]
    # data = [['Nutrient', 'Amount\nPer 100g', 'Amount\nPer Serving(1gm)']]
    table_style = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                              # ('GRID', (0, 0), (0, -1), 1, colors.black),
                              # ('GRID', (-1, 0), (-1, -1), 1, colors.black),
                              ('FONTNAME', (0, 0), (2, 0), 'Cambria-Bold'),
                              ('FONTNAME', (0, 1), (-1, -1), 'Cambria-Regular'),
                              ('FONTSIZE', (0, 0), (-1, -1), 10, colors.black),
                              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                              ('ALIGN', (1, 0), (2, -1), 'CENTER'),
                              ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                              ('LEFTPADDING', (0, 0), (-1, -1), 8),
                              ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                              ('BOTTOMPADDING', (1, 0), (-1, -1), 8),
                              ('TOPPADDING', (1, 0), (-1, -1), 8)])

    # data.append([i.ingredients, i.activity])
    t = Table(data, style=table_style, colWidths=[100, 100, 120], splitByRow=1, repeatRows=1)
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, (w - tw) / 2, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y = y - th - 30
    ### END ###

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{product_name_footer}_Nutritional_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
