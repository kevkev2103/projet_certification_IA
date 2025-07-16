from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..database import get_db
from ..models import Film, Personne, Participation, Prediction
from .auth import get_current_user 


router = APIRouter()

# route pour récupérer tous les films
@router.get("/films/", response_model=list[Film], status_code=status.HTTP_200_OK)
def get_films(db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    print("*"*50)
    print("get_films")
    print("*"*50)
    films = db.exec(select(Film)).all()
    print("*"*50)
    print(films)
    print("*"*50)   
    if not films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucun film trouvé dans la BDD")
    return films

# route pour ajouter un film
@router.post("/films/", response_model=Film, status_code=status.HTTP_201_CREATED)
def create_film(film: Film, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    # Vérifier si un film avec le même titre existe déjà
    existing_film = db.exec(select(Film).where(Film.titre == film.titre)).first()
    if existing_film:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un film avec ce titre existe déjà")

    db.add(film)
    db.commit()
    db.refresh(film)  # Recharge l'objet après l'insertion
    return film

# route pour supprimer un film
@router.delete("/films/{id_film}", status_code=status.HTTP_200_OK)
def delete_film(id_film: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    film = db.get(Film, id_film)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film non trouvé")

    db.delete(film)
    db.commit()
    return {"message": f"Le film avec l'ID {id_film} a été supprimé"}

# route pour mettre à jour un film
@router.put("/films/{id_film}", response_model=Film, status_code=status.HTTP_200_OK)
def update_film(id_film: int, updated_film: Film, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    film = db.get(Film, id_film)
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Film non trouvé")

    # Met à jour uniquement les champs envoyés dans la requête
    film_data = updated_film.dict(exclude_unset=True)  # Exclure les champs non envoyés
    for key, value in film_data.items():
        setattr(film, key, value)

    db.commit()
    db.refresh(film)
    return film

@router.get("/films/{id_film}/acteurs/", status_code=status.HTTP_200_OK)
def get_acteurs_by_film(id_film: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Personne).join(Participation).where(
        Participation.id_film == id_film,
        Participation.role == "acteur"
    )
    acteurs = db.exec(query).all()
    return acteurs

@router.get("/films/{id_film}/realisateurs/", status_code=status.HTTP_200_OK)
def get_realisateurs_by_film(id_film: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Personne).join(Participation).where(
        Participation.id_film == id_film,
        Participation.role == "realisateur"
    )
    realisateurs = db.exec(query).all()
    return realisateurs

# route pour récupérer toutes les prédictions
@router.get("/predictions/", response_model=list[Prediction], status_code=status.HTTP_200_OK)
def get_predictions(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    predictions = db.exec(select(Prediction)).all()
    return predictions

# route pour récupérer les prédictions d'un film spécifique
@router.get("/films/{id_film}/predictions/", response_model=list[Prediction], status_code=status.HTTP_200_OK)
def get_predictions_by_film(id_film: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    query = select(Prediction).where(Prediction.id_film == id_film)
    predictions = db.exec(query).all()
    return predictions
