### This file handles any scrambling of passwords, etc. ###
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import db_helper
import os 
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
# forces users to login every 1440 minutes for security
ACCESS_TOKEN_EXPIRE_MINS = 1440

# we are using 'bcrypt' as our password scrambling method
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

def get_password_hash(password: str) -> str:
    # converts a plain password to hash
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # hash password when user enters it, and check again
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    # Creates the JWT token after a successful login
    # Packages the user's email inside the token along with expiration time
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINS)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    This function runs BEFORE the API endpoints.
    1. It grabs the token string from the incoming HTTP request.
    2. It checks if the token is forged or expired.
    3. If valid, it looks up the user in PostgreSQL and hands their info to your endpoint.
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db_helper.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user
