import requests
from bs4 import BeautifulSoup as bs
import telebot
import sqlite3
import codecs
from datetime import datetime
import time
import schedule


import time
from db import create_news_table, create_sports_table, create_eco_table, create_politica_table, create_folha_table, create_ab_table
import sys
print(sys.path)

bot = telebot.TeleBot('6158090839:AAHT3YOgKMMXobnBMZiVJeVV855KmOeXctw', parse_mode="HTML")

def get_ab():
    url = 'https://agenciabrasil.ebc.com.br/ultimas'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    html = bs(response.text, 'html.parser')

    abs = html.find_all('div', {'class':"col-md-12 order-first view-content"})

    for ab in abs:
        image = ab.find('div', class_='shadow overflow-hidden rounded-lg d-block w-100').find('img')
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


# ULTIMAS NOTÍCIAS
def get_folha():
    url = 'https://www1.folha.uol.com.br/ultimas-noticias/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    html = bs(response.text, 'html.parser')

    folhas = html.find_all('div', {'class':"page"})

    for folha in folhas:
        titulo = folha.find('h2', {'class':"c-main-headline__title"})
        descricao = folha.find('p', {'class':"c-main-headline__standfirst"})
        link = folha.find('a', {'class':"c-main-headline__url"})
        data_element = folha.find('time', {'class': "c-headline__dateline"})


        if titulo and descricao and link and data_element:
            titulo_text = titulo.text.strip()
            descricao_text = descricao.text.strip()
            descricao_text = codecs.encode(descricao_text, 'latin-1').decode('utf-8', 'ignore')  
            link_href = link['href']
            data_text = data_element.text.strip()


            yield {
                'title': titulo_text,
                'description': descricao_text,
                'link': link_href,
                'date': data_text,
            }


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

# ULTIMAS NOTÍCIAS
def get_news():
    url = 'https://g1.globo.com/ultimas-noticias/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    response = requests.get(url, timeout=10, headers=headers)
    html = bs(response.text, 'html.parser')

    noticias = html.find_all('div', {'class': 'feed-post'})

    for noticia in noticias:
        imagem = noticia.find('div', {'class': 'bstn-fd-picture-image})
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

def job_get_ab():
    print("Coletando notícias da Agência Brasil...")
    send_ab_to_channel()

def job_get_folha():
    print("Coletando notícias da Folha...")
    send_folha_to_channel()

def job_get_news():
    print("Coletando notícias do G1...")
    send_news_to_channel()

def job_get_politica():
    print("Coletando notícias de política...")
    send_politica_to_channel()

def job_get_sports():
    print("Coletando notícias de esportes...")
    send_sports_to_channel()

def job_get_eco():
    print("Coletando notícias de economia...")
    send_eco_to_channel()


schedule.every(1).hours.do(job_get_ab)
schedule.every(1).hours.do(job_get_folha)
schedule.every(1).hours.do(job_get_news)
schedule.every(1).hours.do(job_get_politica)
schedule.every(1).hours.do(job_get_sports)
schedule.every(2).hours.do(job_get_eco)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)

