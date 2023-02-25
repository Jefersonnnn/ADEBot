import os
import threading
from datetime import datetime, time, timedelta
import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from api import login
from extractor import extrair_quadras, extrair_datas_atuais, extrair_horarios

from models import session as db_session, Quadra, Alertas, QuadraHorario, QuadraData
from utils import validate_date_and_convert

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# This can be your own ID, or one for a developer group/channel.
# You can use the /start command of this bot to see your chat id.
TOKEN_BOT_TELEGRAM = os.getenv("TOKEN_BOT_TELEGRAM")
DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    message = "Escolha uma opção:\n"
    message += "/listar_quadras\n"
    message += "/alerta\n"
    message += "/listar_alertas\n"
    message += "/remover_alerta\n"
    # context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    await update.message.reply_text(message)


async def remover_alerta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove o alerta do usuário."""

    mensagem = update.message.text
    parametros = mensagem.split()
    if len(parametros) <= 1 or len(parametros) > 2:
        message = ""
        message += "/remover_alerta alerta_id\n"
        message += "\tEx: /remover_alerta 123\n"
        await update.message.reply_text(message)
        return

    _id_alerta = parametros[1]
    alerta = db_session.query(Alertas).filter_by(
        id=_id_alerta,
        chat_id=update.message.chat_id).first()

    if not alerta:
        await update.message.reply_text(f"Alerta [id={_id_alerta}] não encontrado!")
        return

    try:
        db_session.delete(alerta)
        db_session.commit()
        await update.message.reply_text("Alerta foi excluído!")
    except Exception:
        db_session.rollback()
        await update.message.reply_text("Erro ao excluir o Alerta!")


async def listar_alertas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    alertas = db_session.query(Alertas).filter_by(
        usuario_informado=False,
        chat_id=update.message.chat_id) \
        .all()

    if not alertas:
        await update.message.reply_text("Nenhum alerta cadastrado até o momento!")
        return

    resp_msg = ''
    for alerta in alertas:
        resp_msg += f"id: {alerta.id} - {datetime.strftime(alerta.init_date, '%d/%m/%Y %H:%M')} - Quadra: {alerta.id_quadra}\n"

    await update.message.reply_text(resp_msg)


async def listar_quadras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    quadras = db_session.query(Quadra).all()

    if not quadras:
        await update.message.reply_text("Nenhum quadra cadastrada até o momento!")
        return

    resp_msg = ''
    for quadra in quadras:
        resp_msg += f'id: {quadra.id} - {quadra.nome}\n'

    await update.message.reply_text(resp_msg)


async def avisar_usuarios(context):
    avisos = db_session.query(Alertas).filter_by(usuario_informado=False).all()
    for aviso in avisos:
        init_date = aviso.init_date
        if init_date.minute == 0:
            next_date = init_date + timedelta(minutes=59)
        elif init_date.minute == 30:
            next_date = init_date + timedelta(minutes=29)
        else:
            next_date = init_date + timedelta(minutes=1)

        horario_disponivel = db_session.query(QuadraHorario).filter(
            QuadraHorario.disponivel == 1,
            QuadraHorario.data.has(QuadraData.id_quadra == aviso.id_quadra),
            QuadraHorario.init_date.between(init_date, next_date)
        ).first()

        if horario_disponivel:
            message = (
                f"Alerta de horario disponível!\n"
                f"<pre>Quadra: {horario_disponivel.data.quadra.nome}"
                "</pre>\n\n"
                f"Data: {datetime.strftime(horario_disponivel.init_date, '%d/%m/%Y %H:%M')}"
                "\n\n"
                f"RESERVE AGORA!"
            )

            # Finally, send the message
            await context.bot.send_message(
                chat_id=aviso.chat_id, text=message, parse_mode=ParseMode.HTML
            )
            aviso.usuario_informado = True
            db_session.commit()


async def alerta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Obter a data e o id da quadra a partir da mensagem do usuário
    mensagem = update.message.text
    parametros = mensagem.split()
    if len(parametros) <= 1 or len(parametros) > 4:
        message = ""
        message += "/alerta DD/MM/YYYY HORARIO ID_DA_QUADRA\n"
        message += "\tEx: /alerta 12/12/2023 20:00 123\n"
        await update.message.reply_text(message)
        return

    data = parametros[1]
    horario = parametros[2]
    id_quadra = parametros[3]

    data = validate_date_and_convert(data, horario)
    if not data:
        await update.message.reply_text(text="Data não está no formato correto [dia/mês/ano] ex 01/01/2023.")
        return
    if data <= datetime.now():
        await update.message.reply_text(text="Não podemos te alertar no passado ainda :/.")
        return

    quadra = db_session.query(Quadra).filter_by(id=id_quadra).first()
    if not quadra:
        await update.message.reply_text(text=f"Quadra de id{id_quadra} não encontrada")
        return

    alerta = db_session.query(Alertas).filter_by(
        usuario_informado=False,
        id_quadra=quadra.id,
        init_date=data,
        chat_id=update.message.chat_id
    ).first()

    if alerta:
        await update.message.reply_text(text=f"Alerta já está criado!")
        return

    try:
        alerta_quadra = Alertas(
            id_quadra=quadra.id,
            init_date=data,
            chat_id=update.message.chat_id
        )

        db_session.add(alerta_quadra)
        db_session.commit()
    except Exception as e:
        await update.message.reply_text(text="Erro ao criar o alerta!")
        return

    # Enviar uma mensagem de confirmação para o usuário
    await update.message.reply_text(text="Alerta registrado com sucesso!")


async def etl_quadras(context=None):
    session = login()
    extrair_quadras(session)

def _etl_quadras(context=None):
    session = login()
    extrair_quadras(session)


async def etl_datas(context=None):
    session = login()
    extrair_datas_atuais(session)

def _etl_datas(context=None):
    session = login()
    extrair_datas_atuais(session)


async def etl_horarios(context=None):
    session = login()
    extrair_horarios(session)


def main() -> None:
    app = ApplicationBuilder().token(TOKEN_BOT_TELEGRAM).build()

    # remove jobs
    app.job_queue.scheduler.remove_all_jobs()

    _etl_quadras()
    _etl_datas()

    # Register the commands...
    app.add_handler(CommandHandler(["start", "help", "menu"], start))
    app.add_handler(CommandHandler(['listar_quadras', 'lista_quadras', 'quadras'], listar_quadras))
    app.add_handler(CommandHandler('alerta', alerta))
    app.add_handler(CommandHandler(['listar_alertas', 'lista_alertas', 'alertas'], listar_alertas))
    app.add_handler(CommandHandler("remover_alerta", remover_alerta))

    # on non command i.e message - echo the message on Telegram
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    # ...and the error handler
    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(etl_quadras, interval=60*60*24*7, first=0)
    app.job_queue.run_repeating(etl_datas, interval=60 * 60 * 12, first=0)
    app.job_queue.run_repeating(etl_horarios, interval=60 * 10, first=0)
    app.job_queue.run_repeating(avisar_usuarios, interval=60 * 5, first=0)

    # Run the bot until the user presses Ctrl-C
    app.run_polling()


if __name__ == "__main__":
    main()
