import logging

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

stylesheet = getSampleStyleSheet()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def header_footer(c, company):
    w, h = A4
    lineSpacing = 20
    if company == 'SEB':
        ### HEADER START ###
        ## Adding the logo
        mask = [0, 2, 40, 42, 136, 139]
        c.drawImage("src/data/sebLogo.jpg", 30, h - 90, mask=mask, height=65, width=190)

        ## Header Line
        y = h - 90 - lineSpacing
        c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
        c.line(30, y, 565, y)
        ### HEADER END ###

        ### FOOTER ###
        c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
        c.line(30, 100, 565, 100)

        style_footer = ParagraphStyle("footer",
                                      fontName="Cambria-Regular",
                                      fontSize=8,
                                      textColor=colors.black,
                                      alignment=TA_JUSTIFY,
                                      justifyBreaks=1,
                                      justifyLastLine=0,
                                      leftIndent=30,
                                      rightIndent=30,
                                      strikeColor=0.4)

        footer_text = """The information is presented in good faith as of the date set forth herein and valid for one 
        year, and we assume no obligation to update this statement. Nothing herein is intended as legal or 
        regulatory advice. The information herein is presented solely for your independent consideration, 
        review and verification. This statement does not constitute a representation or warranty regarding the 
        product, and we shall have no liability regarding this statement or your use of the information contained 
        herein."""

        p = Paragraph(footer_text, style_footer)
        pfw, pfh = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, pfh)  # Adjusting the Y-position to ensure proper alignment

        return c, y, pfh

    elif company == 'EI':
        ### HEADER START ###
        ## Adding the logo
        mask = [0, 2, 40, 42, 136, 139]
        c.drawImage('src/data/eiLogo.png', 30, h - 140, mask=mask, height=100, width=350)

        ## Header Line
        y = h - 100 - lineSpacing
        ### HEADER END ###

        ### FOOTER ###

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
                                      rightIndent=30,
                                      )

        footer_text = """The information is presented in good faith as of the date set forth herein and valid for one 
        year, and we assume no obligation to update this statement. Nothing herein is intended as legal or 
        regulatory advice. The information herein is presented solely for your independent consideration, 
        review and verification. This statement does not constitute a representation or warranty regarding the 
        product, and we shall have no liability regarding this statement or your use of the information contained 
        herein."""

        p = Paragraph(footer_text, style_footer)
        pfw, pfh = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, pfh)  # Adjusting the Y-position to ensure proper alignment
        return c, y, pfh
