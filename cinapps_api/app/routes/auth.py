from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional
from pydantic import BaseModel
from ..security import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from ..database import get_db
from ..models import User
from ..services import UserService

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Modèle Pydantic pour l'inscription
class UserCreate(BaseModel):
    username: str
    password: str

# Modèle Pydantic pour la réponse d'inscription
class UserResponse(BaseModel):
    username: str
    message: str

def get_user(db: Session, username: str):
    """Récupère un utilisateur de la base de données `main_user`"""
    return UserService.get_user_by_username(db, username)

def authenticate_user(db: Session, username: str, password: str):
    """Vérifie les identifiants de l'utilisateur"""
    return UserService.authenticate_user(db, username, password)

@router.post("/auth/token", summary="Obtenir un token d'accès")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authentifie un utilisateur et retourne un token JWT"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Récupère l'utilisateur actuel à partir du token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = get_user(db, username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/auth/users/me", summary="Obtenir l'utilisateur actuel")
def read_users_me(current_user: User = Depends(get_current_user)):
    """Retourne l'utilisateur actuellement authentifié"""
    return {"username": current_user.username}

@router.post("/auth/register", response_model=UserResponse, summary="Inscription d'un nouvel utilisateur")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Inscrit un nouvel utilisateur dans la base de données"""
    
    # Utiliser le service pour créer l'utilisateur
    new_user = UserService.create_user(db, user_data.username, user_data.password)
    
    return UserResponse(
        username=new_user.username,
        message="Utilisateur créé avec succès"
    )

@router.get("/auth/users", summary="Lister tous les utilisateurs")
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Liste tous les utilisateurs (nécessite une authentification)"""
    users = UserService.get_all_users(db)
    return [{"username": user.username, "id": user.id} for user in users]

@router.delete("/auth/users/{username}", summary="Supprimer un utilisateur")
def delete_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Supprime un utilisateur (nécessite une authentification)"""
    UserService.delete_user(db, username)
    return {"message": f"Utilisateur {username} supprimé avec succès"}
