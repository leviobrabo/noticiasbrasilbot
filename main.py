import requests
from bs4 import BeautifulSoup

import configparser
from telebot.apihelper import ApiTelegramException
import psutil

import telebot
from telebot import types
import telegraph

from datetime import datetime, timedelta
from time import sleep

import io
import schedule
import db
from loguru import logger


config = configparser.ConfigParser()
config.read('bot.conf')
logger.add(config['LOG']['LOG_PATH'])

TOKEN = config['NEWS']['TOKEN']
GROUP_LOG = int(config['NEWS']['NEWS_LOG'])
CHANNEL = int(config['NEWS']['NEWS_CHANNEL'])
CHANNEL_USERNAME = config['NEWS']['CHANNEL_USERNAME']
BOT_NAME = config['NEWS']['BOT_NAME']
BOT_USERNAME = config['NEWS']['BOT_USERNAME']
OWNER = int(config['NEWS']['OWNER_ID'])
OWNER_USERNAME = config['NEWS']['OWNER_USERNAME']
TELEGRAPH = config['NEWS']['TELEGRAPH_TOKEN']

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Anti-spam

for _ in range(4):
    try:
        bot.send_message
    except ApiTelegramException as ex:
        if ex.error_code == 429:
            sleep(ex.result_json['parameters']['retry_after'])
        else:
            raise
else:
    bot.send_message

# SUDO


def sudo(user_id):
    user = db.search_user(user_id)
    if user and user.get('sudo') == 'true':
        return True
    return False


# sys


@bot.message_handler(commands=['sys'])
def cmd_sys(message: types.Message):
    user_id = message.from_user.id
    if sudo(user_id):
        bot.reply_to(
            message,
            f'\n──❑ 「 System Stats 」 ❑──\n\n ☆ CPU usage: {psutil.cpu_percent(4)} %\n ☆ RAM usage: {psutil.virtual_memory()[2]} %',
        )


# start


@bot.message_handler(commands=['start'])
def cmd_start(message):
    try:
        if message.chat.type != 'private':
            return
        user_id = message.from_user.id
        user = db.search_user(user_id)
        first_name = message.from_user.first_name

        if not user:
            db.add_user_db(message)
            user = db.search_user(user_id)
            user_info = f"<b>#{BOT_USERNAME} #New_User</b>\n<b>User:</b> {user['first_name']}\n<b>ID:</b> <code>{user['user_id']}</code>\n<b>Username</b>: {user['username']}"
            bot.send_message(GROUP_LOG, user_info)
            logger.info(
                f'novo usuário ID: {user["user_id"]} foi criado no banco de dados'
            )
            return

        markup = types.InlineKeyboardMarkup()
        add_group = types.InlineKeyboardButton(
            '✨ Adicione-me em seu grupo',
            url=f'https://t.me/{BOT_USERNAME}?startgroup=true',
        )
        channel_ofc = types.InlineKeyboardButton(
            'Canal Oficial 🇧🇷', url=f'https://t.me/{CHANNEL_USERNAME}'
        )
        how_to_use = types.InlineKeyboardButton(
            '⚠️ Como usar o bot', callback_data='how_to_use'
        )

        markup.row(add_group)
        markup.row(channel_ofc, how_to_use)

        photo = 'https://telegra.ph/file/ae233348e8ca7c9765ae4.jpg'
        msg_start = f"Olá, <b>{first_name}</b>!\n\nEu sou <b>{BOT_NAME}</b>, um bot que envia Notícias do dia.\n\nAdicione-me em seu grupo para receber as mensagens lá.\n\n📦<b>Meu código-fonte:</b> <a href='https://github.com/leviobrabo/noticiasbrasil24h'>GitHub</a>"

        bot.send_photo(
            message.chat.id,
            photo=photo,
            caption=msg_start,
            reply_markup=markup,
        )

    except Exception as e:
        logger.error(e)


# Noticias

def get_news(limit=5):
    logger.info('Obtendo notícias...')
    url = 'https://g1.globo.com/ultimas-noticias/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code != 200:
            logger.error(
                f'Erro ao obter notícias. Status Code: {response.status_code}'
            )
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        post_sections = soup.find_all('div', {'class': 'bastian-feed-item'})

        news_list = []
        for section in post_sections:
            logger.info('Notícia recebida')

            title_element = section.find('a', {'class': 'feed-post-link'})
            description_element = section.find(
                'div', {'class': 'feed-post-body-resumo'}
            )
            link_element = section.find('a', {'class': 'feed-post-link'})
            image_element = section.find(
                'img', {'class': 'bstn-fd-picture-image'}
            )

            if link_element:
                link_response = requests.get(
                    link_element['href'], timeout=10, headers=headers
                )
            else:
                print('Link não encontrado')
                continue
            link_content = BeautifulSoup(link_response.content, 'html.parser')

            full_text_content = link_content.find_all(
                'div', {'class': 'mc-column content-text active-extra-styles'}
            )
            media_content = link_content.find_all(
                'div', {'class': 'mc-column content-media__container'}
            )

            full_text = ''
            media_links = []
            for text_section in full_text_content:
                text = text_section.get_text(strip=True)
                if text:
                    full_text += text + '\n\n'

            for media_section in media_content:
                media_element = media_section.find('img')
                if media_element and 'src' in media_element.attrs:
                    media_links.append(media_element['src'])
                    full_text += f'<img src="{media_element["src"]}">\n\n''src'

            autor_element = link_content.find(
                'p', {'class': 'content-publication-data__from'}
            )

            if (
                title_element
                and link_element
                and description_element
                and image_element
            ):
                title = title_element.text.strip()
                link = link_element['href']
                description = description_element.text.strip()
                image_url = image_element['src']

                if autor_element:
                    autor = autor_element.text
                else:
                    autor = None

                news_list.append(
                    {
                        'title': title,
                        'description': description,
                        'link': link,
                        'image': image_url,
                        'autor': autor,
                        'full_text': full_text,
                    }
                )
                if len(news_list) >= limit:
                    break

        logger.info(f'{len(news_list)} notícias obtidas.')
        return news_list

    except Exception as e:
        logger.exception(f'Erro ao obter notícias: {str(e)}')
        return []


def upload_telegraph_image(image_url, attempt=0):
    logger.info('Fazendo upload da imagem no Telegraph...')
    if attempt == 3:
        return None

    telegraph_api = telegraph.Telegraph(TELEGRAPH)

    try:
        file = requests.get(image_url)
        if file.status_code != 200:
            logger.warning(f'Erro ao baixar imagem do link: {image_url}')
            return None

        inmemoryfile = io.BytesIO(file.content)
        path = telegraph_api.upload_file(inmemoryfile)
        return f'https://telegra.ph{path[0]["src"]}' if path else None

    except Exception as e:
        logger.exception(
            f'Erro ao fazer upload da imagem no Telegraph: {str(e)}'
        )
        return None


def create_telegraph_post(
    title, description, link, image_url, autor, full_text
):
    logger.info('Criando post no Telegraph...')
    try:
        telegraph_api = telegraph.Telegraph(TELEGRAPH)

        formatted_text = ''.join(
            [f'<p>{paragraph}</p>' for paragraph in full_text.split('\n\n')])
        formatted_title = f'<strong>{title}</strong>'

        iv_template = """
            <figure>
                <img src="{}">
                <figcaption>{}</figcaption>
            </figure>
            <p>{}</p>
            <a href="{}">Leia a matéria original</a>
            <footer>{}</footer>
        """.format(image_url, description, formatted_title, link, autor)

        response = telegraph_api.create_page(
            f'{title}',
            html_content=iv_template,
            author_name=f'{autor}',
        )
        return response['url'], title, link

    except Exception as e:
        logger.exception(f'Erro ao criar post no Telegraph: {str(e)}')
        return None, None, None


def create_telegraph_posts():
    logger.info('Criando posts no Telegraph...')
    news = get_news()
    telegraph_links = []

    for n in news:
        title = n['title']
        description = n['description']
        link = n['link']
        image_url = n['image']
        autor = n['autor']
        full_text = n['full_text']

        telegraph_link = create_telegraph_post(
            title, description, link, image_url, autor, full_text
        )
        if telegraph_link[0]:
            telegraph_links.append(telegraph_link)

    logger.info(f'{len(telegraph_links)} posts criados no Telegraph.')
    return telegraph_links


def total_news():
    try:
        all_news = db.get_all_news()
        total_count = len(list(all_news))
        bot.send_message(
            GROUP_LOG,
            f'TOTAL de Notícia enviada hoje: <code>{total_count}</code> Notícias',
        )
    except Exception as e:
        logger.exception(f'Error sending total news count: {str(e)}')


schedule.every().day.at('23:58').do(total_news)


def delete_news():
    try:
        logger.info('Deletando todas as noticias do bnaco de dados...')
        db.remove_all_news()
    except Exception as e:
        logger.exception(
            f'Erro ao deletar as notícias do banco de dados: {str(e)}'
        )


schedule.every().day.at('00:00').do(delete_news)

if __name__ == '__main__':
    while True:
        try:
            logger.info('Iniciando o bot...')
            created_links = create_telegraph_posts()

            for telegraph_link, title, original_link in created_links:
                news_name = db.search_title(title)

                if news_name:
                    logger.info('A notícia já foi postada.')
                else:
                    logger.info(
                        'Adicionando notícia ao banco de dados e enviando mensagem...'
                    )
                    current_datetime = datetime.now() - timedelta(hours=3)
                    date = current_datetime.strftime('%d/%m/%Y - %H:%M:%S')
                    db.add_news(title, date)

                    logger.info('Enviando notícia...')
                    bot.send_message(
                        CHANNEL,
                        f'<a href="{telegraph_link}">󠀠</a><b>{title}</b>\n\n'
                        f'🗞 <a href="{original_link}">G1 NEWS</a>',
                    )
                    sleep(720)

            logger.info('Todas as notícias foram enviadas para o Telegram.')
            sleep(3600)
            logger.info('Reiniciando a pesquisa após 1h')
            schedule.run_pending()
            sleep(60)
            logger.info('Observando se há schedule')

        except Exception as e:
            logger.exception(f'Erro não tratado: {str(e)}')
