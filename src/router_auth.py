from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
# from fastapi.security import OAuth2PasswordBearer
from functools import partial
from fastapi.responses import JSONResponse
# import jwt
from jose import JWTError
from jwt import ExpiredSignatureError
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.engine.pharma_db import get_db
# from fastapi.security import OAuth2PasswordRequestForm
from src.utilities.utils import(
    check_permission,
    create_refresh_token,
    get_user_by_email,
    # check_password,
    create_access_token,
    create_user_db,
    verify_refresh_token,
    # JWT_SECRET,
    # ALGORITHM,
    verify_token,
    # get_current_user
)
from src.model import model, schemas
from rich.logging import RichHandler
import warnings
import logging

# Configure RichHandler
logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
warnings.filterwarnings('ignore')
auth_router = APIRouter()

def get_router() -> APIRouter:
    return auth_router

# Login route
@auth_router.post("/login")
async def login(request: model.LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await get_user_by_email(db, email = request.email) 
        
        # Check if user exists and password is correct
        if not user or user.password != request.password:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Create access and refresh tokens
        access_token, _ = await create_access_token(user)
        refresh_token, _ = await create_refresh_token(user)
        
        response = JSONResponse(
            content = {
                "message" : "Login successful", 
                "role" : user.role.value,
                "email" : user.email, 
                "name" : user.name,
                "is_active" : user.is_active
                # "expiry_time": expiry_time  # In seconds since Unix epoch (1970-01-01)
            }
        )
        response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",
        max_age=60*60  # 60 minutes
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True, 
            samesite="None", # Important for cross-origin requests
            max_age=60*60*24  # 1 days
            
        )
        return response
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR , detail=f"Error logging in: {str(e)}")

@auth_router.get("/session")
async def check_session(request: Request, db: AsyncSession = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Session expired"}
        )
        response.delete_cookie("access_token")
        return response

    try:
        payload = verify_token(access_token)
    except ExpiredSignatureError:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Session expired"}
        )
        response.delete_cookie("access_token")
        return response
    except JWTError:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"}
        )
        response.delete_cookie("access_token")
        return response

    email = payload.get("email")

    stmt = select(schemas.User).where(schemas.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        response = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "User not found"}
        )
        response.delete_cookie("access_token")
        return response

    return {
        "message": "User authenticated",
        "user": {"email": user.email, "role": user.role.value, "name": user.name, "is_active": user.is_active}
    }

# Admin Dashboard (Restricted to Admins Only)
@auth_router.get(
    "/dashboard", 
    response_model = model.AdminDashboardResponse, 
    dependencies=[Depends(partial(check_permission, required_role="admin"))]
)
async def admin_panel(db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(schemas.User)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return {"message": "Welcome to the Admin Dashboard!", "Users": users}

    except Exception as e:
        logger.error(f"Error fetching all users: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching all users: {str(e)}")


# Create User (Restricted to Admins)
@auth_router.post("/create", response_model=model.UserResponse, dependencies=[Depends(partial(check_permission, required_role="admin"))])
async def create_user(user: model.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if user already exists by email
        existing_user  = await get_user_by_email(db, email = user.email)
        if existing_user :
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"User with email '{user.email}' already registered")
        
        # Create a new user
        new_user = await create_user_db(db, user)
        access_token, _ = await create_access_token(new_user)
        
        # Create and save the new user
        return {
            "email": new_user.email, 
            "name": new_user.name, 
            "is_active": new_user.is_active, 
            "role": new_user.role, 
            "token": access_token
        }
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating user: {str(e)}")

@auth_router.post("/refresh")
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")
    
    if not refresh_token and not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tokens not found")

    # Extract access token payload and expiry time
    access_payload = verify_token(access_token)
    access_expiry = access_payload.get("exp")
    access_user = access_payload.get("role")
    
    # Fetch user details from db
    user = await get_user_by_email(db, email=access_payload.get("email"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Check if access token expires in the next 5 minutes, 
    current_time = datetime.now(timezone.utc).timestamp()
    remaining_time = access_expiry - current_time
    
    if remaining_time >= 5 * 60 and access_user == user.role:
        return JSONResponse(content={"message": "Access token is still valid", "expires_in": remaining_time})
    elif access_user != user.role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Role Mismatch/Changed")

    # if access_expiry > current_time > 5 * 60:
    #     return JSONResponse(content={"message": "Access token is stil valid"})
    
    # Verify refresh token and get user details
    refresh_payload = verify_refresh_token(refresh_token, access_token)
    refresh_expiry = refresh_payload.get("exp")
    email = refresh_payload.get("email")
    
    if refresh_expiry < current_time:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    stmt = select(schemas.User).where(schemas.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Generate new tokens
    new_access_token, new_access_expiry = await create_access_token(user)
    
    response_data = {
        "message": "Access Token refreshed",
        "access_token_expires_in": int(new_access_expiry - current_time)
    }

    response = JSONResponse(content=response_data)
    response.set_cookie("access_token", new_access_token, httponly=True, secure=True, samesite="None", max_age=60 * 60)

    # Generate new refresh token only if it's about to expire (within 5 minutes)
    refresh_lifespan = 60 * 60 * 24  # Assuming 24 hours (modify as per your config)
    if refresh_expiry - current_time <= 5 * 60:  # If refresh token has ≤5 minutes left
        new_refresh_token, new_refresh_expiry = await create_refresh_token(user)
        response.set_cookie("refresh_token", new_refresh_token, httponly=True, secure=True, samesite="None", max_age=refresh_lifespan)
        response_data["refresh_token_expires_in"] = int(new_refresh_expiry - current_time)

    return response


# Fetch all user from db
# @auth_router.get("/user/all", response_model = list[model.UserBase], dependencies=[Depends(partial(check_permission, required_role="admin"))])
# async def get_all_users(db: AsyncSession = Depends(get_db)):
#     try:
#         stmt = select(schemas.User)
#         result = await db.execute(stmt)
#         users = result.scalars().all()
#         return users
#     except Exception as e:
#         logger.error(f"Error fetching all users: {str(e)}")
#         raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching all users: {str(e)}")


# Update User details by email id
@auth_router.patch("/{email}", dependencies=[Depends(partial(check_permission, required_role="admin"))])
async def update_user_profile(
    user_data: model.UserUpdate, email: EmailStr, db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch user by email
        stmt = select(schemas.User).where(schemas.User.email == email)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email '{email}' not found"
            )

        # Update user details dynamically
        update_data = user_data.model_dump(exclude_unset=True)  # Only update non-null fields
        for key, value in update_data.items():
            setattr(user, key, value)

        # Commit changes
        await db.commit()
        await db.refresh(user)

        return user  # Returns the updated user with the correct response model

    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )

# Logout route
@auth_router.post("/logout")
async def logout(request: Request):
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie("access_token", httponly=True, secure=True, samesite="None")
    response.delete_cookie("refresh_token", httponly=True, secure=True, samesite="None")
    return response