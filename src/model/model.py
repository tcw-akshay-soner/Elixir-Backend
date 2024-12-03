from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Boolean, func, TIMESTAMP
from datetime import  datetime as dt
from src.engine.pharma_db import metadata
from pydantic import BaseModel
import pytz

# Set Indian timezone
IST = pytz.timezone("Asia/Kolkata")

items = Table(
    "items",
    metadata,
    Column("product_id", String, nullable = True),              
    Column("ing_item_code", String, nullable = False),      
    Column("ing_name", String, nullable = False),                 
    Column("per_composition", Float, nullable = False),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)    
)

product = Table(
    "product",
    metadata,
    Column("product_id", String, primary_key = True, unique= True, nullable=False),  # Auto-increment for unique ID
    Column("product_name", String, nullable = False), 
    Column("created_at", DateTime, nullable = True),
    Column("updated_at", DateTime, nullable = True)
)

ingredient = Table(
    "ingredient",
    metadata,
    Column("ing_item_code", String, primary_key = True, nullable = False),
    Column("ing_name", String, nullable = False),
    Column("vendor", String, nullable = False),                  
    Column("rm_code", String, primary_key = True, nullable = False),
    Column("cas_num", String, nullable = True),
    Column("ec_num", String, nullable = True),
    Column("ing_type", String, nullable = True),
    Column("source_type", String, nullable = True),
    Column("source", String, nullable = True),
    Column("country_origin", String, nullable = True),
    Column("created_at", DateTime, nullable=True),
    Column("updated_at", DateTime, nullable=True),
)

declaration = Table(
    "declaration",
    metadata,
    Column("ing_item_code", String, primary_key = True, nullable = False),
    Column("rm_code", String, primary_key = True, nullable = True),
    Column("vegetarian", String, nullable = True),
    Column("vegan", String, nullable = True),
    Column("non_gmo", String, nullable = True),
    Column("classification", String, nullable = True),
    Column("gluten_status", String, nullable = True),  # Gluten Free/ Gluten Containing
    Column("bse_tse", String, nullable = True),
    Column("declared_allergen", String, nullable = True),
    Column("wheat", String, nullable = True),
    Column("eggs", String, nullable = True),
    Column("crustaceans_shell_fish", String, nullable = True),
    Column("fish", String, nullable = True),
    Column("milk", String, nullable = True),
    Column("tree_nuts", String, nullable = True),
    Column("peanuts", String, nullable = True),
    Column("soy", String, nullable = True),
    Column("sesame_seeds", String, nullable = True),
    Column("celery", String, nullable = True),
    Column("barley_oats_rye_spelt", String, nullable = True),
    Column("orange_kiwi_peaches_apples", String, nullable = True),
    Column("mushrooms", String, nullable = True),
    Column("mustard", String, nullable = True),
    Column("lupin", String, nullable = True),
    Column("mulluscs", String, nullable = True),
    Column("sulfur", String, nullable = True),
    Column("allergen_fermentation", String, nullable = True),
    Column("residual_solvent", String, nullable = True),
    Column("wada_compliance", String, nullable = True),
    Column("eto_treated", String, nullable = True),
    Column("irradiated", String, nullable = True),
    Column("sewage_sludge_treated", String, nullable = True),
    Column("pesticide", String, nullable = True),
    Column("aflatoxin", String, nullable = True),
    Column("preservative", String, nullable = True),
    Column("antibiotic", String, nullable = True),
    Column("gras", String, nullable = True),
    Column("prop65_complaint", String, nullable = True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)

fda = Table(
    "fda",
    metadata,
    Column("company_id", Integer, primary_key = True, autoincrement = True),  # Auto-increment for unique ID
    Column("company_name", String, nullable = False),
    Column("fda_reg", String, unique = True ,nullable = False)
)


from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class IngredientData(BaseModel):
    ing_item_code: str = Field(...)
    ing_name: str = Field(...)
    per_composition: float

class Items(BaseModel):
    product_id: str = Field(...)
    ingredients: List[IngredientData]  # A list of ingredients
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)
        
class Product(BaseModel):
    product_id: str = Field(...)
    product_name: str = Field(...)
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)

# Ingredient Pydantic model matching the "ingredient" table
class Ingredient(BaseModel):
    ing_item_code: str = Field(..., alias="ingredient_item_code")
    ing_name: str = Field(..., alias="ingredient_name")
    vendor: str = Field(...)
    rm_code: str = Field(...)
    cas_num: Optional[str] = Field(None, alias="cas_number")
    ec_num: Optional[str] = Field(None, alias="ec_number")
    ing_type: str = Field(..., alias="ingredient_type")
    source_type: str = Field(...)
    source: str = Field(...)
    country_origin: str = Field(..., alias="country_of_origin")
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)

# Declaration Pydantic model matching the "declaration" table
class Declaration(BaseModel):
    ing_item_code: str = Field(...)
    rm_code: str = Field(...)
    vegetarian: Optional[str] = None
    vegan: Optional[str] = None
    non_gmo: Optional[str] = None
    classification: Optional[str] = None
    gluten_status: Optional[str] = None
    bse_tse: Optional[str] = None
    declared_allergen: Optional[str] = None
    wheat : Optional[str] = None
    eggs : Optional[str] = None
    crustaceans_shell_fish : Optional[str] = None
    fish : Optional[str] = None
    milk : Optional[str] = None 
    tree_nuts : Optional[str] = None
    peanuts : Optional[str] = None
    soy : Optional[str] = None
    sesame_seeds : Optional[str] = None
    celery : Optional[str] = None
    barley_oats_rye_spelt : Optional[str] = None
    orange_kiwi_peaches_apples : Optional[str] = None
    mushrooms : Optional[str] = None
    mustard : Optional[str] = None
    lupin : Optional[str] = None
    mulluscs : Optional[str] = None
    sulfur : Optional[str] = None
    allergen_fermentation: Optional[str] = None
    residual_solvent: Optional[str] = None
    wada_compliance: Optional[str] = None
    eto_treated: Optional[str] = None
    irradiated: Optional[str] = None
    sewage_sludge_treated: Optional[str] = None
    pesticide: Optional[str] = None
    aflatoxin: Optional[str] = None
    preservative: Optional[str] = None
    antibiotic: Optional[str] = None
    gras: Optional[str] = None
    prop65_complaint: Optional[str] = None
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)

class FDA(BaseModel):
    company_id: int = Field(...)
    company_name: str = Field(...)
    fda_reg: str = Field(...)


class GenerateRequest(BaseModel):
    company_name : str
    product_id : str
    template_name : str
    customer_name : Optional[str] = None