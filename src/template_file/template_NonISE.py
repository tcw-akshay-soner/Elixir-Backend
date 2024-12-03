import logging,os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.template_file import letterhead
from src.engine.pharma_data import fetch_product, fetch_declaration_data
from src.template_file.template_B_irraditated import create_template_birradiation

stylesheet = getSampleStyleSheet()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_compliance(declaration_data, field):
    if field == 'non-irradiated':
        for row in declaration_data:
            if row['irradiated'] == 'Yes':
                return True
        return False
    if field == 'non-irradiation, non-eto and non-sewer/sludge statement':
        for row in declaration_data:
            if row['irradiated'] == 'Yes' or row['eto_treated'] == 'Yes' or row['sewage_sludge_treated'] == 'Yes':
                return True
        return False
    if field == 'non-eto and non-sewer/sludge statement':
        for row in declaration_data:
            if row['eto_treated'] == 'Yes' or row['sewage_sludge_treated'] == 'Yes':
                return True
        return False

async def generate_file_name(company, temp, product_id):
    
    product_data = await fetch_product(product_id)
    product_name = product_data[0]['product_name'] if product_data else "N/A"    
    
    if temp == 'non-irradiated':
        return f"{company}_{product_name}_Non Irradiated_01A0.pdf", product_name
    elif temp == 'non-irradiation, non-eto and non-sewer/sludge statement':
        return f"{company}_{product_name}_Non ISE_01A0.pdf", product_name
    elif temp == 'non-eto and non-sewer/sludge statement':
        return f"{company}_{product_name}_Non Sewage and Non ETO_01A0.pdf", product_name
    else:
        raise ValueError(f"Unknown template type: {temp}")

async def create_template_nonise(date, company, temp, product_id, temp_dir):
        
    # Validate input and create the file path
    if not os.path.exists(temp_dir):
        raise FileNotFoundError(f"Directory {temp_dir} does not exist.")
    
    declaration_data = await fetch_declaration_data(product_id)
    
    if temp == 'non-irradiated':
        nonirradiated = await check_compliance(declaration_data, 'non-irradiated')
        if nonirradiated:
            file_path, file_name = await create_template_birradiation(date, temp_dir, company, product_id)
            return file_path, file_name
    if temp == 'non-irradiation, non-eto and non-sewer/sludge statement':
        ise = await check_compliance(declaration_data, 'non-irradiation, non-eto and non-sewer/sludge statement')
        if ise:
            raise ValueError("File generation failed because the listed product's underwent irradiation, sludge treatment, and ethylene oxide (ETO) was used in the manufacturing process.")
    if temp == 'non-eto and non-sewer/sludge statement':
        se = await check_compliance(declaration_data, 'non-eto and non-sewer/sludge statement')
        if se:
            raise ValueError("File generation failed because the listed product's is treated with sludge and ethylene oxide (ETO) in the manufacturing process.")
    
    file_name, product_name = await generate_file_name(company, temp, product_id)
    file_path = os.path.join(temp_dir, file_name)

    c = canvas.Canvas(file_path)  

    ## Letterhead
    w, h = A4
    lineSpacing = 20
    c, y, pfh = letterhead.header_footer(c, company)

    ## Date Section
    y = y - lineSpacing
    c.setFont('Cambria-Regular', 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Section
    y = y - lineSpacing * 4
    
    c.setFont('Cambria-Bold', 30)
    c.drawRightString(w - 30, y, product_name)  # Placeholder for product name

    y = y - lineSpacing
    c.setFont('Cambria-Regular', 10)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.drawRightString(w - 30, y, "Proprietary and Confidential")

    ## Title
    if temp == 'non-irradiated':
        text_data = ("NON-IRRADIATION STATEMENT",
                    "The above listed product(s) is not subjected to irradiation during the manufacturing process. The ingredients used in the above listed product are certified by the vendor(s) to be non-irradiated. The above listed product is a non-irradiated product.")
    elif temp == 'non-irradiation, non-eto and non-sewer/sludge statement':
        text_data = ("NON-IRRADIATION, NON-ETO and NON-SEWER/SLUDGE STATEMENT",
                    "The above listed product(s) is neither irradiation nor sludge treatment used in the manufacturing of above listed product. Furthermore, ethylene oxide was not used in the manufacturing of the stated material. Therefore above listed product is a non-irradiation, non-ETO and non-sludge product.")
    elif temp == 'non-eto and non-sewer/sludge statement':
        text_data = ("NON-ETO and NON-SEWAGE/SLUDGE STATEMENT",
                    "The above listed product(s) is not treated with sewage/ sludge during the manufacturing process. Ethylene oxide is not used in the manufacturing of the stated material. Therefore above listed product is a non-sludge and non-ETO product.")
    y = y - lineSpacing * 4
    c.setFillColorRGB(0, 0, 0, 1)
    c.setFont("Cambria-Bold", 14)
    title, content = text_data
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
                                fontSize=11,
                                textColor=colors.black,
                                alignment=TA_JUSTIFY,
                                leading=15,
                                justifyBreaks=1,
                                justifyLastLine=0,
                                leftIndent=30,
                                rightIndent=30)

    p = Paragraph(content, style_body)
    w, h = p.wrap(w, h)  # Wrap the text to avoid overflow by reducing the available width
    p.drawOn(c, 0, y - h)  # Adjusting the Y-position to ensure proper alignment

    product_name = product_name.replace(" ","")
    c.setFont('Cambria-Regular', 8)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    if temp == "non-irradiated":
        c.drawRightString(w - 30, pfh + 3, f"{product_name}_Non Irradiated_01A0")
    elif temp == "non-irradiation, non-eto and non-sewer/sludge statement":
        c.drawRightString(w - 30, pfh + 3, f"{product_name}_Non ISE_01A0")
    elif temp == "non-eto and non-sewer/sludge statement":
        c.drawRightString(w - 30, pfh + 3, f"{product_name}_Non Sewage and Non ETO_01A0")
    c.showPage()
    c.save()

    return file_path, file_name
