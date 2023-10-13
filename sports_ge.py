import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3

import time
from db import create_news_table, create_sports_table

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

# esportes
def get_sports():
    url = 'https://ge.globo.com/plantao/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, timeout=10, headers=headers)
    html = bs(response.text, 'html.parser')

    esportes = html.find_all('div', class_="feed-root")

    for esporte in esportes:
        titulo = esporte.find('div', class_="feed-post-body-title gui-color-primary gui-color-hover")
        descricao = esporte.find('div', class_="feed-post-body-resumo")
        link = esporte.find('a', class_="feed-post-link gui-color-primary gui-color-hover")
        data = esporte.find('span', class_="feed-post-datetime")

        if titulo and descricao and link and data:
            titulo_text = titulo.text.strip()
            descricao_text = descricao.text.strip()
            link_href = link['href']
            data_text = data.text.strip()

            yield {
                'title': titulo_text,
                'description': descricao_text,
                'link': link_href,
                'date': data_text
            }
            time.sleep(120)

def send_sports_to_channel():
    conn = sqlite3.connect('sports.db')
    cursor = conn.cursor()

    try:
        for sports_article in get_sports():
            title = sports_article['title']
            link = sports_article['link']
            description = sports_article['description']
            date = sports_article['date']

            cursor.execute('SELECT * FROM sent_sports WHERE title=?', (title,))
            if cursor.fetchone():
                continue

            bot.send_message('-1001882188409', f'<b>{title}</b>\n\n{description} - {date} #Esportes\n\n<a href="{link}">Saiba mais</a>')
            print(f"Enviado esportes GE: {title}")

            cursor.execute('INSERT INTO sent_sports (title) VALUES (?)', (title,))
            conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")

    conn.close()

if __name__ == "__main__":
    while True:
        send_sports_to_channel()

