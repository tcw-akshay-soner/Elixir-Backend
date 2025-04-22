from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Flowable, Image
)


# from src.template_file.template_SDS import prepare_custom_styles


def seb_section_data(product_data, prepare_custom_styles):
    return {
        "SECTION 1 – PRODUCT AND COMPANY IDENTIFICATION": [{
            "subsection_title": "1.1 &nbsp;&nbsp;&nbsp;<b>Product Identifiers</b>",
            "content": [
                ("Product Name", f"{product_data['product_name']}"),
                ("CAS-No.", f"{product_data['cas_number']}"),
                ("EC Number", f"{product_data['ec_number']}"),
                # ("Product Type", f"{product_data['product_type']}"),
            ]},
            {
                "subsection_title": "1.2 &nbsp;&nbsp;&nbsp;<b>Relevant identified uses of the substance or mixture "
                                    "and uses advised against</b>",
                "content": [
                    ("Relevant Identified Uses", f"{product_data['identified_uses']}"),  # Dynamic
                ]},
            {
                "subsection_title": "1.3 &nbsp;&nbsp;&nbsp;<b>Details of the supplier of the safety data sheet</b>",
                "content": [
                    ("Company", f"{product_data['company']}"),  # Dynamic
                    ("Telephone", "(909)-613-1660"),
                    ("Fax", "(909)-613-1663"),
                ]},
            {
                "subsection_title": "1.4 &nbsp;&nbsp;&nbsp;<b>Emergency telephone number</b>",
                "content": [
                    ("Emergency Phone #", "(909)-613-1660"),
                ]
            }],
        "SECTION 2 – HAZARDS IDENTIFICATION": [{
            "subsection_title": "2.1 &nbsp;&nbsp;&nbsp;<b>Classification of substance or mixture</b>",
            "content": Paragraph(
                "<u>GHS classification in accordance with 29 CFR 1910 (OSHA HCS)</u> <br/>"
                "Respiratory sensitization (Category 1), H334 <br/>For full text on H-statements mentioned in this "
                "section, see Section 16",
                prepare_custom_styles()["Normal"]
            )},
            {
                "subsection_title": "2.2 &nbsp;&nbsp;&nbsp;<b>GHS label elements, including precautionary "
                                    "statements</b>",
                "content": [
                    ("Pictogram", Image('src/data/danger.png')),
                    ("Signal word", "Danger"),
                    (Paragraph("<u>Hazard statement(s)-</u>", prepare_custom_styles()['LeftAligned']), ""),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;H 334",
                     "May cause allergy or asthma symptoms or breathing difficulties if inhaled."),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;H 319", "Causes serious eye irritation"),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;H 315", "Causes skin irritation"),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;H 335", " May cause respiratory irritation"),
                    (Paragraph("<u>Precautionary statement(s)-</u>", prepare_custom_styles()['LeftAligned']), ""),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;P 261", "Avoid breathing dust/fume/gas/mist/vapours/spray"),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;P 285",
                     "In case of inadequate ventilation wear respiratory protection"),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;P 304 + P 341",
                     "IF INHALED, breathing if difficult, remove victim to fresh air and keep at rest position comfortable for breathing"),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;P 342 + P 311",
                     "If experiencing respiratory symptoms: Call POISON CENTER or doctor/physician"),
                    ("&nbsp;&nbsp;&nbsp;&nbsp;P 501",
                     "Dispose of contents/ container according to local regulations"),
                ]},
        ],
        "SECTION 3 – COMPOSITION/INFORMATION ON INGREDIENTS": [{
            "subsection_title": "3.1 &nbsp;&nbsp;&nbsp;Substances/Mixtures",
            "content": [
                ("Synonyms", f"{product_data['mixtures']}"),  # Dynamic
                ("CAS-No.", f"{product_data['cas_number']}"),
                ("EC Number", f"{product_data['ec_number']}"),
            ]},
            {
                "subsection_title": "",
                "content": Paragraph("For full text of the H-statements that are mentioned in this section. See "
                                     "section 16.", prepare_custom_styles()['Normal'])
            }],

        "SECTION 4 – FIRST AID MEASURES": [{
            "subsection_title": "4.1 &nbsp;&nbsp;&nbsp;Description of first aid measures",
            "content": [
                ("General advice",
                 "Consult a physician; show this safety data sheet to the doctor in attendance. Move out of dangerous area."),
                ("If Inhaled",
                 "Remove from exposure. If symptoms of irritation of sensitization occur (Shortness of breath, wheezing or labored cough), seek medical advice."),
                ("In case of skin contact",
                 "Rinse thoroughly in running water. Remove contaminated shoes and clothing. Consult doctor if symptoms develop"),
                ("In case of eye contact",
                 "Rinse thoroughly in running water. Consult doctor if symptoms develop."),
                ("If Swallowed",
                 "Rinse mouth and throat thoroughly with water. Should irritation occur, seek medical advice."),
            ]},
            {
                "subsection_title": "4.2 &nbsp;&nbsp;&nbsp;Most important symptoms and effects, both acute and delayed",
                "content": [
                    ("Inhalation",
                     "Inhalation may cause irritation to respiratory system. May entail sensitization via inhalation."),
                    ("Ingestion", "May entail gastrointestinal problems"),
                    ("Contact with skin", "May cause irritation"),
                    ("Contact with eyes", "May cause eye irritation (Redness)"),
                ]},
            {
                "subsection_title": "4.3 &nbsp;&nbsp;&nbsp;Indication of any immediate medical attention and special treatment needed",
                "content": Paragraph("No data available", prepare_custom_styles()['Normal'])}
        ],

        # # SECTION 5: Firefighting Measures
        "SECTION 5 – FIREFIGHTING MEASURES": [{
            "subsection_title": "5.1 &nbsp;&nbsp;&nbsp;Extinguishing media",
            "content": Paragraph(
                "<u>Suitable extinguishing media- </u><br/>Use water spray, alcohol-resistant foam, dry chemical or carbon dioxide.",
                prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "5.2 &nbsp;&nbsp;&nbsp;Special hazards arising from the substance or mixture",
                "content": Paragraph("Nature of decomposition product is unknown.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "5.3 &nbsp;&nbsp;&nbsp;Advice for firefighters",
                "content": Paragraph("Wear self-contained breathing apparatus for firefighting if necessary.",
                                     prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "5.4 &nbsp;&nbsp;&nbsp;Further Information",
                "content": Paragraph("No Data available", prepare_custom_styles()['Normal'])
            }],
        # SECTION 6: Accidental Release Measures
        "SECTION 6 – ACCIDENTAL RELEASE MEASURES": [{
            "subsection_title": "6.1 &nbsp;&nbsp;&nbsp;Personal precautions, protective equipment and emergency "
                                "procedures",
            "content": Paragraph("Use personal protective equipment. Avoid dust formation. Avoid breathing vapors, "
                                 "mist or gas. Ensure adequate ventilation. Evacuate personnel to safe areas. Avoid "
                                 "breathing dust.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "6.2 &nbsp;&nbsp;&nbsp;Environmental precautions",
                "content": Paragraph("Do not let product enter drains.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "6.3 &nbsp;&nbsp;&nbsp;Methods and materials for containment and cleaning up",
                "content": Paragraph("Pickup and arrange disposal without creating dust. Sweep up and shovel. Keep in "
                                     "suitable, closed containers for disposal.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "6.4 &nbsp;&nbsp;&nbsp;Reference to other sections",
                "content": Paragraph(
                    "For disposal see section 13 and see section 8 for individual protective equipment.",
                    prepare_custom_styles()['Normal'])

            }],
        # SECTION 7: Handling and Storage
        "SECTION 7 – HANDLING AND STORAGE": [{
            "subsection_title": "7.1 &nbsp;&nbsp;&nbsp;Precautions for safe handling",
            "content": Paragraph("Avoid contact with skin and eyes. Avoid formation of dust and aerosols. Provide "
                                 "appropriate exhaust ventilation at places where dust is formed. See Section 2.2 for "
                                 "precautions. Do not eat, drink, smoke or use personal products when handling "
                                 "chemical substance.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "7.2 &nbsp;&nbsp;&nbsp;Conditions for safe storage, including any "
                                    "incompatibilities",
                "content": Paragraph("Store in clean, cool, dry and well ventilated space. Away from direct sunlight.",
                                     prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "7.3 &nbsp;&nbsp;&nbsp;Specific end use(s)",
                "content": Paragraph("Substance intended to catalyze reactions by enzymatic means.",
                                     prepare_custom_styles()['Normal'])
            }],

        # SECTION 8: Exposure Controls/Personal Protection
        "SECTION 8 – EXPOSURE CONTROLS/PERSONAL PROTECTION": [{
            "subsection_title": "8.1 &nbsp;&nbsp;&nbsp;Control parameters",
            "content": Paragraph("<u>Components with workplace control parameters-</u><br/>Contains no substances "
                                 "with occupational exposure limit values.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "8.2 &nbsp;&nbsp;&nbsp;Exposure controls",
                "content": [
                    (Paragraph("<u>Personal protective equipment-</u>", prepare_custom_styles()['LeftAligned']), ""),
                    ("Eye/Face protection", "Full Mask"),
                    ("Skin Protection", "Wear appropriate protective clothing"),
                    ("Body Protection", "Wear appropriate gloves, clothes"),
                    ("Respiratory Protection", "Wear P3 dust mask"),
                    ("Control of environment exposure",
                     "Do not let product enter drains. Notify local authorities "
                     "if significant leaks and cannot be contained."),

                ]
            }],

        # SECTION 9: Physical and Chemical Properties
        "SECTION 9 – PHYSICAL AND CHEMICAL PROPERTIES": [{
            "subsection_title": "9.1 &nbsp;&nbsp;&nbsp;Information on basic physical and chemical properties",
            "content": [
                ("1. &nbsp; Appearance", f"{product_data['appearance']}"),  #Dynamic
                ("2. &nbsp; Color", f"{product_data['color']}"),  #Dynamic
                ("3. &nbsp; Odor threshold, pH, Melting point/Freezing point, Initial boiling point/ boiling point "
                 "range, Flash point, Evaporation rate, Flammability (Solid, Gas), Upper/Lower flammability or "
                 "explosive limits, Vapor pressure, Vapor density, Water solubility, Partition coefficient, "
                 "Auto ignition temperature, Decomposition temperature, Viscosity, Explosive properties, "
                 "Oxidizing properties", "Data Not Relevant"),
            ]},
            {
                "subsection_title": "9.2 &nbsp;&nbsp;&nbsp;Other safety information",
                "content": Paragraph("No data available", prepare_custom_styles()['Normal'])
            }],
        # SECTION 10: Stability and Reactivity
        "SECTION 10 – STABILITY AND REACTIVITY": [{
            "subsection_title": "",
            "content": Table([
                [Paragraph("<b>10.1</b> &nbsp;&nbsp;Reactivity", prepare_custom_styles()['secheading']), ":",
                 Paragraph("Data not relevant", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>10.2</b> &nbsp;&nbsp;Chemical Stability", prepare_custom_styles()['secheading']), ":",
                 Paragraph("Stable under recommended conditions", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>10.3</b> &nbsp;&nbsp;Possibility of hazardous reaction",
                           prepare_custom_styles()['secheading']), ":",
                 Paragraph("N/A under recommended conditions", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>10.4</b> &nbsp;&nbsp;Conditions to avoid", prepare_custom_styles()['secheading']), ":",
                 Paragraph("See section 5 and 7", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>10.5</b> &nbsp;&nbsp;Incompatible Materials", prepare_custom_styles()['secheading']),
                 ":", Paragraph("No special recommendations", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>10.6</b> &nbsp;&nbsp;Hazardous decomposition products",
                           prepare_custom_styles()['secheading']), ":",
                 Paragraph("No data available.", prepare_custom_styles()['RightAligned'])],
            ], colWidths=[260, 15, 270])
        }],

        # SECTION 11: Toxicological Information
        "SECTION 11 – TOXICOLOGICAL INFORMATION": [{
            "subsection_title": "Information on toxicological effects",
            "content": [
                ("Acute toxicity", "No data available"),
                ("Skin corrosion/irritation", "May entail irritation"),
                ("Serious eye damage/eye irritation", "No data available"),
                ("Respiratory or skin sensitization", "May entail irritation"),
                ("Germ cell mutagenicity", "No data available"),
                ("Carcinogenicity", "No data available"),
                ("Reproductive toxicity", "No data available"),
                ("Specific target organ toxicity- Single exposure", "No data available"),
                ("Specific target organ toxicity- Repeated exposure(s)", "No data available"),
                ("Aspiration hazard", "No data available"),
                ("Additional Information- RTECS", "No data available"),
            ]},
            {
                "subsection_title": "",
                "content": Paragraph("To best of our knowledge, the chemical, physical and toxicological properties "
                                     "have not thoroughly investigated.", prepare_custom_styles()['Normal'])
            }],

        # SECTION 12: Ecological Information
        "SECTION 12 – ECOLOGICAL INFORMATION": [{
            "subsection_title": "",
            "content": Table([
                [Paragraph("<b>12.1</b> &nbsp;&nbsp;Toxicity", prepare_custom_styles()['secheading']), ":",
                 Paragraph("No data available", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>12.2</b> &nbsp;&nbsp;Persistence and degradability",
                           prepare_custom_styles()['secheading']), ":",
                 Paragraph("No data available", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>12.3</b> &nbsp;&nbsp;Bioaccumulative potential", prepare_custom_styles()['secheading']),
                 ":", Paragraph("No data available", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>12.4</b> &nbsp;&nbsp;Mobility in soil", prepare_custom_styles()['secheading']), ":",
                 Paragraph("No data available", prepare_custom_styles()['RightAligned'])],
                [Paragraph("<b>12.5</b> &nbsp;&nbsp;Other adverse effects", prepare_custom_styles()['secheading']), ":",
                 Paragraph("No data available", prepare_custom_styles()['RightAligned'])],
            ], colWidths=[260, 15, 270])
        }],
        #
        # SECTION 13: Disposal Considerations
        "SECTION 13 – DISPOSAL CONSIDERATIONS": [{
            "subsection_title": "13.1 &nbsp;&nbsp;&nbsp;Waste treatment methods",
            "content": Paragraph("Dispose of waste in compliance with national and local laws, environment protection "
                                 "rules. Wastewater must be evacuated to a purification plant. The waste code must be "
                                 "allocated by the user according to the application of product.",
                                 prepare_custom_styles()['Normal'])
        }],
        #
        # SECTION 14: Transport Information
        "SECTION 14 – TRANSPORT INFORMATION": [{
            "subsection_title": "",
            "content": [
                ("DOT (US)", "Not dangerous goods"),
                ("IMDG", "Not dangerous goods"),
                ("IATA", "Not dangerous goods"),
            ]
        }],
        #
        # SECTION 15: Regulatory Information
        "SECTION 15 – REGULATORY INFORMATION": [{
            "subsection_title": "",
            "content": Paragraph("No Data Available", prepare_custom_styles()['Normal'])
        }],

        # SECTION 16: Other Information
        "SECTION 16 – OTHER INFORMATION": [{
            "subsection_title": "<u>Full text of H-statements referred to under Section 2 and 3-</u>",
            "content": Paragraph("""Hazard statement(s)<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;H 334: May cause allergy or asthma symptoms or breathing difficulties if inhaled.<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;H 319: Causes serious eye irritation<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;H 315: Causes skin irritation<br/>
            &nbsp;&nbsp;&nbsp;&nbsp;H 335: May cause respiratory irritation""", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "<u>Further Information</u>",
                "content": Paragraph("The above information is believed to be correct but does not purport to be all "
                                     "inclusive and shall be used only as a guide for the independent verification of "
                                     "the user. The information in this document is based on the present state of our "
                                     "knowledge and is applicable to the product with regard to appropriate safety "
                                     "precautions. It does not represent any guaranty or warranty. Certain guidelines "
                                     "above may be broader than actually required in order to ensure all material is "
                                     "handled with the utmost care.  The company and its affiliates assume no "
                                     "liability for any damage resulting from handling or contact with the above "
                                     "product.  See the Company’s confirmation of purchase order for additional terms "
                                     "and conditions of sale.", prepare_custom_styles()['justify'])
            }, ],
    }
