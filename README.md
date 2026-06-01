# Notícias Brasil

Bot que envia notícias do [G1 News](https://g1.globo.com/ultimas-noticias/) automaticamente para o canal do Telegram [Notícias Brasil](https://t.me/noticiasbrasil24h).

[![](https://i.imgur.com/6w7p7Ao.png)](#)

---

## Funcionalidades

- Busca notícias no G1 a cada 12 minutos
- Cria posts no Telegraph com o conteúdo completo das matérias
- Envia para o canal do Telegram com intervalo de 1 hora entre cada notícia
- Deduplicação por título e link — não reposta a mesma notícia
- Limpeza automática do banco às 00:00 e relatório diário às 23:58
- Comandos de administração para usuários sudo

## Comandos

| Comando   | Acesso | Descrição                              |
|-----------|--------|----------------------------------------|
| `/start`  | Todos  | Apresenta o bot e registra o usuário   |
| `/sys`    | Sudo   | Uso de CPU e RAM do servidor           |
| `/stats`  | Sudo   | Notícias postadas hoje, usuários, grupos |

---

## Rodando o bot

### Pré-requisitos

- Python 3.10+
- MongoDB (local ou Atlas)
- Token do Telegram Bot ([@BotFather](https://t.me/BotFather))
- Token do Telegraph

### Instalação

```bash
# Clone o repositório
git clone https://github.com/leviobrabo/noticiasbrasil.git
cd noticiasbrasil

# Instale as dependências
pip3 install -r requirements.txt

# Configure o bot
cp sample.bot.conf bot.conf
vi bot.conf   # preencha as variáveis abaixo
```

### Variáveis de configuração (`bot.conf`)

```ini
[NEWS]
TOKEN=              # Token do bot (BotFather)
NEWS_LOG=           # ID do grupo de logs
NEWS_CHANNEL=       # ID do canal onde as notícias são postadas
BOT_NAME=           # Nome do bot
BOT_USERNAME=       # Username do bot (sem @)
OWNER_ID=           # ID do dono
CHANNEL_USERNAME=   # Username do canal (sem @)
OWNER_USERNAME=     # Username do dono (sem @)
TELEGRAPH_TOKEN=    # Token da API do Telegraph

[DB]
MONGO_CON=          # URI de conexão com o MongoDB

[LOG]
LOG_PATH=           # Caminho para o arquivo de log (ex: bot.log)
```

### Executando

```bash
python3 main.py
```

---

## Estrutura do projeto

```
noticiasbrasilbot/
├── main.py          # Lógica principal do bot
├── db.py            # Interface com o MongoDB
├── sample.bot.conf  # Template de configuração
├── requirements.txt # Dependências Python
└── start            # Script de inicialização
```
