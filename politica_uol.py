import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3


import time
from db import create_politica_table, create_sports_table

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

# ULTIMAS NOTÍCIAS
def get_politica():
    url = 'https://noticias.uol.com.br/politica/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = bs(response.text, 'html.parser')

    noticias = html.find_all('div', {'class':"collection-standard"})

    for noticia in noticias:
        titulo = noticia.find('h3', {'class':"thumb-title title-xsmall title-lg-small"})
        link = noticia.find('a', {'class':"thumbnails-wrapper"})
        data = noticia.find('time', {'class':"thumb-date"})
        autor = noticia.find('p', {'class':"author"})

        if titulo and link and autor and data:
            titulo_text = titulo.text.strip()
            link_href = link['href']
            data_text = data.text.strip()
            autor_text = autor.text.strip()

            yield {
                'title': titulo_text,
                'link': link_href,
                'date': data_text,
                'autor': autor_text
            }
            time.sleep(3600)


def send_politica_to_channel():
    conn = sqlite3.connect('politica.db')
    cursor = conn.cursor()

    for politica_article in get_politica():
        title = politica_article['title']
        link = politica_article['link']
        date = politica_article['date']
        autor = politica_article['onde']

        cursor.execute('SELECT * FROM sent_politica WHERE title=?', (title,))
        if cursor.fetchone():
            continue

        bot.send_message('-1001882188409', f'<b>{title}</b>\n\n{date} - Por {autor} #Politica \n\n<a href="{link}">Saiba mais</a>')
        print(f"Enviado Política UOL: {title}")

        cursor.execute('INSERT INTO sent_politica (title) VALUES (?)', (title,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    while True:
        send_politica_to_channel()

