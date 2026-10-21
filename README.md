# appeu - API de Biblioteca

## Descrição

API REST para gestão de uma biblioteca, desenvolvida com **FastAPI**, **Pydantic** e **SQLAlchemy**, com persistência de dados em **SQLite**. O sistema permite cadastrar, listar, atualizar e remover livros.

## Estrutura do projeto

```
appeu_livraria/
├── database.py          # Conexão com o SQLite (engine, SessionLocal, Base, get_db)
├── models.py            # Modelo SQLAlchemy da tabela livros
├── schemas.py           # Schemas Pydantic de entrada e resposta
├── routers/
│   └── livros.py        # APIRouter com o CRUD de livros
├── main.py              # Ponto de entrada: FastAPI, create_all e include_router
├── requirements.txt     # Dependências
└── .gitignore
```

## Tabela `livros`

| Campo          | Tipo    | Restrições               |
|----------------|---------|--------------------------|
| id             | inteiro | chave primária, índice   |
| titulo         | texto   | obrigatório, índice      |
| autor          | texto   | obrigatório              |
| ano_publicacao | inteiro | obrigatório              |
| preco          | decimal | obrigatório              |
| disponivel     | boolean | obrigatório (padrão true) |

## Contrato das Rotas HTTP

| Método | Rota                | Descrição                                   | Sucesso     | Erro          |
|--------|---------------------|---------------------------------------------|-------------|---------------|
| GET    | `/`                 | Status da API                               | 200 OK      | -             |
| POST   | `/livros/`          | Cadastra um novo livro                      | 201 Created | 422           |
| GET    | `/livros/`          | Lista livros (filtro opcional `?autor=`)    | 200 OK      | -             |
| PUT    | `/livros/{id}`      | Atualiza todos os campos de um livro        | 200 OK      | 404 Not Found |
| DELETE | `/livros/{id}`      | Remove um livro                             | 200 OK      | 404 Not Found |

## Como executar

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

- API: http://127.0.0.1:8000
- Documentação interativa (Swagger): http://127.0.0.1:8000/docs

O banco `biblioteca.db` é criado automaticamente na primeira execução.