import warnings
import logging, os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

stylesheet = getSampleStyleSheet()
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_template_customer_seb(date, temp_dir, company, customer_name, product_id):

       file_name = f"{company}_{customer_name}_LOCG_01A0.pdf"
       file_path = os.path.join(temp_dir, file_name)
       
       c = canvas.Canvas(file_path)
       w, h = A4
       lineSpacing = 12

       # Adding the logo
       mask = [0, 2, 40, 42, 136, 139]
       if company == 'SEB':
              c.drawImage('src/data/sebLogo.jpg', 30, 750, mask=mask, height=65, width=190)
       elif company == 'EI':
              raise ValueError("File Generation Failed, Company must be 'SPECIALTY ENZYMES AND PROBIOTICS'")
              # c.drawImage('src/data/eiLogo.png', 30, 750, mask=mask,  height=100, width=350)
       c.setFont('Cambria-Regular', 10)
       c.setFillColorRGB(0.5, 0.5, 0.5, 0.7)
       c.drawRightString(w-60, 720, "Proprietary and Confidential")

       # Title
       c.setFillColorRGB(0, 0, 0, 1)
       c.setFont("Cambria-Bold", 14)
       title = "Guarantee of Continuing Compliance"
       c.drawCentredString(w/2,700,title)
       text_width = c.stringWidth(title, "Cambria-Bold", 14)

       # Title underline
       x = (w / 2) - (text_width / 2)
       c.setStrokeColorRGB(0, 0, 0, 1)
       c.line(x, 700 - 16 * 0.2, x + text_width, 700 - 16 * 0.2)
       y = 680
       y = y - lineSpacing

       ### BODY TEXT SECTION ###
       c.setFont("Cambria-Regular", 12)
       c.drawString(60, y , date)
       y = y - lineSpacing

       c.drawString(60,y,f"FOR: {customer_name}")
       y = y - lineSpacing/3

       style_body = ParagraphStyle("Body_Text",
                                   fontName="Cambria-Regular",
                                   fontSize=11,
                                   textColor=colors.black,
                                   alignment=TA_JUSTIFY,
                                   justifyBreaks=1,
                                   justifyLastLine=0,
                                   leading = 15,
                                   leftIndent=60,
                                   rightIndent=60)
       text = "Specialty Enzymes & Probiotics hereby makes the below Guarantee to the above-listed Customer <br/>"\
              "(hereinafter “Customer”)."\
              "This Guarantee shall be a continuing Guarantee and shall continue in effect<br/>"\
              "until such date as Customer receive from Specialty Enzymes & Probiotics notice of the revocation of the <br/>Guarantee contained herein."
       p = Paragraph(text, style_body)
       w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
       p.drawOn(c, 0, y - h)
       y = y - h - lineSpacing/2

       text ="As of the date of delivery, all products delivered to Customer in response to orders made"\
              "by Customer<br/>comports with the laws to the extent then effective and applicable in the "\
              "following ways:"

       p = Paragraph(text, style_body)
       w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
       p.drawOn(c, 0, y - h)       # Adjusting the Y-position to ensure proper alignment

       y = y - h - 10
       point_style = ParagraphStyle("point_Text",
                                   fontName="Cambria-Regular",
                                   fontSize=11,
                                   textColor=colors.black,
                                   alignment=TA_JUSTIFY,
                                   justifyBreaks=1,
                                   justifyLastLine=0,
                                   leading=14,
                                   leftIndent=110,
                                   rightIndent=110)
       text_data = [("(a)","The products are not adulterated or misbranded within the meaning of the Federal Food, Drug and Cosmetic Act (hereinafter “FDCA”), 21 U.S.C. 342-3, nor within the meaning of any identical or substantially similar lawful state law or municipal ordinance in which the definitions of adulteration and misbranding are identical or substantially similar to those in the FDCA;"),
                     ("(b)","The products do not contain articles which may not be introduced into interstate commerce in violation of the FDCA;"),
                     ("(c)","The products will have been formulated, manufactured, packaged, labeled, and handled in accordance with all other applicable requirements of federal, state, and local law.")]
       for letter, text in text_data:      # Iteration for Alphabetical Sequencing
              c.drawString(90, y - 11 , letter)
              text = f"{text}"
              p = Paragraph(text, point_style)
              bw, bh = p.wrap(w, h)       # Wrap the text to avoid overflow by reducing the available width
              p.drawOn(c, 0, y - bh)      # Adjusting the Y-position to ensure proper alignment
              y -= bh + lineSpacing / 2

       text = "This Guarantee continues with the products only so long as the product remains in the original "\
              "unopened container from Specialty Enzymes & Probiotics’s plant in Chino, California."
       p = Paragraph(text, style_body)
       w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
       p.drawOn(c, 0, y - h)       # Adjusting the Y-position to ensure proper alignment

       y = y - h - lineSpacing/2
       text = "This Guarantee shall, however, be void and of no effect in any instance where the particular use by Customer or its distributee of any article"\
              " to which this Guarantee would otherwise apply is a use which is<br/>not in accordance with the requirements of the FDCA or other"\
              "applicable federal law. This Guarantee<br/>shall also be void and of no effect if Customer fails to notify the undersigned "\
              "in writing of any violation<br/>which come to its attention of any of the above-mentioned laws immediately upon discovery of such violation."
       p = Paragraph(text, style_body)
       w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
       p.drawOn(c, 0, y - h)       # Adjusting the Y-position to ensure proper alignment

       y = y - h - lineSpacing*2
       c.drawString(60,y,"Sincerely,")
       y = y - lineSpacing*2
       c.drawString(60,y,"Harshad Doshi")
       y = y - lineSpacing
       c.drawString(60,y, "Chief Operations Officer")


       style_other = ParagraphStyle("Other_Text",
                                   fontName="Cambria-Regular",
                                   fontSize=8,
                                   textColor=colors.black,
                                   alignment=TA_JUSTIFY,
                                   justifyBreaks=1,
                                   justifyLastLine=0,
                                   leftIndent=60,
                                   rightIndent=60)

       text = "The information is presented in good faith as of the date set forth herein and " \
              "valid for one year, and we assume no obligation to update this<br/>statement." \
              "Nothing herein is intended as legal or regulatory advice. " \
              "The information herein is presented solely for your independent<br/>consideration, review and verification. " \
              "This statement does not constitute a representation or warranty regarding the product, and " \
              "we shall have<br/>no liability regarding this statement or your use of the information contained herein."
       p = Paragraph(text, style_other)
       w, h = p.wrap(w, h)     # Wrap the text to avoid overflow by reducing the available width
       p.drawOn(c, 0 , h + 20)     # Adjusting the Y-position to ensure proper alignment

       c.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
       c.line(60, 50, 535, 50)

       style_footer = ParagraphStyle("footer",
                                   fontName="Cambria-Regular",
                                   fontSize=12,
                                   textColor=colors.black,
                                   alignment=TA_CENTER)

       footer_text = "Your Global Resource for Quality <font color='green'>Enzymes </font> & <font color='blue'>Probiotics</font>"
       p = Paragraph(footer_text, style_footer)
       w, h = p.wrap(w, h)
       p.drawOn(c, 0, h + 20)
       c.showPage()
       c.save()
       
       return file_path, file_name
