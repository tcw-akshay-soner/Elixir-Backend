from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Boolean, func, TIMESTAMP, \
    ForeignKey, Enum
from src.engine.pharma_db import metadata, Base
from src.model.model import Roles

symbols = Table(
    "symbols",
    metadata,
    Column("symbol_id", Integer, primary_key=True, autoincrement=True, nullable=False),
    Column("symbol_name", String, nullable=True),
    Column("symbol", String, nullable=True),
    Column("symbol_code", String, nullable=True, unique=True),
    Column("created_at", DateTime,server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now())
)

items = Table(
    "items",
    metadata,
    Column("product_id", String, nullable=False),
    Column("ing_item_code", String, nullable=False),
    Column("seq_no", Integer, nullable=True),
    Column("ing_name", String, nullable=False),
    Column("other_ing", Integer, nullable=True),
    Column("per_composition", Float, nullable=True),
    Column("alpha_composition", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now())
)

product = Table(
    "product",
    metadata,
    Column("product_id", String, primary_key=True, unique=True, nullable=False),  # Auto-increment for unique ID
    Column("product_name", String, nullable=False),
    Column("symbol_id", Integer, ForeignKey("symbols.symbol_id"), nullable=True),
    Column("identified_uses", String, nullable=True),
    Column("mixtures", String, nullable=True),
    Column("appearance", String, nullable=True),
    Column("color", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now()),
)

ingredient = Table(
    "ingredient",
    metadata,
    Column("ing_item_code", String, primary_key=True, nullable=False),
    Column("ing_name", String, nullable=False),
    Column("symbol_id", Integer, ForeignKey("symbols.symbol_id"), nullable=True),
    Column("vendor", String, nullable=False),
    Column("rm_code", String, primary_key=True, nullable=False),
    Column("cas_num", String, nullable=True),
    Column("ec_num", String, nullable=True),
    Column("ing_type", String, nullable=True),
    Column("source_type", String, nullable=True),
    Column("source", String, nullable=True),
    Column("country_origin", String, nullable=True),
    Column("calories", Float, nullable=True),
    Column("fat", Float, nullable=True),
    Column("carbohydrates", Float, nullable=True),
    Column("protein", Float, nullable=True),
    Column("moisture", Float, nullable=True),
    Column("ash", Float, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now()),
)

declaration = Table(
    "declaration",
    metadata,
    Column("ing_item_code", String, primary_key=True, nullable=False),
    Column("rm_code", String, primary_key=True, nullable=True),
    Column("vegetarian", String, nullable=True),
    Column("vegan", String, nullable=True),
    Column("non_gmo", String, nullable=True),
    Column("classification", String, nullable=True),
    Column("gluten_status", String, nullable=True),  # Gluten Free/ Gluten Containing
    Column("bse_tse", String, nullable=True),
    Column("declared_allergen", String, nullable=True),
    Column("wheat", String, nullable=True),
    Column("eggs", String, nullable=True),
    Column("crustaceans_shell_fish", String, nullable=True),
    Column("fish", String, nullable=True),
    Column("milk", String, nullable=True),
    Column("tree_nuts", String, nullable=True),
    Column("peanuts", String, nullable=True),
    Column("soy", String, nullable=True),
    Column("sesame_seeds", String, nullable=True),
    Column("celery", String, nullable=True),
    Column("barley_oats_rye_spelt", String, nullable=True),
    Column("orange_kiwi_peaches_apples", String, nullable=True),
    Column("mushrooms", String, nullable=True),
    Column("mustard", String, nullable=True),
    Column("lupin", String, nullable=True),
    Column("molluscs", String, nullable=True),
    Column("sulfur", String, nullable=True),
    Column("allergen_fermentation", String, nullable=True),
    Column("residual_solvent", String, nullable=True),
    Column("wada_compliance", String, nullable=True),
    Column("eto_treated", String, nullable=True),
    Column("irradiated", String, nullable=True),
    Column("sewage_sludge_treated", String, nullable=True),
    Column("pesticide", String, nullable=True),
    Column("aflatoxin", String, nullable=True),
    Column("preservative", String, nullable=True),
    Column("antibiotic", String, nullable=True),
    Column("gras", String, nullable=True),
    Column("prop65_complaint", String, nullable=True),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, onupdate=func.now())
)

fda = Table(
    "fda",
    metadata,
    Column("company_id", Integer, primary_key=True, autoincrement=True),  # Auto-increment for unique ID
    Column("company_name", String, nullable=False),
    Column("fda_reg", String, unique=True, nullable=False)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(64), nullable=False)
    email = Column(String(32), primary_key=True, unique=True, index=True, nullable=False)
    password = Column(String(32), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(Roles), default = Roles.user, nullable = False) # Fixed default role to user and Enum Usage
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())
    
