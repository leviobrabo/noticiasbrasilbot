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


# add_sudo


@bot.message_handler(commands=['add_sudo'])
def add_sudo(message):
    try:
        if message.chat.type == 'private':
            if message.from_user.id == OWNER:
                if len(message.text.split()) == 2:
                    user_id = message.from_user.id
                    user = int(message.text.split()[1])
                    user_db = db.search_user(user)

                    if user_db:
                        if user_db.get('sudo') == 'true':
                            bot.send_message(
                                message.chat.id,
                                'Este usuário já tem permissão de sudo.',
                            )
                        else:
                            result = db.set_user_sudo(user)
                        if result.modified_count > 0:
                            if message.from_user.username:
                                username = '@' + message.from_user.username
                            else:
                                username = 'Não tem um nome de usuário'
                            updated_user = db.search_user(user)
                            if updated_user:
                                bot.send_message(
                                    message.chat.id,
                                    f"<b>Novo sudo adicionado com sucesso</b>\n\n<b>ID:</b> <code>{user}</code>\n<b>Nome:</b> {updated_user.get('first_name')}\n<b>Username:</b> {username}",
                                )
                                bot.send_message(
                                    GROUP_LOG,
                                    f"<b>#{BOT_USERNAME} #New_sudo</b>\n<b>ID:</b> <code>{user}</code>\n<b>Name:</b> {updated_user.get('first_name')}\nU<b>sername:</b> {username}",
                                )
                        else:
                            bot.send_message(
                                message.chat.id,
                                'User not found in the database.',
                            )
                    else:
                        bot.send_message(
                            message.chat.id, 'User not found in the database.'
                        )
                else:
                    bot.send_message(
                        message.chat.id,
                        'Por favor, forneça um ID de usuário após /add_sudo.',
                    )

    except Exception as e:
        logger.error(e)


# rem_sudo
@bot.message_handler(commands=['rem_sudo'])
def unsudo_command(message):
    try:
        if message.chat.type == 'private':
            if message.from_user.id == OWNER:
                if len(message.text.split()) == 2:
                    user_id = int(message.text.split()[1])
                    user = db.search_user(user_id)
                    if user:
                        if user.get('sudo') == 'false':
                            bot.send_message(
                                message.chat.id,
                                'Este usuário já não tem permissão de sudo.',
                            )
                        else:
                            result = db.un_set_user_sudo(user_id)
                            if result.modified_count > 0:
                                if message.from_user.username:
                                    username = '@' + message.from_user.username
                                else:
                                    username = 'Não tem um nome de usuário'
                                updated_user = db.search_user(user_id)
                                if updated_user:
                                    bot.send_message(
                                        message.chat.id,
                                        f"<b>User sudo removido com sucesso</b>\n\n<b>ID:</b> <code>{user_id}</code>\n<b>Nome:</b> {updated_user.get('first_name')}\n<b>Username:</b> {username}",
                                    )
                                    bot.send_message(
                                        GROUP_LOG,
                                        f"<b>#{BOT_USERNAME} #Rem_sudo</b>\n<b>ID:</b> <code>{user_id}</code>\n<b>Nome:</b> {updated_user.get('first_name')}\n<b>Username:</b> {username}",
                                    )
                            else:
                                bot.send_message(
                                    message.chat.id,
                                    'Usuário não encontrado no banco de dados.',
                                )
                    else:
                        bot.send_message(
                            message.chat.id,
                            'Usuário não encontrado no banco de dados.',
                        )
                else:
                    bot.send_message(
                        message.chat.id,
                        'Por favor, forneça um ID de usuário após /rem_sudo.',
                    )

    except Exception as e:
        logger.error(e)


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

                full_text_text = ''
                for text_section in full_text_content:
                    text = text_section.get_text(separator='\n\n', strip=True)
                    if text:
                        full_text_text += text + '\n\n'
                if autor_element:
                    autor = autor_element.text
                else:
                    autor = None
                if len(news_list) >= limit:
                   break
                news_list.append(
                    {
                        'title': title,
                        'description': description,
                        'link': link,
                        'image': image_url,
                        'autor': autor,
                        'full_text': full_text_text,
                    }
                )

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
        response = telegraph_api.create_page(
            f'{title}',
            html_content=(
                f'<img src="{image_url}"><br><br>'
                + f'<h4>{description}</h4><br><br>'
                + f'{full_text}<br><br>'
                + f'<a href="{link}">Leia a matéria original</a>'
            ),
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
        total_count = len(list(all_news))  # Calculate total count
        bot.send_message(
            GROUP_LOG,
            f'TOTAL de Notícia enviada hoje: <code>{total_count}</code> Notícias',
        )  # Send the total count
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
    while True:  # Loop infinito
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
                    db.add_news(title, date)  # Adiciona a notícia ao banco de dados

                    logger.info('Enviando notícia...')
                    bot.send_message(
                        CHANNEL,
                        f'<a href="{telegraph_link}">󠀠</a><b>{title}</b>\n\n'
                        f'🗞 <a href="{original_link}">G1 NEWS</a>',
                    )
                    sleep(720)
                    

            logger.info('Todas as notícias foram enviadas para o Telegram.')
            sleep(3600)
            schedule.run_pending()
            sleep(60)
            
        except Exception as e:
            logger.exception(f'Erro não tratado: {str(e)}')
