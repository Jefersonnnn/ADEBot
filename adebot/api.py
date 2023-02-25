import datetime
import os

import requests
import pickle
from bs4 import BeautifulSoup

USERNAME = os.getenv("ADE_USERNAME")
PASSWORD = os.getenv("ADE_PASSWORD")
BASE_URL = 'https://adembraco.com.br/'


def delete_session():
    try:
        os.remove('sessao.pickle')
    except FileNotFoundError:
        return


def load_session() -> requests.Session:
    try:
        with open('sessao.pickle', 'rb') as file_s:
            sessao = pickle.load(file_s)
    except FileNotFoundError:
        sessao = None

    return sessao


def login():
    session = load_session()
    if session:
        if session.get(url=BASE_URL + 'reservas/quadras/').url == BASE_URL + 'reservas/login/':
            delete_session()
        else:
            return session

    # Realizar o login no site
    session = requests.Session()
    login_url = BASE_URL + 'reservas/login/'

    payload = {'empresaLogin': '4',
               'matriculaLogin': USERNAME,
               'senhaLogin': PASSWORD,
               'goto': '',
               'Entrar': 'Entrar'}

    if session.post(login_url, data=payload).url == BASE_URL + 'reservas/login/':
        raise Exception("Não foi possível realizar o login no site")

    # Salvar sessao em um arquivo usando pickle
    delete_session()
    with open('sessao.pickle', 'wb') as file_s:
        pickle.dump(session, file_s)

    return session


def listar_quadras(session: requests.Session):
    quadras_url = BASE_URL + 'reservas/quadras/'
    page = session.get(quadras_url)

    # Extrair as informações sobre as quadras disponíveis a partir da página
    soup = BeautifulSoup(page.content, 'html.parser')

    # Encontrar o elemento 'select' com o id='select_espaco'
    select_espaco = soup.find('select', {'id': 'select_espaco'})

    if not select_espaco:
        return []

    quadras = []
    for option in select_espaco.find_all('option'):
        nome = option.text.strip()
        _id = option['value']

        quadras.append({'nome': nome, 'id': _id})
    return quadras


def listar_datas_disponiveis(session, id_quadra):
    datas_url = BASE_URL + "wp-content/themes/template_ade/ajax/list.available_dates.php"
    payload = {'spaceID': id_quadra,
               'type': 'avulso'}

    lista_datas = session.post(url=datas_url, data=payload)
    if 'days' in lista_datas.json():
        return lista_datas.json()['days']


def listar_horarios_disponiveis(session: requests.Session, id_quadra: int, data: datetime.date):
    horarios_url = BASE_URL + "wp-content/themes/template_ade/ajax/list.hours.php"

    payload = {'space_id': {id_quadra},
               'date_search': data.strftime('%Y-%m-%d'),
               'type': 'avulso'}
    lista_horarios = session.post(horarios_url, data=payload)
    return lista_horarios.json()['hours']


if __name__ == "__main__":
    session = login()
    datas = listar_datas_disponiveis(session, id_quadra=2399)

    horarios = listar_horarios_disponiveis(session, id_quadra=2399, data=datetime.date(2023, 2, 24))

    print(datas, '\n\n', horarios)
