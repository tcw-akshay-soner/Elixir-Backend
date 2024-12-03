from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

from src.engine.pharma_db import engine
from src.model.model import fda, product, items, ingredient, declaration

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
    async with async_session() as session:
        try:
            query = select(product.c.product_name).where(product.c.product_id == product_id)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)


async def fetch_composition(product_id):
    async with async_session() as session:
        try:
            query = select(items.c.ing_item_code,items.c.ing_name, items.c.per_composition).where(items.c.product_id == product_id)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)


# asyncio.run(fetch_composition('FGBA018'))

async def fetch_ingredient_data(product_id):
    async with async_session() as session:
        try:
            query = select(items.c.ing_name,ingredient).join(
                items,
                ingredient.c.ing_item_code == items.c.ing_item_code,
                isouter=True  # LEFT JOIN
            ).where(items.c.product_id == product_id)
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
            ).where(items.c.product_id == product_id)
            result = await session.execute(query)
            data = result.fetchall()
            return [dict(row._mapping) for row in data]
        except SQLAlchemyError as e:
            print(e)

# asyncio.run(fetch_declaration_data('FGBE222'))
