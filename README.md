## Configuração do bot
Requisitos
Antes de iniciar o bot, você precisa ter instalado o Python 3 em seu sistema. Além disso, você também precisa ter o gerenciador de pacotes Poetry instalado. Para instalar o Poetry, execute o seguinte comando no terminal:

````shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
````

### Variáveis de ambiente
Para que o bot funcione corretamente, você precisa definir algumas variáveis de ambiente. A maneira de fazer isso varia de acordo com o sistema operacional que você está usando.

#### Linux 
Para definir as variáveis de ambiente no Linux, abra o terminal e execute os seguintes comandos:
```shell
export TOKEN_BOT_TELEGRAM='<TOKEN_BOT_TELEGRAM>'
export DEVELOPER_CHAT_ID='<TELEGRAM_CHAT_ID>'
export ADE_USERNAME='<USERNAME_ADE>'
export ADE_PASSWORD='<PASSWORD_ADE>'
```

#### Windows  
Para definir as variáveis de ambiente no Windows, siga estas etapas:

1. Abra o menu Iniciar e pesquise por "Variáveis de ambiente".
2. Clique em "Editar as variáveis de ambiente do sistema".
3. Clique no botão "Variáveis de ambiente".
4. Clique em "Nova" para adicionar uma nova variável de ambiente.
5. Digite "TOKEN_BOT_TELEGRAM" como o nome da variável e o seu token do bot como o valor da variável.
6. Repito para as variáveis: DEVELOPER_CHAT_ID, ADE_USERNAME e ADE_PASSWORD
8. Clique em "OK" para salvar as alterações.

### Run App

O Poetry é uma ferramenta de gerenciamento de pacotes para Python. Para instalar as dependências do projeto usando o Poetry, execute o seguinte comando no terminal:

```shell
poetry install
```

```shell
poetry run run-app
```


