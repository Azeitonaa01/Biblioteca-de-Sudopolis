import re
from datetime import date
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ANO_ATUAL = date.today().year
PADRAO_NOME = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ' .-]+\Z")
PADRAO_LETRA = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]")


def _validar_texto(v, campo, minimo, maximo):
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"O campo {campo} é obrigatório e não pode ficar em branco.")
    v = v.strip()
    if len(v) < minimo:
        raise ValueError(f"O campo {campo} deve ter no mínimo {minimo} caracteres.")
    if len(v) > maximo:
        raise ValueError(f"O campo {campo} deve ter no máximo {maximo} caracteres.")
    return v


def _validar_nome(v, campo, minimo, maximo):
    v = _validar_texto(v, campo, minimo, maximo)
    if not PADRAO_NOME.fullmatch(v) or not PADRAO_LETRA.search(v):
        raise ValueError(
            f"O campo {campo} deve conter letras e pode incluir espaços, "
            "hífen, apóstrofo e ponto."
        )
    return v


# ---------- LIVROS ----------
class LivroCreateSchema(BaseModel):
    titulo: str = Field(
        min_length=2, max_length=150, examples=["Dom Casmurro"],
        description="Título do livro (2 a 150 caracteres)",
    )
    autor: str = Field(
        min_length=3, max_length=100, examples=["Machado de Assis"],
        description="Nome do autor (3 a 100 caracteres)",
    )
    ano_publicacao: int = Field(
        ge=1000, le=ANO_ATUAL, examples=[1899],
        description=f"Ano de publicação (entre 1000 e {ANO_ATUAL})",
    )
    preco: float = Field(
        gt=0, le=100000, examples=[39.90],
        description="Preço maior que zero, até R$ 100.000,00 e com no máximo 2 casas decimais",
    )
    disponivel: bool = True

    @field_validator("titulo", mode="before")
    @classmethod
    def validar_titulo(cls, v):
        v = _validar_texto(v, "título", 2, 150)
        if not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]", v):
            raise ValueError("O título deve conter pelo menos uma letra ou número.")
        return v

    @field_validator("autor", mode="before")
    @classmethod
    def validar_autor(cls, v):
        return _validar_nome(v, "autor", 3, 100)

    @field_validator("ano_publicacao", mode="before")
    @classmethod
    def validar_ano(cls, v):
        if isinstance(v, bool) or not (
            isinstance(v, int) or (isinstance(v, str) and re.fullmatch(r"[0-9]+", v))
        ):
            raise ValueError("O ano de publicação deve ser um número inteiro.")
        v = int(v)
        if not (1000 <= v <= ANO_ATUAL):
            raise ValueError(f"O ano de publicação deve estar entre 1000 e {ANO_ATUAL}.")
        return v

    @field_validator("preco", mode="before")
    @classmethod
    def validar_preco(cls, v):
        if isinstance(v, bool) or not isinstance(v, (int, float, str, Decimal)):
            raise ValueError("O preço deve ser um número.")
        try:
            valor = Decimal(str(v))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("O preço deve ser um número.")
        if not valor.is_finite():
            raise ValueError("O preço deve ser um número finito.")
        if valor <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        if valor > 100000:
            raise ValueError("O preço não pode ultrapassar R$ 100.000,00.")
        if valor.as_tuple().exponent < -2 and valor != valor.quantize(Decimal("0.01")):
            raise ValueError("O preço deve ter no máximo 2 casas decimais.")
        return float(valor)
class LivroResponseSchema(LivroCreateSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- LEITORES ----------
class LeitorCreateSchema(BaseModel):
    nome: str = Field(
        min_length=3, max_length=100, examples=["Maria Silva"],
        description="Nome completo (3 a 100 caracteres)",
    )
    telefone: str = Field(
        min_length=11, max_length=11, examples=["11987654321"],
        description="DDD + número, exatamente 11 dígitos",
    )
    cep: str = Field(
        min_length=8, max_length=8, examples=["01310100"],
        description="CEP com exatamente 8 dígitos",
    )
    email: EmailStr = Field(examples=["maria@email.com"])

    @field_validator("nome", mode="before")
    @classmethod
    def validar_nome(cls, v):
        return _validar_nome(v, "nome", 3, 100)

    @field_validator("telefone", mode="before")
    @classmethod
    def validar_telefone(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("O campo telefone é obrigatório e não pode ficar em branco.")
        v = v.strip()
        if not re.fullmatch(r"[0-9]{11}", v):
            raise ValueError("O telefone deve conter 11 dígitos com o DDD.")
        return v

    @field_validator("cep", mode="before")
    @classmethod
    def validar_cep(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("O campo CEP é obrigatório e não pode ficar em branco.")
        v = v.strip()
        if not re.fullmatch(r"[0-9]{8}", v):
            raise ValueError("O CEP deve conter exatamente 8 dígitos.")
        return v

    @field_validator("email", mode="before")
    @classmethod
    def validar_email(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("O campo e-mail é obrigatório e não pode ficar em branco.")
        v = v.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("Insira um e-mail válido no formato nome@dominio.com.")
        return v


class LeitorResponseSchema(LeitorCreateSchema):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- EMPRÉSTIMOS ----------
PRAZO_PADRAO_DIAS = 7
MULTA_POR_DIA = 1.00


class EmprestimoCreateSchema(BaseModel):
    livro_id: int = Field(gt=0, examples=[1], description="ID do livro (maior que zero)")
    leitor_id: int = Field(gt=0, examples=[1], description="ID do leitor (maior que zero)")
    prazo_dias: int = Field(
        default=PRAZO_PADRAO_DIAS, gt=0, le=30, examples=[7],
        description="Prazo de devolução em dias (1 a 30)",
    )
    data_emprestimo: date | None = Field(
        default=None, examples=["2026-10-01"],
        description="Opcional. Data do empréstimo (AAAA-MM-DD). Se vazio, usa hoje. Não pode ser futura.",
    )

    @field_validator("livro_id", "leitor_id", "prazo_dias", mode="before")
    @classmethod
    def validar_numeros(cls, v, info):
        try:
            v = int(v)
        except (TypeError, ValueError):
            raise ValueError(f"O campo {info.field_name} deve ser um número inteiro.")
        if v <= 0:
            raise ValueError(f"O campo {info.field_name} deve ser maior que zero.")
        if info.field_name == "prazo_dias" and v > 30:
            raise ValueError("O prazo de devolução deve ser de no máximo 30 dias.")
        return v

    @field_validator("data_emprestimo")
    @classmethod
    def validar_data(cls, v):
        if v and v > date.today():
            raise ValueError("A data do empréstimo não pode ser no futuro.")
        return v


class EmprestimoResponseSchema(BaseModel):
    id: int
    livro_id: int
    titulo_livro: str
    leitor_id: int
    nome_leitor: str
    data_emprestimo: date
    data_prevista_devolucao: date
    data_devolucao: date | None = None
    dias_com_o_livro: int
    status: str
    dias_atraso: int
    dias_restantes: int
    multa: float
