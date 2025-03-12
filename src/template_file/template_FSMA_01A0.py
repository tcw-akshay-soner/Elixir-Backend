import os.path
import warnings
import logging
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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

async def create_template_fsma(date, temp_dir, company, product_id):
    
    # if company == "EI":
    #     raise ValueError("File Generation failed, Company must be 'Specialty Enzymes and Probiotics'")
    
    file_name = f"{company}_FSMA_01A0.pdf"
    file_path = os.path.join(temp_dir, file_name)
    if company == "SEB":
        company_name = "Specialty Enzymes & Probiotics"
    elif company == "EI":
        company_name = "Enzyme Innovation"
    
    c = canvas.Canvas(file_path)
    w, h = A4
    lineSpacing = 20

    ### HEADER START ###
    # Adding the logo
    # mask = [0, 2, 40, 42, 136, 139]
    # c.drawImage('src/data/sebLogo.jpg', 30, h - 90, mask=mask, height=65, width=190)
    # y = h - 90 - lineSpacing
    #
    # # Header Line
    # c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
    # c.line(30, y, 565, y)
    c, y, pfh = letterhead.header_footer(c, company)
    ### HEADER END ###

    y = y - lineSpacing
    c.setFont("Cambria-Regular", 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.7)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    # Date
    y = y - lineSpacing * 3
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont('Cambria-Regular', 12)
    c.drawString(50, y, date)

    # Title
    y = y - lineSpacing * 3
    c.setFont("Cambria-Bold", 14)
    title = "FDA Food Safety and Modernization Act (FSMA)"
    c.drawCentredString(w / 2, y, title)
    text_width = c.stringWidth(title, "Cambria-Bold", 14)

    # Title Underline
    x = (w / 2) - (text_width / 2)
    c.setStrokeColorRGB(0, 0, 0, 1)
    c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)

    ### BODY TEXT SECTION ###

    y = y - lineSpacing * 2
    style_body = ParagraphStyle("Body_Text",
                                fontName="Cambria-Regular",
                                fontSize=12,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leading=15,
                                leftIndent=50,
                                rightIndent=50)

    text = f"""The Food Safety and Modernization Act (FSMA) was signed into law on January 4, 2011. {company_name} has been observing compliance various aspects of FSMA."""
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)       # Adjusting the Y-position to ensure proper alignment

    y = y - h - lineSpacing

    style_bullet = ParagraphStyle("Bullet_Text",
                                fontName="Cambria-Regular",
                                fontSize=12,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                bulletFontSize=12,
                                bulletIndent=50,
                                leading=15,
                                leftIndent=60,
                                rightIndent=60)

    text_data = [
        'Our facility has at least one Preventive Controls Qualified Individuals (PCQI) who has successfully completed FSPCA Preventive control for Human Food training course.',
        'We have a written Food Safety Plan which includes hazard analysis and preventive controls',
        'We have a recall plan',
        'We comply with our portion of the FSMA requirement to ensure safe transport by monitoring outgoing trucks for cleanliness and pests before they are loaded',
        'We are compliant with the Foreign Supplier Verification Program (FSVP)',
        'We observe Good Manufacturing Practices. Our GMPs are verified by third party independent auditors']

    for text in text_data:
        text = f"<bullet>&bull;</bullet>{text}"
        p = Paragraph(text, style_bullet)
        bw, bh = p.wrap(w, h)       # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - bh)      # Adjusting the Y-position to ensure proper alignment
        y -= bh + lineSpacing / 2

    y = y - lineSpacing
    text = f"{company_name} is committed to supplying safe and finest quality products to our customers. " \
        "Maintaining your trust in our quality products is of prime importance to us. " \
        "If you have additional questions please contact the quality department or your sales rep at " \
        f"{company_name}."
    p = Paragraph(text, style_body)
    w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)       # Adjusting the Y-position to ensure proper alignment

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
    #             "valid for one year, and we assume no obligation to update this<br/>statement. " \
    #             "Nothing herein is intended as legal or regulatory advice. " \
    #             "The information herein is presented solely for your independent<br/>consideration, review and verification. " \
    #             "This statement does not constitute a representation or warranty regarding the product, and " \
    #             "we shall have<br/>no liability regarding this statement or your use of the information contained herein."
    #
    # p = Paragraph(footer_text, style_footer)
    # pfw, pfh = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
    # p.drawOn(c, 0, pfh)     # Adjusting the Y-position to ensure proper alignment

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, pfh + 6, f"{company}_FSMA_01A0")
    c.showPage()
    c.save()
    
    return file_path, file_name
