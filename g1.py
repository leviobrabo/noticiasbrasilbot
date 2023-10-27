import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3


import time
from db import create_news_table, create_sports_table

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

# ULTIMAS NOTÍCIAS
def get_news():
    url = 'https://g1.globo.com/ultimas-noticias/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, timeout=10, headers=headers)
    html = bs(response.text, 'html.parser')

    noticias = html.find_all('div', {'class': 'feed-post'})

    for noticia in noticias:
        titulo = noticia.find('a', {'class': 'feed-post-link gui-color-primary gui-color-hover'})
        descricao = noticia.find('div', {'class': 'feed-post-body-resumo'})
        link = noticia.find('a', {'class': 'feed-post-figure-link gui-image-hover'})
        data = noticia.find('span', {'class': 'feed-post-datetime'})
        onde = noticia.find('span', {'class': "feed-post-metadata-section"})

        if titulo and descricao and link and data:
            titulo_text = titulo.text.strip()
            descricao_text = descricao.text.strip()
            link_href = link['href']
            data_text = data.text.strip()
            onde_text = onde.text.strip()

            yield {
                'title': titulo_text,
                'description': descricao_text,
                'link': link_href,
                'date': data_text,
                'onde': onde_text
            }
            time.sleep(3600)


def send_news_to_channel():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()

    for news_article in get_news():
        title = news_article['title']
        link = news_article['link']
        description = news_article['description']
        date = news_article['date']
        where = news_article['onde']

        cursor.execute('SELECT * FROM sent_news WHERE title=?', (title,))
        if cursor.fetchone():
            continue

        bot.send_message('-1001882188409', f'<b>{title}</b>\n\n{description}\n\n{date} - Em {where} #News\n\n<a href="{link}">Saiba mais</a>')
        print(f"Enviado notícia G1: {title}")

        cursor.execute('INSERT INTO sent_news (title) VALUES (?)', (title,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    while True:
        send_news_to_channel()

