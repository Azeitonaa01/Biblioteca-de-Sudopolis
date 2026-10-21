from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/livros", tags=["Livros"])


@router.post("/", response_model=schemas.LivroResponseSchema, status_code=201)
def cadastrar_livro(livro: schemas.LivroCreateSchema, db: Session = Depends(get_db)):
    novo_livro = models.Livro(**livro.model_dump())
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    return novo_livro


@router.get("/", response_model=list[schemas.LivroResponseSchema])
def listar_livros(autor: str | None = None, db: Session = Depends(get_db)):
    consulta = db.query(models.Livro)
    if autor:
        consulta = consulta.filter(models.Livro.autor.ilike(f"%{autor}%"))
    return consulta.all()

@router.put("/{livro_id}", response_model=schemas.LivroResponseSchema)
def atualizar_livro(livro_id: int, dados: schemas.LivroCreateSchema, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    for campo, valor in dados.model_dump().items():
        setattr(livro, campo, valor)
    db.commit()
    db.refresh(livro)
    return livro

@router.delete("/{livro_id}")
def remover_livro(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    db.delete(livro)
    db.commit()
    return {"mensagem": f"Livro {livro_id} removido com sucesso"}



@router.get("/{livro_id}", response_model=schemas.LivroResponseSchema)
def buscar_livro_por_id(livro_id: int, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return livro