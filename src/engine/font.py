from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from rich import print

# Register the Cambria font family
def register_font_family(font_name: str, font_paths: dict):
    """
    Register a font family with ReportLab.
    
    Args:
        font_name (str): The base name for the font family.
        font_paths (dict): A dictionary with keys `regular`, `bold`, `italic`, and `bold_italic`
        mapping to the paths of the respective font files.
    """
    try:
        # Register individual font styles
        pdfmetrics.registerFont(TTFont(f"{font_name}-Regular", font_paths["regular"]))
        pdfmetrics.registerFont(TTFont(f"{font_name}-Bold", font_paths["bold"]))
        pdfmetrics.registerFont(TTFont(f"{font_name}-Italic", font_paths["italic"]))
        pdfmetrics.registerFont(TTFont(f"{font_name}-BoldItalic", font_paths["bold_italic"]))

        # Register the font family
        pdfmetrics.registerFontFamily(
            font_name,
            normal=f"{font_name}-Regular",
            bold=f"{font_name}-Bold",
            italic=f"{font_name}-Italic",
            boldItalic=f"{font_name}-BoldItalic",
        )
        print(f"Font family '{font_name}' registered successfully.")
    except Exception as e:
        print(f"Error registering font family '{font_name}': {e}")

# Paths to the font files
cambria_fonts = {
    "regular": r"./src/font/Cambria.ttf",
    "bold": r"./src/font/cambriab.ttf",
    "italic": r"./src/font/cambriai.ttf",
    "bold_italic": r"./src/font/cambriaz.ttf",
}

