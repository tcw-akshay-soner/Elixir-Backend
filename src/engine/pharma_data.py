from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.engine.pharma_db import engine
from src.model.schemas import fda, product, items, ingredient, declaration, symbols
from rich import print

# Create session factory
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Dependency to get database session
async def fetch_fda(company):
    async with async_session() as session:
        try:
            query = select(fda.c.fda_reg).where(fda.c.company_name == company)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)


async def fetch_product(product_id):
    async with (async_session() as session):
        try:
            query = select(product, symbols).join(
                symbols,
                symbols.c.symbol_id == product.c.symbol_id
            ).where(product.c.product_id == product_id)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)


async def fetch_composition(product_id):
    async with async_session() as session:
        try:
            query = select(items).where(items.c.product_id == product_id).order_by(items.c.seq_no)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)


# asyncio.run(fetch_composition('FGBA018'))

async def fetch_ingredient_data(product_id):
    async with async_session() as session:
        try:
            query = (select(ingredient, items, symbols)
                     .join(items, ingredient.c.ing_item_code == items.c.ing_item_code)
                     .join(symbols, ingredient.c.symbol_id == symbols.c.symbol_id, isouter=True)
                     .where(items.c.product_id == product_id)
                     .order_by(items.c.seq_no))
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)


async def fetch_declaration_data(product_id):
    async with async_session() as session:
        try:
            query = select(declaration).join(
                items,
                declaration.c.ing_item_code == items.c.ing_item_code,
                isouter=True
            ).where(items.c.product_id == product_id).order_by(items.c.seq_no)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)

# async def fetch_symbols_data(product_id):
#     async with async_session() as session:
#         try:
#             query = select(symbols).join(
#                 product,
#                 product.c.symbol_id == symbols.c.symbol_id,
#                 isouter=True
#             ).where(product.c.product_id == product_id)
#             result = await session.execute(query)
#             data = result.fetchall()
#             logging.info(data)
#             return [dict(row._mapping) for row in data]
#         except SQLAlchemyError as e:
#             print(e)

# asyncio.run(fetch_declaration_data('FGBE222'))
