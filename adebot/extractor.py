from datetime import datetime, timedelta
import logging
import time

from adebot.api import login, listar_quadras, listar_datas_disponiveis, listar_horarios_disponiveis
from adebot.models import session as db_session, Quadra, QuadraHorario, QuadraData, Alertas

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def _gerar_alerta_recorrente(current_alert: Alertas):
    if not current_alert.is_recurring:
        return

    next_day_week = current_alert.init_date + timedelta(weeks=1)

    new_alert = Alertas(
        id_quadra=current_alert.id_quadra,
        init_date=next_day_week,
        chat_id=current_alert.chat_id,
        is_recurring=current_alert.is_recurring
    )
    try:
        db_session.add(new_alert)
        db_session.commit()
    except Exception as e:
        logger.error("Não foi possível gerar alerta: ", e)
        db_session.rollback()


def _excluir_alertas_antigos():
    _data_atual = datetime.now()
    _alertas = db_session.query(Alertas).filter(
        Alertas.init_date < _data_atual
    ).all()

    if len(_alertas) > 0:
        for alerta in _alertas:
            _gerar_alerta_recorrente(alerta)
            try:
                db_session.delete(alerta)
                db_session.commit()
            except Exception as e:
                logger.error("Não foi possível deletar uma data antiga: ", e)
                db_session.rollback()


def _excluir_datas_antigas():
    _data_atual = datetime.now()
    _qd = db_session.query(QuadraData).filter(
        QuadraData.data < _data_atual.date()
    ).all()

    if len(_qd) > 0:
        for q in _qd:
            try:
                db_session.delete(q)
                db_session.commit()
            except Exception as e:
                logger.error("Não foi possível deletar uma data antiga: ", e)
                db_session.rollback()


def _clean_database():
    _excluir_datas_antigas()
    _excluir_alertas_antigos()


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
    _clean_database()
    logger.info("EXTRAIR_DATAS_ATUAIS INICIADO")
    quadras = db_session.query(Quadra).filter(Alertas.id_quadra == Quadra.id).all()

    for quadra in quadras:
        logger.info(f"--QUADRA {quadra.nome}")
        time.sleep(5)  # Aguardar
        datas = listar_datas_disponiveis(session, id_quadra=quadra.id_ade)
        for data in datas:
            _data = datetime.strptime(list(data.keys())[0], '%Y-%m-%d').date()
            logger.info(f"--DATA {_data}")
            _qd = db_session.query(QuadraData).filter_by(id_quadra=quadra.id, data=_data).first()
            if not _qd:
                db_session.add(QuadraData(data=_data, id_quadra=quadra.id))
            db_session.commit()
    logger.info("EXTRAIR_DATAS_ATUAIS FINALIZADO")


def extrair_horarios(session):
    _clean_database()

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
                _init_date = datetime.strptime(hora['init_date'], '%Y-%m-%d %H:%M:%S')
                logger.info(f"Verificando data: {_init_date}")
                _qh = db_session.query(QuadraHorario).filter(
                    QuadraHorario.init_date == _init_date,
                    QuadraHorario.data_id == data.id) \
                    .first()
                if not _qh:
                    db_session.add(QuadraHorario(init_date=_init_date, disponivel=not hora['booked'], data_id=data.id))
                else:
                    logger.info(f"Atualizando data: {_init_date} - Reservado {_qh.disponivel} -> {not hora['booked']}")
                    _qh.disponivel = not hora['booked']
                db_session.commit()
    logger.info("EXTRAIR_HORARIOS FINALIZADO")


if __name__ == '__main__':
    alerta_quadra = Alertas(
        id=1,
        id_quadra=4,
        init_date=datetime(year=2023, month=3, day=1, hour=20, minute=0),
        chat_id=1234,
        is_recurring=True
    )

    _gerar_alerta_recorrente(alerta_quadra)
