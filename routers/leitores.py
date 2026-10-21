from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/leitores", tags=["Leitores"])


@router.post("/", response_model=schemas.LeitorResponseSchema, status_code=201)
def cadastrar_leitor(leitor: schemas.LeitorCreateSchema, db: Session = Depends(get_db)):
    ja_existe = db.query(models.Leitor).filter(models.Leitor.email == leitor.email).first()
    if ja_existe:
        raise HTTPException(
            status_code=409,
            detail="Já existe um leitor cadastrado com esse e-mail.",
        )
    novo_leitor = models.Leitor(**leitor.model_dump())
    db.add(novo_leitor)
    db.commit()
    db.refresh(novo_leitor)
    return novo_leitor


@router.get("/", response_model=list[schemas.LeitorResponseSchema])
def listar_leitores(db: Session = Depends(get_db)):
    return db.query(models.Leitor).all()