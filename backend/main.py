from datetime import timedelta
from typing import Annotated, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

import crud, models, schemas, auth
from database import SessionLocal, engine

# Create database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
# Allow requests from frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
# Ensures each request gets a fresh DB session and it's closed after request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 scheme for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user from the JWT token.
    1. Decodes the token.
    2. Validates the username.
    3. Fetches user from DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode JWT token
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Check if username exists in token data
    if token_data.username is None:
        raise credentials_exception
        
    # Retrieve user from database
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    Checks if username or email already exists.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = crud.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Endpoint to login and get an access token.
    Verifies username and password.
    Returns JWT token.
    """
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    """
    Endpoint to get current user information.
    Requires authentication (valid JWT token).
    """
    return current_user

@app.post("/databases/", response_model=schemas.Database)
def create_database(
    database: schemas.DatabaseCreate,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Create a new database for the current user.
    """
    return crud.create_database(db=db, database=database, user_id=current_user.id)

@app.get("/databases/", response_model=List[schemas.Database])
def read_databases(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all databases for the current user.
    """
    databases = crud.get_databases(db, user_id=current_user.id, skip=skip, limit=limit)
    return databases

@app.get("/databases/{database_id}", response_model=schemas.Database)
def read_database(
    database_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Get a specific database by ID.
    """
    db_database = crud.get_database(db, database_id=database_id, user_id=current_user.id)
    if db_database is None:
        raise HTTPException(status_code=404, detail="Database not found")
    return db_database

@app.put("/databases/{database_id}", response_model=schemas.Database)
def update_database(
    database_id: int,
    database: schemas.DatabaseCreate,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Update a database (save changes).
    """
    db_database = crud.update_database(db, database_id=database_id, database=database, user_id=current_user.id)
    if db_database is None:
        raise HTTPException(status_code=404, detail="Database not found")
    return db_database

@app.delete("/databases/{database_id}", response_model=bool)
def delete_database(
    database_id: int,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Delete a database.
    """
    success = crud.delete_database(db, database_id=database_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Database not found")
    return True


@app.post("/api/query")
def read_api_query():
    """
    Simple example endpoint.
    """
    return {"Hello": "World"}
