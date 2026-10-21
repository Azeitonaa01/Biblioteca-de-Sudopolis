from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/emprestimos", tags=["Empréstimos"])


def montar_resposta(emp: models.Emprestimo) -> schemas.EmprestimoResponseSchema:
    hoje = date.today()
    fim = emp.data_devolucao or hoje
    dias_com_o_livro = (fim - emp.data_emprestimo).days
    diferenca = (fim - emp.data_prevista_devolucao).days
    dias_atraso = max(diferenca, 0)
    dias_restantes = max(-diferenca, 0)

    if emp.data_devolucao:
        status = "devolvido_com_atraso" if dias_atraso > 0 else "devolvido_no_prazo"
        dias_restantes = 0
    elif dias_atraso > 0:
        status = "atrasado"
    else:
        status = "no_prazo"

    return schemas.EmprestimoResponseSchema(
        id=emp.id,
        livro_id=emp.livro_id,
        titulo_livro=emp.livro.titulo,
        leitor_id=emp.leitor_id,
        nome_leitor=emp.leitor.nome,
        data_emprestimo=emp.data_emprestimo,
        data_prevista_devolucao=emp.data_prevista_devolucao,
        data_devolucao=emp.data_devolucao,
        dias_com_o_livro=dias_com_o_livro,
        status=status,
        dias_atraso=dias_atraso,
        dias_restantes=dias_restantes,
        multa=round(dias_atraso * schemas.MULTA_POR_DIA, 2),
    )


@router.post("/", response_model=schemas.EmprestimoResponseSchema, status_code=201)
def emprestar_livro(dados: schemas.EmprestimoCreateSchema, db: Session = Depends(get_db)):
    livro = db.query(models.Livro).filter(models.Livro.id == dados.livro_id).first()
    if not livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    leitor = db.query(models.Leitor).filter(models.Leitor.id == dados.leitor_id).first()
    if not leitor:
        raise HTTPException(status_code=404, detail="Leitor não encontrado.")
    if not livro.disponivel:
        raise HTTPException(status_code=409, detail="Este livro já está emprestado.")

    inicio = dados.data_emprestimo or date.today()
    emprestimo = models.Emprestimo(
        livro_id=dados.livro_id,
        leitor_id=dados.leitor_id,
        data_emprestimo=inicio,
        data_prevista_devolucao=inicio + timedelta(days=dados.prazo_dias),
    )
    livro.disponivel = False
    db.add(emprestimo)
    db.commit()
    db.refresh(emprestimo)
    return montar_resposta(emprestimo)


@router.get("/", response_model=list[schemas.EmprestimoResponseSchema])
def listar_emprestimos(status: str | None = None, db: Session = Depends(get_db)):
    respostas = [montar_resposta(e) for e in db.query(models.Emprestimo).all()]
    if status:
        respostas = [r for r in respostas if r.status == status]
    return respostas


@router.get("/atrasados", response_model=list[schemas.EmprestimoResponseSchema])
def listar_atrasados(db: Session = Depends(get_db)):
    respostas = [montar_resposta(e) for e in db.query(models.Emprestimo).all()]
    return [r for r in respostas if r.status == "atrasado"]


@router.get("/leitor/{leitor_id}", response_model=list[schemas.EmprestimoResponseSchema])
def livros_com_o_leitor(leitor_id: int, db: Session = Depends(get_db)):
    leitor = db.query(models.Leitor).filter(models.Leitor.id == leitor_id).first()
    if not leitor:
        raise HTTPException(status_code=404, detail="Leitor não encontrado.")
    abertos = (
        db.query(models.Emprestimo)
        .filter(models.Emprestimo.leitor_id == leitor_id, models.Emprestimo.data_devolucao.is_(None))
        .all()
    )
    return [montar_resposta(e) for e in abertos]


@router.get("/livro/{livro_id}", response_model=schemas.EmprestimoResponseSchema)
def quem_esta_com_o_livro(livro_id: int, db: Session = Depends(get_db)):
    emprestimo = (
        db.query(models.Emprestimo)
        .filter(models.Emprestimo.livro_id == livro_id, models.Emprestimo.data_devolucao.is_(None))
        .first()
    )
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Este livro não está emprestado no momento.")
    return montar_resposta(emprestimo)


@router.patch("/{emprestimo_id}/devolver", response_model=schemas.EmprestimoResponseSchema)
def devolver_livro(emprestimo_id: int, db: Session = Depends(get_db)):
    emprestimo = db.query(models.Emprestimo).filter(models.Emprestimo.id == emprestimo_id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    if emprestimo.data_devolucao:
        raise HTTPException(status_code=409, detail="Este livro já foi devolvido.")

    emprestimo.data_devolucao = date.today()
    emprestimo.livro.disponivel = True
    db.commit()
    db.refresh(emprestimo)
    return montar_resposta(emprestimo)