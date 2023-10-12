import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3
import codecs
from datetime import datetime


import time
from db import create_news_table, create_sports_table

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

# ULTIMAS NOTÍCIAS
def get_folha():
    url = 'https://www1.folha.uol.com.br/ultimas-noticias/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = bs(response.text, 'html.parser')

    folhas = html.find_all('div', {'class':"page"})

    for folha in folhas:
        titulo = folha.find('h2', {'class':"c-main-headline__title"})
        descricao = folha.find('p', {'class':"c-main-headline__standfirst"})
        link = folha.find('a', {'class':"c-main-headline__url"})
        data = folha.find('time', {'class':"c-headline__dateline"})


        if titulo and descricao and link and data:
            titulo_text = titulo.text.strip()
            titulo_text = codecs.encode(titulo_text, 'latin-1').decode('utf-8', 'ignore')  
            descricao_text = descricao.text.strip()
            link_href = link['href']
            data_text = data['datetime']

            data_datetime = datetime.strptime(data_text, "%Y-%m-%d %H:%M")
            data_formatada = data_datetime.strftime("%d.%b.%Y às %Hh%M")

            yield {
                'title': titulo_text,
                'description': descricao_text,
                'link': link_href,
                'date': data_formatada,
            }
            time.sleep(120)

def send_folha_to_channel():
    conn = sqlite3.connect('folha.db')
    cursor = conn.cursor()

    for folha_article in get_folha():
        title = folha_article['title']
        link = folha_article['link']
        description = folha_article['description']
        date = folha_article['date']

        cursor.execute('SELECT * FROM sent_folha WHERE title=?', (title,))
        if cursor.fetchone():
            continue

        bot.send_message('-1001882188409', f'<b>{title}</b>\n\n{description}\n\n{date} #News\n\n<a href="{link}">Saiba mais</a>')
        print(f"Enviado notícia Folha: {title}")

        cursor.execute('INSERT INTO sent_folha (title) VALUES (?)', (title,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    while True:
        send_folha_to_channel()

