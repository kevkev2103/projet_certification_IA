"""
Services pour la gestion des utilisateurs et de l'authentification
"""

from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import Optional
from .models import User
from .security import verify_password, get_password_hash


class UserService:
    """Service pour la gestion des utilisateurs"""
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Récupère un utilisateur par son nom d'utilisateur"""
        return db.exec(select(User).where(User.username == username)).first()
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur avec son nom d'utilisateur et mot de passe"""
        user = UserService.get_user_by_username(db, username)
        if not user or not verify_password(password, user.password):
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, username: str, password: str) -> User:
        """Crée un nouvel utilisateur"""
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = UserService.get_user_by_username(db, username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec ce nom d'utilisateur existe déjà"
            )
        
        # Valider le mot de passe
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le mot de passe doit contenir au moins 6 caractères"
            )
        
        # Créer le hash du mot de passe
        hashed_password = get_password_hash(password)
        
        # Créer le nouvel utilisateur
        new_user = User(
            username=username,
            password=hashed_password
        )
        
        try:
            # Ajouter l'utilisateur à la base de données
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
            )
    
    @staticmethod
    def get_all_users(db: Session) -> list[User]:
        """Récupère tous les utilisateurs (pour l'administration)"""
        return db.exec(select(User)).all()
    
    @staticmethod
    def delete_user(db: Session, username: str) -> bool:
        """Supprime un utilisateur"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        try:
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la suppression de l'utilisateur: {str(e)}"
            ) 