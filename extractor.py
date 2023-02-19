import datetime
import logging
import time

from api import login, listar_quadras, listar_datas_disponiveis, listar_horarios_disponiveis
from models import session as db_session, Quadra, QuadraHorario, QuadraData, Alertas

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def extrair_quadras(session):
    logger.info("EXTRAIR_QUADRAS INICIADO")
    quadras = listar_quadras(session)

    for quadra in quadras:
        _q = db_session.query(Quadra).filter_by(id_ade=quadra['id']).first()

        if not _q:
            db_session.add(Quadra(id_ade=quadra['id'], nome=quadra['nome']))
        db_session.commit()
    logger.info("EXTRAIR_QUADRAS FINALIZADO")


def extrair_datas_atuais(session):
    logger.info("EXTRAIR_DATAS_ATUAIS INICIADO")
    quadras = db_session.query(Quadra).all()

    for quadra in quadras:
        logger.info(f"--QUADRA {quadra.nome}")
        time.sleep(5)  # Aguardar
        datas = listar_datas_disponiveis(session, id_quadra=quadra.id_ade)
        for data in datas:
            _data = datetime.datetime.strptime(list(data.keys())[0], '%Y-%m-%d').date()
            logger.info(f"--DATA {_data}")
            _qd = db_session.query(QuadraData).filter_by(id_quadra=quadra.id, data=_data).first()
            if not _qd:
                db_session.add(QuadraData(data=_data, id_quadra=quadra.id))
            db_session.commit()
    logger.info("EXTRAIR_DATAS_ATUAIS FINALIZADO")


def extrair_horarios(session):
    logger.info("EXTRAIR_HORARIOS INICIADO")
    avisos = db_session.query(Alertas).filter_by(usuario_informado=False).all()

    for aviso in avisos:
        datas_quadra = db_session.query(QuadraData).filter_by(
            id_quadra=aviso.id_quadra,
            data=aviso.init_date.date()
        ).all()

        for data in datas_quadra:
            time.sleep(5)
            horarios = listar_horarios_disponiveis(session, id_quadra=data.quadra.id_ade, data=data.data)
            for hora in horarios:
                _init_date = datetime.datetime.strptime(hora['init_date'], '%Y-%m-%d %H:%M:%S')
                _qh = db_session.query(QuadraHorario).filter(
                    QuadraHorario.init_date == _init_date,
                    QuadraHorario.data_id == data.id) \
                    .first()
                if not _qh:
                    db_session.add(QuadraHorario(init_date=_init_date, disponivel=not hora['booked'], data_id=data.id))
                else:
                    _qh.disponivel = not hora['booked']
                db_session.commit()
    logger.info("EXTRAIR_HORARIOS FINALIZADO")


def run():
    session = login()
    extrair_quadras(session)
    extrair_datas_atuais(session)
    # extrair_horarios(session)


if __name__ == '__main__':
    run()
