import warnings
import logging, os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from src.engine.pharma_data import fetch_product
from src.template_file import letterhead

stylesheet = getSampleStyleSheet()
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_template_nutritional(date, temp_dir, company,product_id):
    
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"    
    
    w, h = A4
    lineSpacing = 20
    file_name = f"{company}_{product_name}_Nutritional_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date
    y = y - lineSpacing / 2
    c.setFont("Cambria-Regular", 11)
    c.drawRightString(w - 30, y, date)

    ## Product Name Display
    y = y - lineSpacing * 4

    c.setFont('Cambria-Bold', 30)
    c.drawRightString(w - 30, y, product_name)

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

    y = y - lineSpacing
    data = [['Nutrient', 'Amount\nPer 100g', 'Amount\nPer Serving(1gm)']]
    table_style = TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('GRID', (0, 0), (0, -1), 1, colors.black),
                            ('GRID', (-1, 0), (-1, -1), 1, colors.black),
                            ('FONTNAME', (0, 0), (2, 0), 'Cambria-Bold'),
                            ('FONTNAME', (0, 1), (-1, -1), 'Cambria-Regular'),
                            ('FONTSIZE', (0, 0), (-1, -1), 10, colors.black),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                            ('TOPPADDING', (0, 0), (-1, -1), 3)])

    # data.append([i.ingredients, i.activity])
    t = Table(data, style=table_style,colWidths=[150,150,150])
    tw, th = t.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    t.drawOn(c, (w - tw) / 2, (y - th - 20))  # Adjusting the Y-position to ensure proper alignment
    y = y - th - 30
    ### END ###

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, pfh + 3, f"{product_name}_Nutritional_01A0")
    c.showPage()
    c.save()
    
    return file_path, file_name