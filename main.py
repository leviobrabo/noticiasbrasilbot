import threading
import g1
import sports_ge
import veja_eco
import politica_uol
import folha
import agenciabrasil

# Função para buscar e enviar notícias
def send_news():
    while True:
        g1.send_news_to_channel()

# Função para buscar e enviar notícias de esportes
def send_sports():
    while True:
        sports_ge.send_sports_to_channel()

def send_eco():
    while True:
        veja_eco.send_eco_to_channel()

def send_politica():
    while True:
        politica_uol.send_politica_to_channel()

def send_folha():
    while True:
        folha.send_folha_to_channel()

def send_ab():
    while True:
        agenciabrasil.send_ab_to_channel()
        
        

# Crie duas threads para executar as funções
thread_news = threading.Thread(target=send_news)
thread_sports = threading.Thread(target=send_sports)
thread_eco = threading.Thread(target=send_eco)
thread_politica = threading.Thread(target=send_politica)
thread_folha = threading.Thread(target=send_folha)
thread_ab = threading.Thread(target=send_ab)

# Inicie as threads
thread_news.start()
thread_sports.start()
thread_eco.start()
thread_politica.start()
thread_folha.start()
thread_ab.start()

# Aguarde as threads terminarem (ou interrompa manualmente)
thread_news.join()
thread_sports.join()
thread_eco.join()
thread_politica.join()
thread_folha.join()
thread_ab.join('')
