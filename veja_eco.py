import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3

import time
from db import create_news_table, create_sports_table

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

# ULTIMAS ECONOMIA
def get_eco():
    url = 'https://veja.abril.com.br/economia/?utm_source=google&utm_medium=cpc&utm_campaign=eda_veja_audiencia_mercado&gad=1&gclid=Cj0KCQjwj5mpBhDJARIsAOVjBdooITTzhNRUD_iQog9BulvCWvAqirQJqCWWEXXwfyLtqqMFl1AIxDsaAoPZEALw_wcB'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, timeout=10, headers=headers)
    html = bs(response.text, 'html.parser')

    ecos = html.find_all('div', {'id':"infinite-list"})

    for eco in ecos:
        titulo = eco.find('h2', {'class':"title "})
        link = eco.find('a', {'class':'title'})
        data = eco.find('span', {'class': 'feed-post-datetime'})
        autor = eco.find('span', {'class':"author"})

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
            time.sleep(7200)


def send_eco_to_channel():
    conn = sqlite3.connect('eco.db')
    cursor = conn.cursor()

    for eco_article in get_eco():
        title = eco_article['title']
        link = eco_article['link']
        autor = eco_article['autor']

        cursor.execute('SELECT * FROM sent_eco WHERE title=?', (title,))
        if cursor.fetchone():
            continue

        bot.send_message('-1001882188409', f'<b>{title}</b>\n\n\n{autor} #Economia\n\n<a href="{link}">Saiba mais</a>')
        print(f"Enviado VEJA_ECO: {title}")

        cursor.execute('INSERT INTO sent_eco (title) VALUES (?)', (title,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    while True:
        send_eco_to_channel()

