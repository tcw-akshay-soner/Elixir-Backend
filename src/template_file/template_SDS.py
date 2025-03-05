import logging
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Flowable, Image
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from src.data.seb_sds_data import seb_section_data as seb_section_data
from src.data.ei_sds_data import ei_section_data as ei_section_data
from src.engine.pharma_data import fetch_ingredient_data, fetch_product


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
warnings.filterwarnings('ignore')

def prepare_custom_styles():
    """
    Define custom styles for the document.
    """
    styles = {
        "Title": ParagraphStyle(
            name="Title",
            fontName="Cambria-Bold",
            fontSize=14,
            alignment=1,  # Centered
            spaceAfter=12
        ),
        "Normal": ParagraphStyle(
            name="Normal",
            fontName="Cambria-Regular",
            fontSize=12,
            # alignment=TA_JUSTIFY,
            # justifyBreaks=0,
            # justifyLastLine=0,
            leading=15,
            leftIndent=30
        ),
        "image": ParagraphStyle(
            name="image",
            fontName="Cambria-Regular",
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=35,
            leading=20,
        ),
        "LeftAligned": ParagraphStyle(
            name="LeftAligned",
            fontName="Cambria-Regular",
            fontSize=12,
            alignment=TA_LEFT,
            leftIndent=10,
        ),
        "RightAligned": ParagraphStyle(
            name="RightAligned",
            fontName="Cambria-Regular",
            fontSize=12,
            alignment=TA_LEFT,
        ),
        "Heading": ParagraphStyle(
            name="Heading",
            fontName="Cambria-Bold",
            fontSize=12,
            alignment=TA_LEFT,
            leading=14
        ),
        "justify": ParagraphStyle(
            name="justify",
            fontName="Cambria-Regular",
            fontSize=12,
            alignment=TA_JUSTIFY,
            justifyBreaks=1,
            justifyLastLine=0,
            leading=15,
            leftIndent=30,
            rightIndent=30,
        )
    }
    return styles


class SectionTitleBox(Flowable):
    """
    A custom flowable to render a section title inside a box.
    """

    def __init__(self, title, width=540, height=21, padding=5):
        super().__init__()
        self.title = title
        self.width = width
        self.height = height
        self.padding = padding

    def draw(self):
        """
        Draw the section title box with the title inside it.
        """
        self.canv.saveState()
        # Draw the box
        self.canv.setStrokeColorRGB(0, 0, 0, 1)  # Black border
        # self.canv.setFillColorRGB(0.9, 0.9, 0.9)  # Light grey background
        self.canv.setLineWidth(1)
        self.canv.rect(0, 0, self.width, self.height, fill=0, stroke=1)
        # Draw the title
        self.canv.setFillColorRGB(0, 0, 0, 1)  # Black text
        self.canv.setFont("Cambria-Bold", 11)
        self.canv.drawString(self.padding, self.height / 3, self.title)
        self.canv.restoreState()

    def wrap(self, availWidth, availHeight):
        """
        Define the space this flowable takes.
        """
        return self.width, self.height


def header_footer(canvas, doc, company):
    """
    Custom header and footer for every page.
    """
    canvas.saveState()
    w, h = A4
    # Header
    ## Adding the logo
    if company == "SEB":
        mask = [0, 2, 40, 42, 136, 139]
        canvas.drawImage("src/data/sebLogo.jpg", 30, h - 70, mask=mask, height=65, width=190)
        canvas.setFillColorRGB(0.7, 0.7, 0.7, 1)
        canvas.setFont("Cambria-Bold", 12)
        canvas.drawCentredString(w / 2, h - 80, "SAFETY DATA SHEET")
        canvas.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
        canvas.line(30, h - 90, w - 30, h - 90)
    elif company == "EI":
        mask = [0, 2, 40, 42, 136, 139]
        canvas.drawImage('src/data/EI_only_logo.jpg', 30, h - 70, mask=mask, height=50, width=240)
        canvas.drawImage('src/data/EI_add.png', 400 , h-70, mask=mask, height=40, width=150)
        canvas.setFillColorRGB(0.7, 0.7, 0.7, 1)
        canvas.setFont("Cambria-Bold", 12)
        canvas.drawCentredString(w / 2, h - 90, "SAFETY DATA SHEET")

    # Footer with page numbers
    canvas.setStrokeColorRGB(0.5, 0.5, 0.5, 0.3)
    canvas.line(30, 40, w - 30, 40)
    canvas.setFillColorRGB(0.5, 0.5, 0.5, 1)
    canvas.setFont("Cambria-Regular", 10)
    canvas.drawRightString(w - 30, 30, f"{doc.page}| Page")
    canvas.restoreState()


async def create_sds_pdf(date, temp_dir, company, product_id):
    """
    Generate the SDS PDF dynamically based on product and compliance data.
    """
    product_data = await fetch_product(product_id)
    ingredient_data = await fetch_ingredient_data(product_id)
    for row in product_data:
        product_name = row['product_name']
        symbol_id = row['symbol_id']
        symbol_code = row['symbol_code']
        # symbol_name = row['symbol_name']
        symbol = row['symbol']
        identified_uses = row['identified_uses']
        mixtures = row['mixtures']
        appearance = row['appearance']
        color = row['color']

    cas_number = set()
    ec_number = set()
    for row in ingredient_data:
        # ingredient_name = row['ing_name']
        if row['cas_num']:
            cas_number.add(row['cas_num'])
        if row['ec_num']:
            ec_number.add(row['ec_num'])
    cas_number = ", ".join(cas_number)
    ec_number = ", ".join(ec_number)

    if symbol_id:
        product_name_footer = product_name.replace(' ', '').replace(chr(int(symbol_code, 16)), '')
    else:
        product_name_footer = product_name.replace(' ', '')
    if company == 'SEB':
        company_name = "Specialty Enzymes & Probiotics<br/>13591 Yorba Ave.,<br/>Chino, CA-91710"
    elif company == 'EI':
        company_name = "Enzyme Innovation<br/>13591 Yorba Ave.,<br/>Chino, CA-91710"

    data = {
        "product_name": product_name,
        "cas_number": f"{cas_number}",
        "ec_number": f"{ec_number}",
        "identified_uses": identified_uses,
        "company": company_name,
        "mixtures": mixtures,
        "appearance": appearance,
        "color": color
    }
    # Sections with dynamic and static content
    if company == 'EI':
        sections = ei_section_data(data, prepare_custom_styles)
    elif company == 'SEB':
        sections = seb_section_data(data, prepare_custom_styles)

    # Prepare custom styles
    styles = prepare_custom_styles()
    # File setup
    file_name = f"{company}_{product_name_footer}_SDS.pdf"
    file_path = os.path.join(temp_dir, file_name)
    # Create a BaseDocTemplate and PageTemplate
    doc = BaseDocTemplate(file_path, pagesize=A4)
    frame = Frame(20, 50, A4[0] - 50, A4[1] - 140, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=lambda c, d: header_footer(c, d, company))
    doc.addPageTemplates([template])
    # Flowables for content
    content = []
    # Document Title
    # content.append(Paragraph(f"SAFETY DATA SHEET: {product_data['product_name']}", styles["Title"]))
    # content.append(Spacer(1, 24))
    # Add sections with table layout
    try:
        for section_title, subsections in sections.items():
            # Add section title with box
            # content.append(Spacer(1, 12))
            content.append(SectionTitleBox(section_title))
            # content.append(Spacer(1, 8))
            # Add section content
            # Render subsection title
            for subsection in subsections:
                # Add subsection title
                if subsection['subsection_title'] == "":
                    content.append(Spacer(1, 8))
                else:
                    content.append(Spacer(1, 8))
                    content.append(Paragraph(f"{subsection['subsection_title']}", styles["Heading"]))
                    content.append(Spacer(1, 8))
                # Render subsection content
                subsection_content = subsection["content"]
                if isinstance(subsection_content, Paragraph):
                    content.append(subsection_content)
                elif isinstance(subsection_content, Table):
                    content.append(subsection_content)
                else:
                    table_data = []
                    for left, right in subsection_content:
                        if isinstance(right, Image):
                            table_data.append([
                                Paragraph(left, styles['LeftAligned']),
                                ":",
                                Paragraph(
                                    '&nbsp;<img src="src/data/danger.png" width="27" height="27" valign="middle"/>',
                                    styles["image"])
                            ])
                        elif isinstance(left, Paragraph):
                            if isinstance(right, Paragraph):
                                table_data.append([
                                    left,
                                    "",
                                    right
                                ])
                            else:
                                table_data.append([
                                    left, "", ""
                                ])
                        else:
                            table_data.append([
                                Paragraph(left, styles["LeftAligned"]),
                                ":",
                                Paragraph(right, styles["RightAligned"])
                            ])
                    table = Table(table_data, colWidths=[235, 15, 250])
                    table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (1, 0), (1, -1), 'Cambria-Regular'),
                        ('FONTSIZE', (1, 0), (1, -1), 12),
                        # ('WORDWRAP', (0, 0), (-1, -1), True)
                        # ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        # ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        # ('TOPPADDING', (0, 0), (-1, -1), 5),
                        # ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    content.append(table)
            content.append(Spacer(1, 8))
    except Exception as e:
        logging.error(f"Exception Occurred due to : {e}")
    # Final static text
    content.append(Spacer(1, 24))
    content.append(Paragraph("<u>Preparation Information</u>", styles["Normal"]))
    content.append(Paragraph(data["company"], styles["Normal"]))
    content.append(Spacer(1, 14))
    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Cambria-Regular'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT')])
    footer_data = [[f'Preparation {date}', data["product_name"]]]
    table = Table(footer_data, colWidths=[210, 280], style=table_style)
    content.append(table)
    # content.append(Paragraph(f"Preparation {date}", styles["LeftAligned"]))
    # content.append(Paragraph(product_data["product_name"], styles["RightAligned"]))
    # Build the PDF
    doc.build(content)
    return file_path, file_name
