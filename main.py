from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import models
from database import Base, engine
from routers import emprestimos, leitores, livros

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="appeu - Biblioteca",
    description="API de gestão de biblioteca (livros, leitores e empréstimos).",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def tratar_erros_de_validacao(request: Request, exc: RequestValidationError):
    erros = []
    for erro in exc.errors():
        campo = str(erro["loc"][-1])
        if erro["type"] == "missing":
            mensagem = f"O campo {campo} é obrigatório."
        else:
            mensagem = erro["msg"].replace("Value error, ", "")
        erros.append({"campo": campo, "mensagem": mensagem})
    return JSONResponse(status_code=422, content={"erros": erros})


app.include_router(livros.router)
app.include_router(leitores.router)
app.include_router(emprestimos.router)


@app.get("/")
def raiz():
    return {"status": "online", "mensagem": "Biblioteca Funcionando"}