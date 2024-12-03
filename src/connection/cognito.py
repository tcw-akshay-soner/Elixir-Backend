import os 
from dotenv import load_dotenv
from typing import Dict
import logging
import requests
import boto3
from jose import JWTError, jwt
from fastapi import Request, HTTPException, status
load_dotenv()


# AWS Cognito configuration (set these as environment variables)
COGNITO_REGION = os.getenv("COGNITO_REGION")
COGNITO_USERPOOL_ID = os.getenv("COGNITO_USERPOOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USERPOOL_ID}"
COGNITO_KEYS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

logging.info(f" COGNITO ISSUER : {COGNITO_ISSUER}")

# Fetching AWS Cognito keys from the JWKS endpoint
response = requests.get(COGNITO_KEYS_URL)

# Initialize the cognito_keys dictionary
cognito_keys = {}

# Check if the request was successful
if response.status_code == 200:
    # Parse the response as JSON
    response_json = response.json()
    # Update cognito_keys with the 'kid' from the response
    cognito_keys.update({key['kid']: key for key in response_json['keys']})
    logging.info(f" Cognito Key : {cognito_keys}")
else:
    raise HTTPException(status_code=500, detail="Failed to fetch Cognito keys")


# Function to validate the JWT token from AWS Cognito
def validate_jwt_token(token: str) -> Dict:
    try:
        logging.info(" Decoding JWT header...")
        header = jwt.get_unverified_header(token)
        logging.info(f" JWT Header : {header}")
        key = cognito_keys.get(header.get("kid"))
        if not key:
            logging.error(f" Key not found for the given 'kid' : {key}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # Decode the token
        decoded_token = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=COGNITO_CLIENT_ID,
            issuer=COGNITO_ISSUER
        )
        logging.info(f" Decoded JWT : {decoded_token}")
        return decoded_token
    except JWTError as e:
        logging.error(f" JWT Error : {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


# Dependency to secure endpoints
def get_current_user(request: Request) -> Dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logging.error(f" Invalid Authorization header : {auth_header}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")
    token = auth_header.split(" ")[1]
    logging.info(f" Token : {token}")
    return validate_jwt_token(token)
