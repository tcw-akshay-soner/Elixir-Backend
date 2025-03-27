from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
import pytz

# Set Indian timezone
IST = pytz.timezone("Asia/Kolkata")

class LoginRequest(BaseModel):
    email: str
    password: str

class IngredientData(BaseModel):
    ing_item_code: str = Field(...)
    ing_name: str = Field(...)
    seq_no: int
    other_ing: int
    per_composition: float
    alpha_composition: str


class Items(BaseModel):
    product_id: str = Field(...)
    ingredients: List[IngredientData]  # A list of ingredients
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)

class Symbols(BaseModel):
    # symbol_id: int = Field(...)
    symbol_name: str = Field(...)
    symbol: str = Field(...)
    symbol_code: str = Field(...)
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)

class Product(BaseModel):
    product_id: str = Field(...)
    product_name: str = Field(...)
    symbol_id: Optional[int] = Field(None, alias="symbol_id")
    identified_uses: Optional[str] = Field(None, alias="identified_uses_of_application")
    mixtures: Optional[str] = Field(None, alias="mixtures_of_application")
    appearance: Optional[str] = Field(None, alias="product_appearance")
    color: Optional[str] = Field(None, alias="product_color")
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
    calories: Optional[float] = None 
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None 
    protein: Optional[float] = None
    moisture: Optional[float] = None
    ash: Optional[float] = None
    created_at: Optional[datetime] = datetime.now(tz=IST)
    updated_at: Optional[datetime] = datetime.now(tz=IST)

class GlobalUpdates(BaseModel):
    ing_item_code: Optional[str] = None
    ing_name: Optional[str] = None
    cas_num: Optional[str] = None
    ec_num: Optional[str] = None
    ing_type: Optional[str] = None
    source_type: Optional[str] = None
    source: Optional[str] = None
    calories: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    protein: Optional[float] = None
    moisture: Optional[float] = None
    ash: Optional[float] = None
    updated_at: Optional[datetime] = datetime.now(tz=IST)

class RowUpdates(BaseModel):  # 🔹 Fields that apply to specific rm_code
    rm_code: Optional[str] = None
    vendor: Optional[str] = None
    country_origin: Optional[str] = None

class IngredientUpdate(BaseModel):  # 🔹 Main Update Request Model
    ing_item_code: str
    global_updates: Optional[GlobalUpdates] = None
    row_updates: Optional[List[RowUpdates]] = None

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
    wheat: Optional[str] = None
    eggs: Optional[str] = None
    crustaceans_shell_fish: Optional[str] = None
    fish: Optional[str] = None
    milk: Optional[str] = None
    tree_nuts: Optional[str] = None
    peanuts: Optional[str] = None
    soy: Optional[str] = None
    sesame_seeds: Optional[str] = None
    celery: Optional[str] = None
    barley_oats_rye_spelt: Optional[str] = None
    orange_kiwi_peaches_apples: Optional[str] = None
    mushrooms: Optional[str] = None
    mustard: Optional[str] = None
    lupin: Optional[str] = None
    molluscs: Optional[str] = None
    sulfur: Optional[str] = None
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
    company_name: str
    product_id: str
    template_name: str
    customer_name: Optional[str] = None

# ----------------------
# User Schemas
# ----------------------

class Roles(str, Enum):
    user = "user"
    admin = "admin"


class UserBase(BaseModel):
    email: EmailStr
    name : str
    is_active : bool
    role : Roles = Roles.user # Explicitly set default role and Enum Usage
    # password: Optional[str] = None  # Add this field (not recommended)

class UserCreate(UserBase):
    password: str  # Password required for account creation
    
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[Roles] = None    

class UserResponse(UserBase):
    token: str # Includes JWT Token in response

class UserWithPassword(UserBase):
    password: str  # Includes password

class AdminDashboardResponse(BaseModel):
    message: str
    Users: List[UserWithPassword]
    

