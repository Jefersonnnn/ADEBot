from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Modelo de dados para a tabela Quadras
class Quadra(Base):
    __tablename__ = 'quadras'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    descricao = Column(String)
    datas = relationship('Data', back_populates='quadras_datas')


# Modelo de dados para a tabela Datas
class QuadraData(Base):
    __tablename__ = 'quadras_datas'

    id = Column(Integer, primary_key=True)
    data = Column(DateTime)
    quadra_id = Column(Integer, ForeignKey('quadras.id'))
    quadra = relationship('Quadra', back_populates='datas')
    horarios = relationship('QuadrasHorario', back_populates='data')


# Modelo de dados para a tabela Horarios
class QuadraHorario(Base):
    __tablename__ = 'quadras_horarios'

    id = Column(Integer, primary_key=True)
    horario = Column(String)
    disponivel = Column(Integer)
    data_id = Column(Integer, ForeignKey('datas.id'))
    data = relationship('Data', back_populates='horarios')


# Modelo de dados para a tabela Avisos
class Aviso(Base):
    __tablename__ = 'avisos'
    id = Column(Integer, primary_key=True)
    id_quadra = Column(Integer)
    data = Column(Date)
    horario = Column(String(255))
    telegram_chat_id = Column(Integer)
    usuario_informado = Column(Boolean, default=False)


# Cria o engine para o banco de dados SQLite
engine = create_engine('sqlite:///database.db')

# Cria as tabelas no banco de dados
Base.metadata.create_all(engine)

# Cria uma sessão para manipular os dados
Session = sessionmaker(bind=engine)
session = Session()
