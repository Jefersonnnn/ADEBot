from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Date, Boolean, UniqueConstraint, \
    func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Modelo de dados para a tabela Quadras
class Quadra(Base):
    __tablename__ = 'quadras'

    id = Column(Integer, primary_key=True)
    id_ade = Column(Integer)
    nome = Column(String)
    datas = relationship('QuadraData', back_populates='quadra')

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Modelo de dados para a tabela Datas
class QuadraData(Base):
    __tablename__ = 'quadras_datas'

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    id_quadra = Column(Integer, ForeignKey('quadras.id'), nullable=False)
    quadra = relationship('Quadra', back_populates='datas')
    horarios = relationship('QuadraHorario', back_populates='data')

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args = (UniqueConstraint('data', 'id_quadra'), {})


# Modelo de dados para a tabela Horarios
class QuadraHorario(Base):
    __tablename__ = 'quadras_horarios'

    id = Column(Integer, primary_key=True)
    init_date = Column(DateTime, nullable=False)
    disponivel = Column(Boolean)
    data_id = Column(Integer, ForeignKey('quadras_datas.id'), nullable=False)
    data = relationship('QuadraData', back_populates='horarios')

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args = (UniqueConstraint('init_date', 'data_id'), {})


# Modelo de dados para a tabela Avisos
class Alertas(Base):
    __tablename__ = 'alertas'
    id = Column(Integer, primary_key=True)
    id_quadra = Column(Integer, nullable=False)
    init_date = Column(DateTime, nullable=False)
    telegram_chat_id = Column(Integer, nullable=False)
    usuario_informado = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args = (UniqueConstraint('id_quadra', 'data', 'horario', 'telegram_chat_id'), {})


# Cria o engine para o banco de dados SQLite
engine = create_engine('sqlite:///database.db')

# Cria as tabelas no banco de dados
Base.metadata.create_all(engine)

# Cria uma sessão para manipular os dados
Session = sessionmaker(bind=engine)
session = Session()
