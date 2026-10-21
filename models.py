from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Livro(Base):
    __tablename__ = "livros"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False, index=True)
    autor = Column(String, nullable=False)
    ano_publicacao = Column(Integer, nullable=False)
    preco = Column(Float, nullable=False)
    disponivel = Column(Boolean, nullable=False, default=True)


class Leitor(Base):
    __tablename__ = "leitores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String(11), nullable=False)
    cep = Column(String(8), nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)


class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    leitor_id = Column(Integer, ForeignKey("leitores.id"), nullable=False)
    data_emprestimo = Column(Date, nullable=False)
    data_prevista_devolucao = Column(Date, nullable=False)
    data_devolucao = Column(Date, nullable=True)

    livro = relationship("Livro")
    leitor = relationship("Leitor")