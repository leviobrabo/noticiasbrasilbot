import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3


import time
from db import create_news_table, create_sports_table

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

# ULTIMAS NOTÍCIAS
def get_ab():
    url = 'https://agenciabrasil.ebc.com.br/ultimas'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = bs(response.text, 'html.parser')

    abs = html.find_all('div', {'class':"col-md-12 order-first view-content"})

    for ab in abs:
        titulo = ab.find('h4', {'clas':"alt-font font-weight-bold my-2"})
        descricao = ab.find('div', {'class':"alt-font text-secondary my-2"})
        link = ab.find('a', {'class':"post-item-desc py-0"})
        data = ab.find('span', {'class':"date-display-interval"})

        if titulo and descricao and link and data:
            titulo_text = titulo.text.strip()
            descricao_text = descricao.text.strip()
            link_href = link['href']
            data_text = data.text.strip()

            yield {
                'title': titulo_text,
                'description': descricao_text,
                'link': link_href,
                'date': data_text,
            }
            time.sleep(300)

def send_ab_to_channel():
    conn = sqlite3.connect('ab.db')
    cursor = conn.cursor()

    for ab_article in get_ab():
        title = ab_article['title']
        link = ab_article['link']
        description = ab_article['description']
        date = ab_article['date']

        cursor.execute('SELECT * FROM sent_ab WHERE title=?', (title,))
        if cursor.fetchone():
            continue

        bot.send_message('-1001882188409', f'<b>{title}</b>\n\n{description}\n\n{date} #News\n\n<a href="{link}">Saiba mais</a>')
        print(f"Enviado AB: {title}")

        cursor.execute('INSERT INTO sent_ab (title) VALUES (?)', (title,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    while True:
        send_ab_to_channel()

