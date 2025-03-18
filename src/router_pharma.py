# Import necessary modules
from datetime import datetime
from functools import partial
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Query
from starlette.responses import JSONResponse, FileResponse
from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from contextlib import asynccontextmanager
import os
import tempfile
from typing import List, Optional
# Import engine and metadata
from src.engine.pharma_db import engine, metadata, get_db, Base
from src.model.model import (
    IngredientUpdate,
    Product,
    Ingredient,
    Declaration,
    Items,
    Symbols,
    GenerateRequest
)
from src.model.schemas import (
    product,
    ingredient,
    declaration,
    symbols,
    items,
)
# Import templates
from src.template_file.template_A_gras import create_template_gras
from src.template_file.template_A_ediblesource_ import create_template_edible
from src.template_file.template_BSE_TSE import create_template_bsetse
from src.template_file.template_compostion import create_template_composition
from src.template_file.template_COO2_01A0 import create_template_COO2
from src.template_file.template_COO3_01A0 import create_template_COO3
from src.template_file.template_COO_01A0 import create_template_coo
from src.template_file.template_COS_02A0 import create_template_COS
from src.template_file.template_customer_SEB import create_template_customer_seb
from src.template_file.template_FSMA_01A0 import create_template_fsma
from src.template_file.template_gluten import create_template_gluten
from src.template_file.template_lotcode_02A0 import create_template_lotcode
from src.template_file.template_heavyMetal import create_template_heavymetal
from src.template_file.template_NonISE import create_template_nonise
from src.template_file.template_Nutritional import create_template_nutritional
from src.template_file.template_percomposition import create_template_percomposition
from src.template_file.template_ppr import create_template_ppr
from src.template_file.templateFDA_Reg_01A0 import create_template_fda
from src.template_file.template_SEB_nongmo import create_template_nongmo
from src.template_file.templateContact_SEB_01A0 import create_template_contact
from src.template_file.template_SEB_SS import create_template_ss
from src.template_file.template_vegan import create_template_vegan
from src.template_file.template_vegetarian import create_template_vegetarian
from src.template_file.templateAllergen import create_template_allergen
from src.template_file.template_SDS import create_sds_pdf
from src.template_file.template_mflow import create_template_mflow
from src.template_file.template_microorganisms import create_template_microorganisms
from src.utilities.utils import check_permission


# Set up FastAPI app with async lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        # Create tables for metadata (for Table-based models)
        await conn.run_sync(metadata.create_all)

        # Create tables for ORM-based models like User
        await conn.run_sync(Base.metadata.create_all)

    yield
    # Shutdown: dispose engine
    await engine.dispose()


# Set up router
mainRouter = APIRouter(lifespan=lifespan)


def get_router() -> APIRouter:
    return mainRouter


@mainRouter.post("/product_composition")
async def create_data(
        data: Items, data1: Product, db: AsyncSession = Depends(get_db)
):
    try:
        for ingredient in data.ingredients:
            items_query = insert(items).values(
                product_id=data.product_id,
                ing_item_code=ingredient.ing_item_code,
                seq_no=ingredient.seq_no,
                ing_name=ingredient.ing_name,
                other_ing=ingredient.other_ing,
                per_composition=ingredient.per_composition,
                alpha_composition=ingredient.alpha_composition,
                created_at=data.created_at
            )
            await db.execute(items_query)
        # Check if the product exists in the 'products' table
        product_check_query = select(product.c.product_id).where(product.c.product_id == data1.product_id)
        result = await db.execute(product_check_query)
        product_exists = result.scalar()

        if not product_exists:
            # Insert into 'products' table if the product does not exist
            product_query = insert(product).values(
                product_id=data1.product_id,
                product_name=data1.product_name,
                symbol_id=data1.symbol_id,
                identified_uses=data1.identified_uses,
                mixtures=data1.mixtures,
                appearance=data1.appearance,
                color=data1.color,
                created_at=data1.created_at,
            )
            await db.execute(product_query)

        await db.commit()
        return {"message": "Product Composition data inserted successfully!"}
    except SQLAlchemyError as e:
        # Rollback in case of failure
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@mainRouter.post("/symbols")
async def create_sysmbols_data(data: Symbols, db: AsyncSession = Depends(get_db)):
    try:
        # Insert into the 's' table
        query = insert(symbols).values(
            # symbol_id=data.symbol_id,
            symbol_name=data.symbol_name,
            symbol=data.symbol,
            symbol_code=data.symbol_code,
            created_at=data.created_at  # Ensure this column exists in the model
        )

        await db.execute(query)
        await db.commit()
        return {"message": "Symbols data inserted successfully!"}
    except SQLAlchemyError as e:
        # Rollback in case of failure
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@mainRouter.post("/raw_material")
async def create_raw_data(data: Ingredient, data1: Declaration, db: AsyncSession = Depends(get_db)):
    try:
        # Insert into the 'ingredient' table
        query = insert(ingredient).values(
            ing_item_code=data.ing_item_code,
            ing_name=data.ing_name,
            vendor=data.vendor,
            rm_code=data.rm_code,
            cas_num=data.cas_num,
            ec_num=data.ec_num,
            # ing_type=data.ing_type,
            source_type=data.source_type,
            source=data.source,
            country_origin=data.country_origin,
            calories=data.calories,
            fat=data.fat,
            carbohydrates=data.carbohydrates,
            protein=data.protein,
            moisture=data.moisture,
            ash=data.ash,
            created_at=data.created_at  # Ensure this column exists in the model
        )

        # Insert into the 'declaration' table
        query1 = insert(declaration).values(
            ing_item_code=data1.ing_item_code,
            rm_code=data1.rm_code,
            vegetarian=data1.vegetarian,
            vegan=data1.vegan,
            non_gmo=data1.non_gmo,
            classification=data1.classification,
            gluten_status=data1.gluten_status,
            bse_tse=data1.bse_tse,
            # declared_allergen=data1.declared_allergen,
            wheat=data1.wheat,
            eggs=data1.eggs,
            crustaceans_shell_fish=data1.crustaceans_shell_fish,
            fish=data1.fish,
            milk=data1.milk,
            tree_nuts=data1.tree_nuts,
            peanuts=data1.peanuts,
            soy=data1.soy,
            sesame_seeds=data1.sesame_seeds,
            celery=data1.celery,
            barley_oats_rye_spelt=data1.barley_oats_rye_spelt,
            orange_kiwi_peaches_apples=data1.orange_kiwi_peaches_apples,
            mushrooms=data1.mushrooms,
            mustard=data1.mustard,
            lupin=data1.lupin,
            molluscs=data1.molluscs,
            sulfur=data1.sulfur,
            # allergen_fermentation=data1.allergen_fermentation,
            residual_solvent=data1.residual_solvent,
            wada_compliance=data1.wada_compliance,
            eto_treated=data1.eto_treated,
            irradiated=data1.irradiated,
            sewage_sludge_treated=data1.sewage_sludge_treated,
            pesticide=data1.pesticide,
            aflatoxin=data1.aflatoxin,
            preservative=data1.preservative,
            antibiotic=data1.antibiotic,
            gras=data1.gras,
            prop65_complaint=data1.prop65_complaint,
            created_at=data1.created_at  # Ensure this column exists in the model
        )

        # Execute the queries
        await db.execute(query)
        await db.execute(query1)

        # Commit the transaction
        await db.commit()
        return {"message": "Raw Material data inserted successfully!"}

    except SQLAlchemyError as e:
        # Rollback in case of failure
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Route to retrieve data
@mainRouter.get("/fetch_product", dependencies=[Depends(partial(check_permission, required_role="admin"))])
async def read_product_data(
        db: AsyncSession = Depends(get_db)
):
    try:
        # Select all records from the product table
        query = select(product)
        result = await db.execute(query)
        # Fetch all the rows from the result
        data = result.fetchall()
        # Convert each row to a dictionary using row._mapping for correct field access
        return {"data": [dict(row._mapping) for row in data]}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()


@mainRouter.get("/fetch_items/{product_id}")
async def read_items_data(
        product_id: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        # query = select(items).where(items.c.product_id == product_id)
        query = select(
            product.c.product_name,
            product.c.identified_uses,
            product.c.mixtures,
            product.c.appearance,
            product.c.color,
            product.c.symbol_id,
            items
        ).join(
            product,
            product.c.product_id == items.c.product_id,
            isouter=True  # LEFT JOIN
        ).where(
            items.c.product_id == product_id
        )

        result = await db.execute(query)
        data = result.fetchall()
        return {"data": [dict(row._mapping) for row in data]}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to retrieve data
@mainRouter.get("/fetch_ingredient")
async def read_all_ingredient_data(db: AsyncSession = Depends(get_db)):
    try:
        query = select(ingredient, declaration).join(
            declaration,
            and_(
            declaration.c.ing_item_code == ingredient.c.ing_item_code,
            declaration.c.rm_code == ingredient.c.rm_code),
            isouter=True  # LEFT JOIN
        ).distinct()
        result = await db.execute(query)
        data = result.fetchall()
        return {"data": [dict(row._mapping) for row in data]}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@mainRouter.get("/fetch_ingredient/{ing_item_code}")  # row fetch by ingredient item code from ingredient table
async def read_ingredient_data(
        ing_item_code: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        query = select(ingredient).where(ingredient.c.ing_item_code == ing_item_code)
        result = await db.execute(query)
        data = result.fetchall()

        if not data:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        return {"data": [dict(row._mapping) for row in data]}

    except NoResultFound:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@mainRouter.get("/fetch_declaration")
async def fetch_declaration_data(
        ing_item_code: str,
        rm_code: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        query = select(declaration).where(
            (declaration.c.ing_item_code == ing_item_code) &
            (declaration.c.rm_code == rm_code)
        )  # No need for a list; select already expects a Table
        result = await db.execute(query)
        data = result.fetchall()
        return {"data": [dict(row._mapping) for row in data]}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


# @mainRouter.delete("/product/{product_id}")
# async def delete_product(product_id: str, db: AsyncSession = Depends(get_db)):
#     try:
#         # Query to delete a product by item_code
#         query = product.delete().where(product.c.product_id == product_id)
#         result = await db.execute(query)

#         # If no rows were deleted, the item_code doesn't exist
#         if result.rowcount == 0:
#             raise HTTPException(status_code = 404, detail = f"Product {product_id} not found")

#         await db.commit()
#         return {"message": f"Product {product_id} deleted successfully!"}
#     except SQLAlchemyError as e:
#         await db.rollback()
#         raise HTTPException(status_code = 500, detail = str(e))

@mainRouter.patch("/item/{product_id}")
async def update_item(
        product_id: str, data: Items, data1: Product,db: AsyncSession = Depends(get_db)
):
    try:
        # Updating Product Table
        product_update_query = (
            product.update()
            .where(product.c.product_id == product_id)
            .values(
                product_id=data1.product_id,
                product_name=data1.product_name,
                symbol_id=data1.symbol_id,
                identified_uses=data1.identified_uses,
                mixtures=data1.mixtures,
                appearance=data1.appearance,
                color=data1.color,
                updated_at=data1.updated_at
            ))
        result = await db.execute(product_update_query)

        # If the product does not exist, return an error
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        # Updating the list of ingredients
        for ingredient in data.ingredients:
            ingredient_update_query = (
                items.update()
                .where(
                    (items.c.product_id == product_id) &
                    (items.c.ing_item_code == ingredient.ing_item_code)
                )
                .values(
                    product_id=data1.product_id,
                    ing_item_code=ingredient.ing_item_code,
                    seq_no=ingredient.seq_no,
                    ing_name=ingredient.ing_name,
                    per_composition=ingredient.per_composition,
                    other_ing=ingredient.other_ing,
                    alpha_composition=ingredient.alpha_composition,
                    updated_at=data.updated_at
                )
            )
            result = await db.execute(ingredient_update_query)

            # If the ingredient does not exist, return an error or optionally create it
            if result.rowcount == 0:
                raise HTTPException(status_code=404,
                                    detail=f"Ingredient {ingredient.ing_item_code} not found for product {product_id}")

        # Commit the transaction
        await db.commit()
        return {"message": f"Product with product id : {product_id} updated successfully!"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# @mainRouter.patch("/ingredient/{ing_item_code}")  # update ingredient table by ingredient item code and rm code
# async def update_ingredient(ing_item_code: str, rm_code: List[str], data: Ingredient, db: AsyncSession = Depends(get_db)):
#     try:
#         # Query to update an ingredient by ingredient_item_code and rm_code
#         query = (
#             ingredient.update()
#             .where(
#                 (ingredient.c.ing_item_code == ing_item_code) &
#                 (ingredient.c.rm_code == rm_code)
#             )
#             .values(
#                 cas_num=data.cas_num,
#                 ec_num=data.ec_num,
#                 ing_type=data.ing_type,
#                 source_type=data.source_type,
#                 source=data.source,
#                 country_origin=data.country_origin,
#                 updated_at=data.updated_at
#             )
#         )
#         result = await db.execute(query)

#         # If no rows were updated, the combination of ing_item_code and rm_code doesn't exist
#         if result.rowcount == 0:
#             raise HTTPException(status_code=404, detail=f"Ingredient {ing_item_code} with RM code {rm_code} not found")

#         await db.commit()
#         return {"message": f"Ingredient {ing_item_code} updated successfully!"}
#     except SQLAlchemyError as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


# @mainRouter.patch("/ingredient/{ing_item_code}")  # update ingredient table by ingredient item code and rm code
# async def update_ingredient(
#         ing_item_code: str,
#         rm_codes: List[str] = Query([], description="List of RM codes"),
#         data: IngredientUpdate = Depends(),
#         db: AsyncSession = Depends(get_db)
# ):
#     try:
#         if not rm_codes:
#             raise HTTPException(status_code=400, detail="RM codes are required.")
#
#         # Prepara only the data that is provided in the request
#         update_ing_data = {
#             key: value for key, value in data.dict(exclude_unset=True).items()
#             if value is not None
#         }
#
#         if not update_ing_data:
#             raise HTTPException(status_code=400, detail="No valid update data provided.")
#
#         # Ensure `ing_item_code` and `rm_code` are NOT being updated
#         if "ing_item_code" in update_ing_data or "rm_code" in update_ing_data:
#             raise HTTPException(status_code=400,
#                                 detail="(Duplicate Data, data exist) Cannot update primary key fields (ing_item_code, rm_code).")
#
#         # Query to update an ingredient by ingredient_item_code and rm_code
#         query = (
#             ingredient.update()
#             .where(
#                 (ingredient.c.ing_item_code == ing_item_code) &
#                 ingredient.c.rm_code.in_(rm_codes)
#             )
#             .values(**update_ing_data)
#         )
#
#         result = await db.execute(query)
#         await db.commit()
#
#         # If no rows were updated, the combination of ing_item_code and rm_code doesn't exist
#         if result.rowcount == 0:
#             raise HTTPException(status_code=404, detail=f"Ingredient {ing_item_code} with RM code {rm_codes} not found")
#
#         return {"message": f"Ingredient {ing_item_code} and declaration updated successfully!"}
#     except SQLAlchemyError as e:
#         await db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))

@mainRouter.patch("/ingredient/{ing_item_code}")
async def update_ingredient(
        ing_item_code: str,
        update_request: IngredientUpdate,
        db: AsyncSession = Depends(get_db)
):
    try:
        # Apply Global Updates (All rows where ing_item_code matches)
        if update_request.global_updates:
            global_update_data = update_request.global_updates.dict(exclude_unset=True)
            if global_update_data:
                query = (
                    ingredient.update()
                    .where(ingredient.c.ing_item_code == ing_item_code)
                    .values(**global_update_data)
                )
                await db.execute(query)

        # Apply Row-Specific Updates
        if update_request.row_updates:
            for row in update_request.row_updates:
                row_update_data = row.dict(exclude_unset=True)
                rm_code = row_update_data.pop("rm_code")  # Extract rm_code for condition

                query = (
                    ingredient.update()
                    .where(
                        (ingredient.c.ing_item_code == ing_item_code) &
                        (ingredient.c.rm_code == rm_code)
                    )
                    .values(**row_update_data)
                )
                await db.execute(query)

        await db.commit()
        return {"message": "Ingredient and vendor details updated successfully!"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@mainRouter.patch("/declaration/{ing_item_code}")
async def update_declaration(
        ing_item_code: str,
        rm_code: str,
        data1: Declaration,
        db: AsyncSession = Depends(get_db)
):
    try:
        query = (
            declaration.update()
            .where(
                (declaration.c.ing_item_code == ing_item_code) &
                (declaration.c.rm_code == rm_code)
            )
            .values(
                ing_item_code=data1.ing_item_code,
                rm_code=data1.rm_code,
                vegetarian=data1.vegetarian,
                vegan=data1.vegan,
                non_gmo=data1.non_gmo,
                classification=data1.classification,
                gluten_status=data1.gluten_status,
                bse_tse=data1.bse_tse,
                wheat=data1.wheat,
                eggs=data1.eggs,
                crustaceans_shell_fish=data1.crustaceans_shell_fish,
                fish=data1.fish,
                milk=data1.milk,
                tree_nuts=data1.tree_nuts,
                peanuts=data1.peanuts,
                soy=data1.soy,
                sesame_seeds=data1.sesame_seeds,
                celery=data1.celery,
                barley_oats_rye_spelt=data1.barley_oats_rye_spelt,
                orange_kiwi_peaches_apples=data1.orange_kiwi_peaches_apples,
                mushrooms=data1.mushrooms,
                mustard=data1.mustard,
                lupin=data1.lupin,
                molluscs=data1.molluscs,
                sulfur=data1.sulfur,
                residual_solvent=data1.residual_solvent,
                wada_compliance=data1.wada_compliance,
                eto_treated=data1.eto_treated,
                irradiated=data1.irradiated,
                sewage_sludge_treated=data1.sewage_sludge_treated,
                pesticide=data1.pesticide,
                aflatoxin=data1.aflatoxin,
                preservative=data1.preservative,
                antibiotic=data1.antibiotic,
                gras=data1.gras,
                prop65_complaint=data1.prop65_complaint,
                updated_at=data1.updated_at  # Ensure this column exists in the model
            )
        )
        result = await db.execute(query)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"Declaration for ingredient {ing_item_code} and rm_code {rm_code} not found.")
        return {"message": f"Declaration for ingredient {ing_item_code} updated successfully!"}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@mainRouter.delete("/ingredient/{ing_item_code}")
async def delete_ingredient(ing_item_code: str, rm_code: str, db: AsyncSession = Depends(get_db)):
    try:
        # Build delete queries for ingredient and declaration
        ingredient_query = ingredient.delete().where(
            (ingredient.c.ing_item_code == ing_item_code) &
            (ingredient.c.rm_code == rm_code)
        )
        declaration_query = declaration.delete().where(
            (declaration.c.ing_item_code == ing_item_code) &
            (declaration.c.rm_code == rm_code)
        )

        # Execute queries
        declaration_result = await db.execute(declaration_query)
        ingredient_result = await db.execute(ingredient_query)

        # Check if records were found and deleted
        if not declaration_result.rowcount and not ingredient_result.rowcount:
            raise HTTPException(
                status_code=404,
                detail=f"Neither ingredient {ing_item_code.lower()} nor its declaration for rm_code {rm_code.lower()} was found."
            )
        elif not declaration_result.rowcount:
            raise HTTPException(
                status_code=404,
                detail=f"Declaration for ingredient {ing_item_code.lower()} and rm_code {rm_code.lower} not found."
            )
        elif not ingredient_result.rowcount:
            raise HTTPException(
                status_code=404,
                detail=f"Ingredient {ing_item_code.lower()} with rm_code {rm_code} not found."
            )

        # Commit the transaction
        await db.commit()
        return {
            "message": f"Ingredient with ingredient item code :{ing_item_code} and related declaration with rm_code : {rm_code} deleted successfully!"}

    except SQLAlchemyError as e:
        # Rollback the transaction on error
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting ingredient and declaration: {str(e)}"
        )


@mainRouter.delete("/product/{product_id}")
async def delete_product(
        product_id: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        # Delete from 'product' table
        query_product = product.delete().where(product.c.product_id == product_id)
        result_product = await db.execute(query_product)

        # Check if product was found
        if result_product.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

        # Delete from 'items' table
        query_item = items.delete().where(items.c.product_id == product_id)
        await db.execute(query_item)

        # Commit the transaction after both deletions
        await db.commit()

        return {"message": f"Product with product id : {product_id} deleted successfully"}

    except SQLAlchemyError as e:
        # Rollback the transaction if any exception occurs
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@mainRouter.post("/generate_document")
async def generate_document(request: GenerateRequest):
    temp_dir = tempfile.mkdtemp()
    date_str = datetime.now().strftime('%B %d, %Y')

    # Dictionary to map template names to corresponding functions and required arguments
    template_mapping = {
        "gras": create_template_gras,
        "fda": create_template_fda,
        "edible source": create_template_edible,
        "non-irradiated": create_template_nonise,
        "non ise": create_template_nonise,
        "non sewage and non eto": create_template_nonise,
        "bse tse": create_template_bsetse,
        "composition": create_template_composition,
        "coo": create_template_coo,
        "coo2": create_template_COO2,
        "coo3": create_template_COO3,
        "cos": create_template_COS,
        "locg": create_template_customer_seb,
        "fsma": create_template_fsma,
        "gluten status": create_template_gluten,
        "heavy metal": create_template_heavymetal,
        "lot code": create_template_lotcode,
        "nutritional": create_template_nutritional,
        "percentage composition": create_template_percomposition,
        "wada": create_template_ppr,
        "packaging": create_template_ppr,
        "preservative": create_template_ppr,
        "proposition 65": create_template_heavymetal,
        "residual solvent": create_template_ppr,
        "sustainability statement": create_template_ss,
        "non gmo": create_template_nongmo,
        "vegan": create_template_vegan,
        "vegetarian": create_template_vegetarian,
        "contact information": create_template_contact,
        "allergen": create_template_allergen,
        "sds": create_sds_pdf,
        "mflow chart": create_template_mflow,
        "microorganisms": create_template_microorganisms,
    }

    # Determine the template function to call based on the template name
    template_func = template_mapping.get(request.template_name.lower())

    if not template_func:
        raise HTTPException(status_code=400, detail=f"Unknown template name: {request.template_name}")

    # Prepare arguments for the template function call
    kwargs = {
        "date": date_str,
        "temp_dir": temp_dir,
        "company": request.company_name,
        "product_id": request.product_id,
    }

    # Special handling for nonirradiated, ise, se, wada, packaging, preservative, residual_solvent templates
    if request.template_name.lower() in ["non-irradiated", "non ise", "non sewage and non eto"]:
        kwargs["temp"] = request.template_name.lower()
    if request.template_name.lower() in ["wada", "packaging", "preservative", "residual solvent"]:
        kwargs["temp"] = request.template_name.lower()
    if request.template_name.lower() in ["proposition 65", "heavy metal"]:
        kwargs["temp"] = request.template_name.lower()
    if request.template_name.lower() in ["locg"]:
        kwargs["customer_name"] = request.customer_name
    # if request.template_name.lower() in ["b_irraditated"]:
    #     kwargs['temp'] = request.template_name.lower()

    # Call the template function asynchronously
    try:
        file_path, file_name = await template_func(**kwargs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Return the generated file if it exists
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            filename=file_name,
            media_type='application/pdf',
            headers={
                "X-File-Name": file_name,  # Custom header to include file name
                "Access-Control-Expose-Headers": "X-File-Name",  # Required for CORS
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
            }
        )
    else:
        raise HTTPException(status_code=500, detail="Unable to generate the document.")


@mainRouter.get("/all-info")
async def get_all_information(db: AsyncSession = Depends(get_db)):
    try:
        # Initialize an empty dictionary to store all results
        result_dict = {}

        # Fetch classification data
        query = await db.execute(select(declaration.c.classification).distinct())
        results = query.fetchall()
        classification_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['classification'] = classification_list

        # Fetch identified uses data
        query = await db.execute(select(product.c.identified_uses).distinct())
        results = query.fetchall()
        identified_uses_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['identified_uses'] = identified_uses_list

        # Fetch Mixtures data
        query = await db.execute(
            select(product.c.mixtures).distinct()
        )
        results = query.fetchall()
        mixtures_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict["mixtures"] = mixtures_list

        # Fetch appearance data
        query = await db.execute(select(product.c.appearance).distinct())
        results = query.fetchall()
        appearance_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['appearance'] = appearance_list

        # Fetch color data
        query = await db.execute(select(product.c.color).distinct())
        results = query.fetchall()
        color_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['color'] = color_list

        # # Fetch formulation data
        # query = await db.execute(select(product.c.formulation).distinct())
        # results = query.fetchall()
        # formulation_list = [result[0] for result in sorted(results) if result[0].strip()]
        # result_dict['formulation'] = formulation_list

        # Fetch source type data
        query = await db.execute(select(ingredient.c.source_type).distinct())
        results = query.fetchall()
        source_type_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['source_type'] = source_type_list

        # Fetch source data
        query = await db.execute(select(ingredient.c.source).distinct())
        results = query.fetchall()
        source_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['source'] = source_list

        # Fetch country origin data
        query = await db.execute(select(ingredient.c.country_origin).distinct())
        results = query.fetchall()
        country_origin_list = [result[0] for result in sorted(results) if result[0].strip()]
        result_dict['country_origin'] = country_origin_list

        # Fetch symbols data
        query = await db.execute(
            select(symbols.c.symbol_id, symbols.c.symbol, symbols.c.symbol_code)
        )
        results = query.fetchall()
        symbols_list = [dict(row._mapping) for row in results]
        result_dict["symbols"] = symbols_list

        return JSONResponse(content=result_dict, status_code=200)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f" Database error: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Exception Occur at {str(e)}")


@mainRouter.get("/templates")
def templates():
    templates_list = [
        "GRAS", "FDA", "Edible Source", "Non-Irradiated", "Non ISE",
        "Non Sewage and Non ETO", "BSE TSE", "Composition", "COO", "COO2",
        "COO3", "COS", "LOCG", "FSMA", "Gluten Status", "Heavy Metal", "Lot Code", "Nutritional",
        "Percentage Composition", "WADA", "Packaging", "Preservative", "Residual Solvent", "Sustainability Statement",
        "Non GMO", "Vegan", "Vegetarian", "Contact Information", "Allergen", "Proposition 65", "SDS", "Mflow Chart",
        "Microorganisms"
    ]

    sorted_templates = sorted(templates_list)

    return {"templates": [template.upper() for template in sorted_templates]}


@mainRouter.get("/allergen")
def allergen():
    return {
        "allergen": [
            "wheat",
            "eggs",
            "crustaceans_shell_fish",
            "fish",
            "milk",
            "tree_nuts",
            "peanuts",
            "soy",
            "sesame_seeds",
            "celery",
            "barley_oats_rye_spelt",
            "orange_kiwi_peaches_apples",
            "mushrooms",
            "mustard",
            "lupin",
            "molluscs",
            "sulfur"
        ]
    }


@mainRouter.get("/ingredient")
async def read_data(db: AsyncSession = Depends(get_db)):
    try:
        # Select only the ingredient_name and item_code columns
        query = select(ingredient.c.ing_name, ingredient.c.ing_item_code).distinct()
        result = await db.execute(query)
        data = result.fetchall()
        return {"data": [dict(row._mapping) for row in data]}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
