import os.path
import logging
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.template_file import letterhead
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

async def create_template_contact(date, temp_dir, company, product_id):
    # if company == "EI":
    #        raise ValueError("File Generation failed, Company must be 'Specialty Enzymes and Probiotics'")

    file_name = f"{company}_Contact Information_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    c = canvas.Canvas(file_path)
    w, h = A4
    lineSpacing = 20

    ### HEADER ###
    ## Logo
    # mask = [0, 2, 40, 42, 136, 139]
    # c.drawImage('src/data/sebLogo.jpg', 30, h - 90, mask=mask, height=65, width=190)
    # ## Header line
    # y = h - 90 - lineSpacing
    # c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
    # c.line(30, y, 565, y)
    c, y, pfh = letterhead.header_footer(c, company)
    ### HEADER ###

    ## Date
    y = y - lineSpacing
    c.setFont("Cambria-Regular", 12)
    c.drawRightString(w - 30, y, date)

    y = y - lineSpacing * 3
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.7)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    y = y - lineSpacing * 2
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    # title = "Specialty Enzymes & Probiotics –Emergency Contact Information"
    title = "Emergency Contact Information"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    ## Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)
    y = y - lineSpacing * 2

    ### BODY TEXT SECTION ###
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=12,
                                textColor=colors.black,
                                alignment=TA_LEFT,
                                firstLineIndent=-10,
                                leftIndent=60)
    text = "1.\tJackie Burton <br/>" \
           " Title: Office Manager <br/>" \
           " Phone: 909-613-1660 <br/>" \
           " Email: <u><link color='blue'>jackie@specialtyenzymes.com</link></u>"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)
    p.drawOn(c, 0, y - h)

    y = y - h - lineSpacing
    text = "2.\tHarshad Doshi <br/>" \
           " Title: CFO <br/>" \
           " Phone: 909-613-1660 <br/>" \
           " Email: <u><link color='blue'>harshad@specialtyenzymes.com</link></u>"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)
    p.drawOn(c, 0, y - h)

    y = y - h - lineSpacing
    text = "3.&nbsp;Erika Martinez <br/>" \
           " Title: Regulatory Affairs Supervisor <br/>" \
           " Phone: 909-613-1660 <br/>" \
           " Email: <u><link color='blue'>ra@specialtyenzymes.com</link></u>"
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)
    p.drawOn(c, 0, y - h)

    ### FOOTER ###
    # c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
    # c.line(30, 100, 565, 100)
    #
    # style_footer = ParagraphStyle("footer",
    #                             fontName="Cambria-Regular",
    #                             fontSize=8,
    #                             textColor=colors.grey,
    #                             alignment=TA_JUSTIFY,
    #                             justifyBreaks=1,
    #                             justifyLastLine=0,
    #                             leftIndent=30,
    #                             rightIndent=30,
    #                             strikeColor=0.4)
    #
    # footer_text = "The information is presented in good faith as of the date set forth herein and " \
    #               "valid for one year, and we assume no obligation to update this<br/>statement. " \
    #               "Nothing herein is intended as legal or regulatory advice. " \
    #               "The information herein is presented solely for your independent<br/>consideration, review and verification. " \
    #               "This statement does not constitute a representation or warranty regarding the product, and " \
    #               "we shall have<br/>no liability regarding this statement or your use of the information contained herein."
    #
    # p = Paragraph(footer_text, style_footer)
    # pfw, pfh = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    # p.drawOn(c, 0, pfh)  # Adjusting the Y-position to ensure proper alignment

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{company}_Contact Information_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
