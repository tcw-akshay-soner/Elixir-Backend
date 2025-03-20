import logging, os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from src.engine.pharma_data import fetch_product, fetch_declaration_data
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


async def create_template_nongmo(date, temp_dir, company, product_id):
    ## Product Data ##
    product_data = await fetch_product(product_id)
    # product_name = product_data[0]['product_name'] if product_data else "N/A"
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
    ## Declaration Data ##
    declaration_data = await fetch_declaration_data(product_id)

    classifications = {row["classification"] for row in declaration_data if row["non_gmo"] == "Yes"}
    non_gmo = "No" if any(row["non_gmo"] == "No" for row in declaration_data) else "Yes"

    if non_gmo == "No":
        code = "01B0"
    elif classifications == {"Enzymes"}:
        code = "02A0"
    elif classifications == {"Probiotics"}:
        code = "02C0"
    elif classifications == {"Enzymes", "Probiotics"}:
        code = "02D0"

    # Dataset for product name
    # code = '01F0'       ## Alphabet Template Code Coming from Database
    if code == '01B0':
        file_name = f"{company}_{product_name_footer}_GMO Dec_01B0.pdf"
    else:
        file_name = f"{company}_{product_name_footer}_Non GMO_{code}.pdf"
    file_path = os.path.join(temp_dir, file_name)
    
    c = canvas.Canvas(file_path)    # Product Name From Database
    c, y, pfh = letterhead.header_footer(c, company)
    w, h = A4
    lineSpacing = 20

    ## Date Section
    y = y - lineSpacing
    c.setFont('Cambria-Regular', 12)
    c.setFillColorRGB(0, 0, 0, 1)
    c.drawRightString(w - 30, y, date)

    ## Product Section
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

    ## Non-GMO statements
    y = y - lineSpacing * 3
    # Define the classification mappings as a dictionary
    # classification_map = {
    #     'Papain': ('STATEMENT ON NON-GMO STATUS OF PAPAIN',
    #                """The plant sources of the enzyme proteins in this formulation are certified by the manufacturer to have been produced by using dried latex of Carica  papaya, which is derived from plant origin and hence have not been modified by the use of recombinant DNA technology (“Non-GMO”)."""),
    #     'Probiotics': ('STATEMENT ON NON-GMO STATUS FOR PROBIOTICS',
    #                    """The probiotic microorganisms in this formulation are certified by the manufacturer to be produced from non-GMO microorganisms."""),
    #     'Microbial Enzymes': ('STATEMENT ON NON-GMO STATUS OF MICROBIAL ENZYMES',
    #                          """The enzyme proteins in this formulation are certified by the manufacturer to be produced from non-GMO microorganisms."""),
    #     'Bromelain': ('STATEMENT ON NON-GMO STATUS OF BROMELAIN',
    #                   """The enzyme proteins in this formulation are derived from plant sources (specifically, pineapple stems) and are certified by the manufacturer as non-GMO, to the best of their knowledge."""),
    #     'Animal-Derived': ('STATEMENT ON NON-GMO STATUS OF ANIMAL ORIGIN ENZYME(S)',
    #                        """The above-mentioned product contains animal origin enzyme which does not contain any genetically modified material."""),
    #     'Protein': ('STATEMENT ON NON-GMO STATUS',
    #                 """The source of the proteins in this formulation are certified by the manufacturer to have been produced by using Vigna radiata flour, which is of plant origin. It has not been modified by the use of recombinant DNA technology (“Non-GMO”)."""),
    #     'Pancreatin': ('STATEMENT ON NON-GMO STATUS OF PANCREATIN',
    #                    """The above-mentioned product contains animal origin enzyme Pancreatin which does not contain any genetically modified material and is not produced from raw material of genetically modified origin."""),
    #     'Other': ('STATEMENT ON NON-GMO STATUS',
    #               """The probiotic microorganisms in this formulation are certified by the manufacturer to be produced from non-GMO microorganisms.""")
    # }

    classification_map = {
        'Enzymes': ('STATEMENT ON NON-GMO STATUS OF ENZYMES',
                    """The enzyme proteins in this formulation are certified by the manufacturer to be produced from 
                    non-GMO microorganisms or non-GMO plant source or non-GMO animals."""),
        'Probiotics': ('STATEMENT ON NON-GMO STATUS OF PROBIOTICS',
                       """The probiotic microorganisms in this formulation are certified by the manufacturer to be 
                       produced from non-GMO microorganisms.""")
    }

    # Initialize the combined classification set
    combined_classification = set()
    # Sort the classification_map by keys
    # sorted_classification_map = dict(sorted(classification_map.items()))

    if non_gmo == "Yes":
        for row in declaration_data:
            classification = row.get("classification")
            if classification in classification_map:
                combined_classification.add(classification_map[classification])
    elif non_gmo == "No":
        gmo = ('STATEMENT ON GMO STATUS',
            """The above mentioned product(s) is not a GMO. The enzyme product is manufactured by fermentation of a microorganism that is not present in the final product. The production organism may be improved by means of modern biotechnology. """)
        combined_classification.add(gmo)

    # Convert the set to a sorted list based on the original key order
    # combined_classification = [entry for key, entry in sorted_classification_map.items() if entry in combined_classification]

    for title, content in combined_classification:        # Iteration for title and content in text data according to the code provided
        # Set title font color to black
        c.setFont('Cambria-Bold', 14)
        c.setFillColorRGB(0, 0, 0, 1)  # Ensure black color for the title
        c.drawCentredString(w / 2, y, title)
        text_width = c.stringWidth(title, "Cambria-Bold", 14)
        x = (w / 2) - (text_width / 2)      # For Underline in the title
        c.setStrokeColorRGB(0, 0, 0, 1)
        c.line(x, y - 16 * 0.2, x + text_width, y - 16 * 0.2)       # Underline in the title
        y -= 15

        # Add content paragraph
        style_normal = ParagraphStyle("Body_Text",
                                    fontName="Cambria-Regular",
                                    fontSize=11,
                                    textColor=colors.black,
                                    alignment=TA_JUSTIFY,
                                    justifyBreaks=1,
                                    justifyLastLine=0,
                                    leading=15,
                                    leftIndent=50,
                                    rightIndent=50)
        p = Paragraph(content, style_normal)
        p_width, p_height = p.wrap(w, h)        # Wrap the text to avoid overflow by reducing the available width
        p.drawOn(c, 0, y - p_height)        # Adjusting the Y-position to ensure proper alignment
        y -= (p_height + 30)

    c.setFont('Cambria-Regular', 8)
    # c.setFillColorRGB(0.5, 0.5, 0.5, 1)
    c.setFillColorRGB(0, 0, 0, 1)
    if non_gmo == 'No':
        c.drawRightString(w - 30, pfh + 6, f'{product_name_footer}_GMO Dec_01B0')
    else:
        c.drawRightString(w - 30, pfh + 6, f'{product_name_footer}_Non GMO_{code}')

    c.showPage()
    c.save()
    
    return file_path, file_name