import warnings
import logging
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.engine.pharma_data import fetch_fda
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

async def create_template_fda(date, temp_dir, company, product_id):

        fda = await fetch_fda(company)
        REG_NUM = fda[0]['fda_reg'] if fda else "N/A"
        if company == "SEB":
            company_name = "Specialty Enzymes & Probiotics"
        elif company == "EI":
            company_name = "Enzyme Innovation"

        file_name = f"{company}_FDA REG_01A0"
        file_path = os.path.join(temp_dir, file_name)

        c = canvas.Canvas(file_path)
        c, y, pfh = letterhead.header_footer(c, company)
        w, h = A4
        lineSpacing = 20

        ## Date
        y = y - lineSpacing
        c.setFont("Cambria-Regular", 12)
        c.drawRightString(w-30, y, date)

        y = y - lineSpacing*3
        c.setFont('Cambria-Regular', 12)
        c.setFillColorRGB(0.5, 0.5, 0.5, 0.7)
        c.drawRightString(w-30, y, "Proprietary and Confidential")

        ## Title
        y = y - lineSpacing*4
        c.setFillColorRGB(0, 0, 0, 1)
        c.setFont("Cambria-Bold", 14)
        c.drawCentredString(w/2, y, "FDA REGISTRATION NUMBER")
        text_width = c.stringWidth("FDA REGISTRATION NUMBER", "Cambria-Bold", 14)


        ## Title Underline
        x = (w / 2) - (text_width / 2)
        c.setStrokeColorRGB(0, 0, 0, 1)
        c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)

        ### BODY TEXT SECTION ###
        y = y - lineSpacing*2
        style_body = ParagraphStyle("Body_Text",
                        fontName="Cambria-Regular",
                        fontSize=12,
                        textColor=colors.black,
                        alignment=TA_LEFT,
                        leftIndent=50)

        text = "<u>To whom it may concern:</u>"
        p = Paragraph(text, style_body)
        w, h = p.wrap(w, h)
        p.drawOn(c, 0, y)

        y = y - lineSpacing*2
        style_body = ParagraphStyle("Body_Text",
                        fontName="Cambria-Regular",
                        fontSize=11,
                        textColor=colors.black,
                        alignment=TA_JUSTIFY,
                        justifyBreaks=1,
                        justifyLastLine=0,
                        leading=15,
                        leftIndent=50,
                        rightIndent=50)

        text = (f"{company_name} facilities located at Chino, California, USA have been registered with US FDA in "
                f"accordance with Bioterrorism Act 2002.")
        p = Paragraph(text, style_body)
        w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y)       # Adjusting the Y-position to ensure proper alignment

        y = y - lineSpacing*2
        text = f"Our Registration Number: <b>{REG_NUM}</b>"     ## Registration Number Coming From Database
        p = Paragraph(text, style_body)
        w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y)       # Adjusting the Y-position to ensure proper alignment


        ### FOOTER ###

        c.setFont('Times-Roman', 8)
        # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
        c.setFillColorRGB(0, 0, 0, 1)
        c.drawRightString(w - 30, pfh + 6, f"{company}_FDA REG_01A0")
        c.showPage()
        c.save()
        return file_path, file_name
