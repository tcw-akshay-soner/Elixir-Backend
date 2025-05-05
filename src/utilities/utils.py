from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from src.engine.pharma_db import get_db
from src.model import schemas, model
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from sqlalchemy.future import select
from jose import jwt
import os
import logging
# from argon2 import PasswordHasher
from rich.logging import RichHandler
from dotenv import load_dotenv

# Configure RichHandler
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("uvicorn")

# Load environment variables from.env file
load_dotenv()
# ph = PasswordHasher()

# Load secrets from environment variables
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "secret")
# ALGORITHM = os.getenv("ALGORITHM", "HS256")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_EXPIRY_TIME", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_EXPIRY_TIME", "1"))



async def create_access_token(user : schemas.User) -> str:
    """Create a new JWT access token with the user's identity and role"""
    try:
        access_expiry = (datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
        access_payload  = {
            "role" : user.role,
            "userId" : user.id,
            # "name" : user.name,
            # "email" : user.email,
            "is_active" : user.is_active,
            # "password" : user.hashed_password, # major security risk because if the token is leaked, the hashed password is also exposed. 
            "exp" : access_expiry,
            "token_type": "access" 
        }
        access_token = jwt.encode(
            claims = access_payload ,
            key = JWT_SECRET,
            algorithm = ALGORITHM
        )
        
        return access_token, access_expiry
    except Exception as e:
        logger.error(f"Error in create_access_token: {e}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

async def create_refresh_token(user : schemas.User) -> str:
    """Generate a new refresh token for a user"""
    refresh_expire = (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    
    refresh_payload = {
        "userId": user.id,
        "exp": refresh_expire,
        "token_type": "refresh"  # Helps to differentiate token types
    }

    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=ALGORITHM)
    return refresh_token, refresh_expire

    
def verify_token(token):
    """Decode the JWT token and return the payload"""
    try:
        payload = jwt.decode(token = token, key = JWT_SECRET, algorithms = ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Token expired, Please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    
def verify_refresh_token(refresh_token, access_token):
    """Verify the refresh token and return the payload"""
    try:
        payload = jwt.decode(token = refresh_token, key = JWT_SECRET, algorithms = ALGORITHM)
        userId = payload.get("userId")
        if not userId:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        if access_token:
            access_payload = verify_token(access_token)
            if userId != access_payload.get("userId"):
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired, Please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    

# Database Functionalities
# async def get_user(db: AsyncSession, user_id: int) -> Optional[schemas.User]:
#     try:
#         result = await db.execute(select(schemas.User).filter(schemas.User.id == user_id))
#         return result.unique().scalars().first()
#     except Exception as e:
#         logger.error(f"Error in get_user: {e}")
#         raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    

async def get_user_by_email(db: AsyncSession, email: EmailStr) -> Optional[schemas.User]:
    try:
        result = await db.execute(select(schemas.User).filter(schemas.User.email == email))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error in get_user_by_email : {e}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

async def get_user_by_userId(db: AsyncSession, userId: int) -> Optional[schemas.User]:
    try:
        result = await db.execute(select(schemas.User).filter(schemas.User.id == userId))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error in get_user_by_userId : {e}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list:
    try:
        stmt = select(schemas.User).offset(skip).limit(limit)
        result = await db.execute(stmt)
        users = result.unique().scalars().all()
        return users
    except Exception as e:
        logger.error(f"Error in get_users: {e}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


async def create_user_db(db: AsyncSession, user_data: model.UserCreate) -> schemas.User:
    try:
        # fake_hashed_password = user.password + "notreallyhashed"
        # hashed_password = get_password_hash(user_data.password)
        new_user = schemas.User(
            name = user_data.name,
            email = user_data.email, 
            password = user_data.password, 
            role = user_data.role, 
            is_active = user_data.is_active
        )
        # token = create_access_token(db_user)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        logger.error(f"Error in create_user_db: {e}")
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

# Simple password check
async def check_password(plain_password : str, stored_password: str) -> bool:
    return plain_password == stored_password

### User Authentication ###
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[schemas.User]:
    """Retrieve the current user from session cookies."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_token(token)
    
    # DEBUGGING: Print the decoded payload
    print("Decoded Token Payload:", payload)
    
    userId = payload.get("userId")
    if not userId:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    user = await get_user_by_userId(db, userId = userId)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

async def check_active(user: schemas.User = Depends(get_current_user)) -> schemas.User:
    """Check if a user is active."""
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user

# async def check_permission(required_role: str, user: schemas.User = Depends(get_current_user)) -> schemas.User:
async def check_permission(
    user: schemas.User = Depends(get_current_user),
    required_role: str = "user"
) -> schemas.User:
    """Ensure user has the required role dynamically."""
    if user.role != required_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return user
