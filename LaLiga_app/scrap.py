import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlmodel import Field, Session, SQLModel, create_engine, select

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
}

###################################################################################################################################################################################
###                     get info de jugadores

def transform_altura(altura):
    altura = altura.split("\xa0")
    new_alt = altura[0].replace(',', '.')
    return new_alt + ' ' + 'm'


def get_player_url(player):
    data=requests.get("https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={}&x=0&y=0".format(player), headers=headers) 

    soup = BeautifulSoup(data.text, features='lxml')

    table = soup.find("table", { "class" : "items" })
    #print(table)
    row = table.find("td", { "class" : "hauptlink" })
    hrefs = row.find("a")
    url = hrefs['href']
    return 'https://www.transfermarkt.es' + url


def get_player_info(name):
    player_url = get_player_url(name)
    "Conseguimos primero estadísticas del jugador"
    aux = []
    indices = [0,1,4,6]
    data=requests.get(player_url, headers=headers)
    soup = BeautifulSoup(data.text, features='lxml')
    div = soup.find("div", { "class" : "info-table" })
    
    for row in div.find_all("span", {"class": "info-table__content info-table__content--bold"}):
        txt = row.text.strip()
        aux.append(txt)
    
    ##Check if name is given by Transfermarkt
    if '/' in aux[0]:
        aux = [name] + aux
        
    res = [aux[index] for index in indices]
    res[2] = transform_altura(res[2])
    
    d = {'nombre': res[0], 'birthdate': res[1], 'altura': res[2], 'posicion': res[3]}
    return d


###################################################################################################################################################################################

###                         GET INFO LIGA (Nombre jugadores)



def get_liga():
    columns = ['posicion', 'club', 'partidos', 'ganados', 'empates', 'perdidos', 'goles', 'diferencia', 'puntos']
    players = {'nombre':[], 'valor':[], 'club':[]}
    res = []
    data=requests.get('https://www.transfermarkt.es/laliga/tabelle/wettbewerb/ES1?saison_id=2021', headers=headers) 
    soup = BeautifulSoup(data.text, features='lxml')
    table = soup.find("div", { "class" : "responsive-table" })
    tbody = table.find("tbody")
    for row in tbody.find_all("tr"):
        aux = []
        for data in row.find_all("td"):
            if 'no-border-rechts' in data['class']:
                a = data.find("a")
                team_id = a['href'].split('verein')[1].split('/')[1] # Get team id for getting further info
                team_stats, player_names = get_info_teams(team_id)
                players['nombre'].extend(player_names['nombre'])
                players['valor'].extend(player_names['valor'])
                continue

            aux.append(data.text.strip())
    
        
        dic = {k:v for k,v in zip(columns, aux)}
        dic.update(team_stats)
        res.append(dic)
        
        players['club'].extend([dic['club']] * len(players['nombre']))
        
    return res, players

def get_playernames(soup):
    dic = {'nombre':[], 'valor':[]}
    table = soup.find("table", { "class" : "items" })
    tbody = table.find("tbody")
    for data in tbody.find_all("td", {"class": "hauptlink"}):
        txt = data.text.strip()
        if ',' in txt:
            dic['valor'].append(txt)
        else:
            dic['nombre'].append(txt)
    return dic

def get_info_teams(team_id):
    columns = ['jugadores', 'edad_media', 'extranjeros', 'internacionales', 'estadio', 'asientos', 'balance']
    url = f'https://www.transfermarkt.es/fc-valencia/kader/verein/{team_id}/saison_id/2021'
    data=requests.get(url, headers=headers) 
    soup = BeautifulSoup(data.text, features='lxml')
    
    player_names = get_playernames(soup)
    
    table = soup.find("div", { "class" : "dataContent" })
    
    aux = []
    for datadaten in table.find_all("div", { "class" : "dataDaten" }):
        for info, row in zip(datadaten.find_all("span", { "class" : "dataItem" }), datadaten.find_all("span", { "class" : "dataValue" })):
            if info.text.strip() == 'Extranjeros:':
                aux.append(row.text.strip().split("\xa0")[0])
            elif info.text.strip() == 'Estadio:':
                info_estadio =  row.text.strip().split("\xa0")
                aux.append(info_estadio[0])
                aux.append(info_estadio[2].split(' ')[0])
            else:
                aux.append(row.text.strip())
    dic = {k:v for k,v in zip(columns, aux)}
    
    
    
    return dic, player_names


###################################################################################################################################################################################
###                         GET INFO PLAYER STATS LIGA 22

def check_gk(soup):
    for value in soup.find_all("span", { "class" : "dataValue"}):
        value = value.text.strip()
        if value == 'Portero':
            return True
    return False

def get_stats_dic(player_url):    
    player_code = player_url.split('/')[-1]
    stats_url = f'https://www.transfermarkt.es/e/leistungsdatendetails/spieler/{player_code}/saison//verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1'
    data=requests.get(stats_url, headers=headers)
    soup = BeautifulSoup(data.text, features='lxml')
    
    if check_gk(soup):
        dic = {"temporada":[], "competicion":[],"club":[],"partidos_equipo":[], "partidos_jugados":[], "puntos_por_partido":[], "goles":[],
            "goles_en_propia":[], "entradas_desde_banquillo":[], "sustituciones":[], "amarillas":[], "dobles_amarillas":[], "rojas":[], 
           "goles_en_contra": [], "partidos_imbatido": [], "minutos_jugados": [],}
        
    else:
        dic = {"temporada":[], "competicion":[],"club":[],"partidos_equipo":[], "partidos_jugados":[], "puntos_por_partido":[], "goles":[],
           "Asistencias":[], "goles_en_propia":[], "entradas_desde_banquillo":[], "sustituciones":[], "amarillas":[], "dobles_amarillas":[], "rojas":[], "penaltis_anotados":[], 
           "minutos_por_gol":[], "minutos_jugados":[]}
    table = soup.find("table", { "class" : "items" })

    table_body = table.find("tbody")
    for row in table_body.find_all('tr'):
        for cell,key in zip(row.find_all('td',{ "class" : ["zentriert","no-border-links" ,"rechts"] }), dic.keys()):
            if len(cell['class']) > 2: #Buscamos la clase hauptlink no-border-rechts zentriert
                dic[key].append(cell.a['title'].strip())
            else:
                dic[key].append(cell.text.strip())
        s = set(dic['temporada'])
        if len(s)==2:
            break
    return dic

def get_player_stats(name):
    url = get_player_url(name)
    d = get_stats_dic(url)
    df = pd.DataFrame.from_dict(d)
    cols = df.columns
    df.drop(columns=['puntos_por_partido'], inplace=True)
    df.drop(df.tail(1).index,inplace=True)
    df.replace('-', '0', inplace=True)
    df['nombre_jugador'] = [name] * len(df['temporada'])
    
    if 'minutos_por_gol' in cols:
        df['minutos_por_gol'] = df['minutos_por_gol'].map(lambda x: x.replace("'", '').replace(".", ''))
    df['minutos_jugados'] = df['minutos_jugados'].map(lambda x: x.replace("'", '').replace(".", ''))
    return df[df['competicion'] == 'LaLiga']
