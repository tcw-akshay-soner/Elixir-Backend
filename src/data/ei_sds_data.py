from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Flowable, Image
)


def ei_section_data(product_data, prepare_custom_styles):
    return {
        "SECTION 1 – PRODUCT AND COMPANY IDENTIFICATION": [{
            "subsection_title": "1.1 &nbsp;&nbsp;&nbsp;<b>Product Identifiers</b>",
            "content": [
                ("Product Name", f"{product_data['product_name']}"),
                ("CAS-No.", f"{product_data['cas_number']}"),
                ("EC Number", f"{product_data['ec_number']}"),
                # ("Product Type", f"{product_data['product_type']}"),
            ]}, {
            "subsection_title": "1.2 &nbsp;&nbsp;&nbsp;<b>Relevant identified uses of the substance or mixture "
                                "and uses advised against</b>",
            "content": [("Relevant Identified Uses", f"{product_data['identified_uses']}"),  # Dynamic
            ]}, {
            "subsection_title": "1.3 &nbsp;&nbsp;&nbsp;<b>Details of the supplier of the safety data sheet</b>",
            "content": [
                ("Company", f"{product_data['company']}"),  # Dynamic
                ("Telephone", "(909)-613-1660"),
                ("Fax", "(909)-613-1663"),
            ]}, {
            "subsection_title": "1.4 &nbsp;&nbsp;&nbsp;<b>Emergency telephone number</b>",
            "content": [
                ("Emergency Phone #", "(909)-613-1660"),
            ]
            }],
        "SECTION 2 – HAZARDS IDENTIFICATION": [{
            "subsection_title": "2.1 &nbsp;&nbsp;&nbsp;<b>Classification of substance or mixture</b>",
            "content": Paragraph(
                "<u>GHS classification in accordance with 29 CFR 1910 (OSHA HCS) & Regulation (EC) No. 1272/2008 ("
                "CLP) OR the inventory</u> <br/>"
                "Respiratory sensitization (Category 1), H334 <br/>For full text on H-statements mentioned in this "
                "section, see Section 16",
                prepare_custom_styles()["Normal"]
            )}, {
            "subsection_title": "2.2 &nbsp;&nbsp;&nbsp;<b>GHS & Regulation (EC) No 1272/2008 [CLP] label "
                                "elements, including precautionary &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;statements</b>",
            "content": [
                ("Pictogram", Image('src/data/danger.png')),
                ("Signal word", "Danger"),
                (Paragraph("<u>Hazard statement(s)-</u>", prepare_custom_styles()['LeftAligned']), ""),
                ("&nbsp;&nbsp;&nbsp;&nbsp;H 334",
                 "May cause allergy or asthma symptoms or breathing difficulties if inhaled."),
                ("&nbsp;&nbsp;&nbsp;&nbsp;H 319", "Causes serious eye irritation"),
                ("&nbsp;&nbsp;&nbsp;&nbsp;H 315", "Causes skin irritation"),
                ("&nbsp;&nbsp;&nbsp;&nbsp;H 335", " May cause respiratory irritation"),
                (Paragraph("<u>Precautionary statement – Prevention:</u>",prepare_custom_styles()['LeftAligned']), ""),
                ("&nbsp;&nbsp;&nbsp;&nbsp;P 261", "Avoid breathing dust/fume/gas/mist/vapours/spray"),
                ("&nbsp;&nbsp;&nbsp;&nbsp;P 285",
                 "In case of inadequate ventilation wear respiratory protection"),
                (Paragraph("<u>Precautionary statement – Response:</u>",prepare_custom_styles()['LeftAligned']), ""),
                ("&nbsp;&nbsp;&nbsp;&nbsp;P 304 + P 341",
                 "IF INHALED, breathing if difficult, remove victim to fresh air and keep at rest position "
                 "comfortable for breathing"),
                ("&nbsp;&nbsp;&nbsp;&nbsp;P 342 + P 311",
                 "If experiencing respiratory symptoms: Call POISON CENTER or doctor/physician"),
                (Paragraph("<u>Precautionary statement – Disposal:</u>", prepare_custom_styles()['LeftAligned']), ""),
                ("&nbsp;&nbsp;&nbsp;&nbsp;P 501",
                 "Dispose of contents/container in accordance with local/regional/national/international "
                 "regulation"),
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
            "subsection_title": "",
            "content": Paragraph("In case of unintended overexposure, the following measures apply:")
        }, {
            "subsection_title": "4.1 &nbsp;&nbsp;&nbsp;Description of first aid measures",
            "content": [
                ("General advice",
                 """Consult a physician; show this safety data sheet to the doctor in attendance. Move out of 
                 dangerous area."""),
                ("If Inhaled",
                 """Move person to fresh air. Loosen the clothing and place the victim in a position 
                 comfortable for breathing. Maintain an open airway but avoid further exposure. If not breathing, 
                 if breathing is irregular or if respiratory arrest occurs, provide artificial respiration or oxygen 
                 by trained personnel. Avoid mouth to mouth resuscitation, as it will be dangerous for the person 
                 providing this aid. Consult a physician if symptoms persist."""),
                ("In case of skin contact",
                 """Flush contaminated skin with plenty of water. Remove contaminated clothing and shoes. Wash 
                 the clothes and clean shoes thoroughly before reuse. Consult a physician if symptoms persist."""),
                ("In case of eye contact",
                 """Immediately flush eye(s) with plenty of water for at least 10 minutes. Check for and 
                 remove any contact lenses. Continue rinsing. Consult a physician if symptoms persist"""),
                ("If Swallowed",
                 """Rinse the mouth with water and give small quantities of water to drink (only if the person 
                 is conscious). Do not induce vomiting unless directed to do so by medical personnel. Consult a 
                 physician if symptoms persist."""),
            ]}, {
            "subsection_title": "4.2 &nbsp;&nbsp;&nbsp;Most important symptoms and effects, both acute and delayed",
            "content": [
                ("Inhalation",
                 """Inhalation of drops or spray may cause irritation to the respiratory system. May entail 
                 sensitization via inhalation. Sensitive people may develop asthma following inhalation of this 
                 substance."""),
                ("Ingestion", "May entail gastrointestinal problems"),
                ("Contact with skin", "Prolonged or repeated contact with the skin may cause irritation."),
                ("Contact with eyes", "May cause eye irritation (Redness)"),
            ]}, {
            "subsection_title": "4.3 &nbsp;&nbsp;&nbsp;Indication of any immediate medical attention and special "
                                "treatment needed",
            "content": [
                ("Notes to physician", "Treat symptomatically"),
                ("Specific treatments", "No specific treatment.")
            ]}
        ],

        # # SECTION 5: Firefighting Measures
        "SECTION 5 – FIREFIGHTING MEASURES": [{
            "subsection_title": "5.1 &nbsp;&nbsp;&nbsp;Extinguishing media",
            "content": Paragraph(
                """<u>Suitable extinguishing media- </u><br/>Use water spray, alcohol-resistant foam, dry chemical 
                powders or carbonic gas for small fires, and appropriate extinguisher for the surrounding materials.""",
                prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "5.2 &nbsp;&nbsp;&nbsp;Special hazards arising from the substance or mixture",
                "content": Paragraph("Nature of decomposition product is unknown.", prepare_custom_styles()['Normal'])},
            {
                "subsection_title": "5.3 &nbsp;&nbsp;&nbsp;Advice for firefighters",
                "content": Paragraph("""Wear self-contained breathing apparatus (SCBA) with chemical resistant gloves 
                and chemical protection suit conforming to European standard EN469. Avoid inhaling gases and fumes. 
                Avoid contact with skin, eyes and clothes. Isolate the affected area by removing the persons from the 
                vicinity of the incident""",prepare_custom_styles()['Normal'])},
            # {
            #     "subsection_title": "5.4 &nbsp;&nbsp;&nbsp;Further Information",
            #     "content": Paragraph("No Data available", prepare_custom_styles()['Normal'])
            # }
        ],

        # SECTION 6: Accidental Release Measures
        "SECTION 6 – ACCIDENTAL RELEASE MEASURES": [{
            "subsection_title": "6.1 &nbsp;&nbsp;&nbsp;Personal precautions, protective equipment and emergency "
                                "procedures",
            "content": Paragraph("""<u>For non-emergency personnel-</u><br/>Evacuate the area of the spillage. Avoid 
            contact with the eyes, skin and clothing. Provide sufficient ventilation. Use appropriate protective 
            clothing. <br/><br/>
            <u>For emergency responders-</u><br/>If specialized clothing is required to deal with the spillage, take not of any information in Section 8 on suitable and unsuitable materials. See also the information in the above section “for non-emergency personnel”.""", prepare_custom_styles()['Normal'])
        }, {
            "subsection_title": "6.2 &nbsp;&nbsp;&nbsp;Environmental precautions",
            "content": Paragraph("Do not let product enter drains. Collect any spillage.", prepare_custom_styles()['Normal'])
        }, {
            "subsection_title": "6.3 &nbsp;&nbsp;&nbsp;Methods and materials for containment and cleaning up",
            "content": Paragraph("""Pickup and arrange disposal. Sweep up, vacuum clean using HEPA filters or shovel. Keep in suitable, closed containers for disposal. Flush the remaining spillage with water. Ensure sufficient ventilation.""", prepare_custom_styles()['Normal'])
        }, {
            "subsection_title": "6.4 &nbsp;&nbsp;&nbsp;Reference to other sections",
            "content": Paragraph(
                "For disposal see section 13 and see section 8 for individual protective equipment.",
                prepare_custom_styles()['Normal'])

        }],

        # SECTION 7: Handling and Storage
        "SECTION 7 – HANDLING AND STORAGE": [{
            "subsection_title": "7.1 &nbsp;&nbsp;&nbsp;Precautions for safe handling",
            "content": Paragraph("""Avoid any aerosol formation. Ensure adequate ventilation in the area of usage. Use in a bonded area. Avoid contact with skin, eyes, and clothes. Put on appropriate protective equipment (Refer to section 8). Do not eat, drink or smoke in the area where this material is handled.""", prepare_custom_styles()['Normal'])
        }, {
            "subsection_title": "7.2 &nbsp;&nbsp;&nbsp;Conditions for safe storage, including any "
                                "incompatibilities",
            "content": Paragraph("Always store product in a clean, cool, dry and well ventilated space. Keep product away from direct sunlight, with temperatures below 10°C.",
                                 prepare_custom_styles()['Normal'])
        }, {
            "subsection_title": "7.3 &nbsp;&nbsp;&nbsp;Specific end use(s)",
            "content": Paragraph("Substance intended to catalyze reactions during industrial processes.",
                                 prepare_custom_styles()['Normal'])
        }],

        # SECTION 8: Exposure Controls/Personal Protection
        "SECTION 8 – EXPOSURE CONTROLS/PERSONAL PROTECTION": [{
            "subsection_title": "8.1 &nbsp;&nbsp;&nbsp;Control parameters",
            "content": Paragraph("<u>Components with workplace control parameters-</u><br/>This product, as supplied, does not contain any hazardous materials or substances with occupational exposure limits.", prepare_custom_styles()['Normal'])
        },{
            "subsection_title": "8.2 &nbsp;&nbsp;&nbsp;Exposure controls",
            "content": [
                (Paragraph("<u>Personal protective equipment-</u>", prepare_custom_styles()['LeftAligned']), ""),
                ("Eye/Face protection", "Face shield or respirator"),
                ("Skin Protection", "Wear appropriate protective clothing"),
                ("Body Protection", "Wear appropriate gloves, clothes"),
                ("Respiratory Protection", "Face shield or respirator"),
                ("Control of environment exposure",
                 "Do not let product enter drains. Notify local authorities if significant leaks and cannot be contained"),
                ("Engineering controls", "Ensure the area is adequately ventilated."),
                ("Hygiene measures", "Follow good industrial hygiene measures. Wash your hands and forearm after handling the material. Wash contaminated clothes before reusing."),
                ("Environmental exposure control", "None")
            ]
        }],

        # SECTION 9: Physical and Chemical Properties
        "SECTION 9 – PHYSICAL AND CHEMICAL PROPERTIES": [{
            "subsection_title": "9.1 &nbsp;&nbsp;&nbsp;Information on basic physical and chemical properties",
            "content": [
                ("1. &nbsp; Appearance", f"{product_data['appearance']}"),  #Dynamic
                ("2. &nbsp; Color", f"{product_data['color']}"),  #Dynamic
                ("""3. &nbsp;Odor threshold, pH, Melting point/Freezing point, Initial boiling point/ boiling point range, Flash point, Evaporation rate, Flammability (Solid, Gas), Upper/Lower flammability or explosive limits, Vapor pressure, Vapor density, Density, Water solubility, Partition coefficient, Auto ignition temperature, Decomposition temperature, Viscosity, Explosive properties, Oxidizing properties""", "Data Not Relevant"),
            ]}, {
            "subsection_title": "9.2 &nbsp;&nbsp;&nbsp;Other safety information",
            "content": Paragraph("No data available", prepare_custom_styles()['Normal'])
        }],

        # SECTION 10: Stability and Reactivity
        "SECTION 10 – STABILITY AND REACTIVITY": [{
            "subsection_title": "",
            "content": [
                ("<b>10.1</b> Reactivity", "The product is stable and non-reactive under normal conditions of use, storage & transport."),
                ("<b>10.2</b> Chemical Stability", "Stable under recommended conditions"),
                ("<b>10.3</b> Possibility of hazardous reaction", "N/A under recommended conditions"),
                ("<b>10.4</b> Conditions to avoid", "See section 5 and 7"),
                ("<b>10.5</b> Incompatible Materials", "No special recommendations"),
                ("<b>10.6</b> Hazardous decomposition products", "No hazardous decomposition products."),
            ]
        }],

        # SECTION 11: Toxicological Information
        "SECTION 11 – TOXICOLOGICAL INFORMATION": [{
            "subsection_title": "11.1 &nbsp;&nbsp;&nbsp;Information on toxicological effects",
            "content": [
                (Paragraph("<i>Potential acute effects on the health</i>", prepare_custom_styles()['LeftAligned']),""),
                ("Inhalation","May entail sensitization"),
                ("Ingestion","No Data Available"),
                ("Acute toxicity", "No data available"),
                ("Skin corrosion/irritation", "May entail irritation"),
                ("Serious eye damage/eye irritation", "No data available"),
                ("Respiratory or skin sensitization", "May entail irritation"),
                (Paragraph("<br/><br/><i>Potential chronic effects on the health</i>", prepare_custom_styles()['LeftAligned']),""),
                ("Germ cell mutagenicity", "No data available"),
                ("Carcinogenicity", "No data available"),
                ("Reproductive toxicity", "No data available"),
                ("Specific target organ toxicity- Single exposure", "No data available"),
                ("Specific target organ toxicity- Repeated exposure(s)", "No data available"),
                ("Aspiration hazard", "No data available"),
                ("Teratogenicity","No data available"),
                ("Effects on development/fertility", "No data available"),
                ("Chronic toxicity", "No data available"),
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
            "content": [
                ("<b>12.1</b> Toxicity", "No data available"),
                ("<b>12.2</b> Persistence and degradability", "No data available"),
                ("<b>12.3</b> Bioaccumulative potential", "No data available"),
                ("<b>12.4</b> Mobility in soil", "No data available"),
                ("<b>12.5</b> Other adverse effects", "No data available"),
            ]}, {
            "subsection_title": "",
            "content": Paragraph("""Comments: The preparation is considered as non-hazardous for the environment, mobility, persistence, degradability, bioaccumulation potential, toxicity in the aquatic environment and other data relative to eco-toxic.""", prepare_custom_styles()['Normal'])
        }],

        # SECTION 13: Disposal Considerations
        "SECTION 13 – DISPOSAL CONSIDERATIONS": [{
            "subsection_title": "13.1 &nbsp;&nbsp;&nbsp;Waste treatment methods",
            "content": Paragraph("""Dispose of waste in compliance with national and local laws, environment protection rules. Wastewater must be evacuated to a purification plant. The waste code must be allocated by the user according to the application of product. Avoid or minimize the generation of waste as much as possible""",
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
                (Paragraph("<i>European legislation for international transport</i>", prepare_custom_styles()['LeftAligned']),""),
                (Paragraph("ADR/RID: not applicable",prepare_custom_styles()['LeftAligned']),Paragraph("IMDG: not applicable", prepare_custom_styles()['LeftAligned'])),
                (Paragraph("ADNR: not applicable", prepare_custom_styles()['LeftAligned']),Paragraph("IATA: not applicable", prepare_custom_styles()['LeftAligned']))
            ]
        }],
        #
        # SECTION 15: Regulatory Information
        "SECTION 15 – REGULATORY INFORMATION": [{
            "subsection_title": "15.1 &nbsp;&nbsp;&nbsp;<i>Health, safety and environmental regulations/legislation specific to the substance of mixture</i>",
            "content": Paragraph("""The substance complies with article 16 of regulation 689/2008 on the export and import of hazardous chemical products.<br/> It complies with regulation 882/2004 relative to the official controls undertaken to check conformity with the legislation on animal feed, foodstuffs and Regulation 178/2002 establishing the general principles and the general prescriptions of the food legislation instituting the European Food Safety Authority and fixing procedures on the safety of foodstuffs.""", prepare_custom_styles()['Normal'])
        }, {
            "subsection_title": "15.2 &nbsp;&nbsp;&nbsp;<i>Evaluation of chemical safety</i>",
            "content": Paragraph("""The substance has not been subject to an evaluation of chemical safety.""", prepare_custom_styles()['Normal'])
        }
        ],

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
            "content": Paragraph("""The above information is believed to be correct but does not purport to be all inclusive and shall be used only as a guide for the independent verification of the user. The information in this document is based on the present state of our knowledge and is applicable to the product with regard to appropriate safety precautions. It does not represent any guaranty or warranty. Certain guidelines above may be broader than actually required in order to ensure all material is handled with the utmost care.  The company and its affiliates assume no liability for any damage resulting from handling or contact with the above product.  See the Company’s confirmation of purchase order for additional terms and conditions of sale. 
The format of this safety datasheet complies with regulation CE/453/2010. A REACH registration number may be allocated to enzymes owing to their possible technical applications. Enzymes used as manufacturing auxiliaries for the “food” or “feed” products are partially exempted for REACH registrations, including the establishment of scenarios of exposure. The legislation in force applicable to these areas must be taken into account.
""", prepare_custom_styles()['justify'])}
        ],
    }
