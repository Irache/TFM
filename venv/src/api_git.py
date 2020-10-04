#Autor: Irache Garamendi - 2020
import requests
import time
import pymongo
from pymongo import MongoClient
import configparser
import requests
import json 

file_ini = "..\\file\\conf.ini"
config = configparser.ConfigParser()
config.read(file_ini)


'client = pymongo.MongoClient("mongodb+srv://UserAct1:<password>@clustervehiculosv0.6kutv.azure.mongodb.net/<dbname>?retryWrites=true&w=majority")'
'db = client.test'
DB_NAME = config['mongo']['DB_NAME']
COLLECTION_REPOS = config['mongo']['COLLECTION_REPOS']
COLLECTION_COMMITS = config['mongo']['COLLECTION_COMMITS']
COLLECTION_COMMITS_INFO = config['mongo']['COLLECTION_COMMITS_INFO']

username = config['github']['client_id']
client_secret = config['github']['client_secret']
data_File = "..\\file\\request_git.json"

####
# inputs
# Autenticación Token de OAuth (enviado en un encabezado)
####
#Llamada que devuelve el límite
def checkRateLimit():
    #consultar el tiempo máximo en el que se puede realizar el número máximo de peticiones
    url = 'https://api.github.com/rate_limit'
    query = {'client_id': username, 'client_secret' : client_secret}
    r = requests.get(url, params=query)
    rate_limit = r.json()
    remaining = rate_limit['resources']['core']['remaining']
    print('Request remaining: ' + str(remaining))
    return remaining

#Búsqueda en el repositorio github
def find_in_repository():
    #Búsqueda en git dentro de los repositorios por palabras con sonarcloud
    #salida json
    #autenticación básica
    remaining = checkRateLimit()
    if remaining < 60:
        print('\n\n\nWaiting for rate limit....\n\n')
        time.sleep(70)
    url = "https://api.github.com/search/repositories"
    querystring = {"q": "sonarcloud in:readme"}

    headers = {
        'authorization': "Basic Z2FyYW1lbmRpLmlyYWNoZUBnbWFpbC5jb206aXJhY2hlMTk4MA==",
        'cache-control': "no-cache",
        'postman-token': "72c78d9c-c7de-9e4d-4825-f7bbaeb8411e"
}
    response = requests.request("GET", url, headers=headers, params=querystring)
    repositoryGit_dict = response.json()
    #Extract data
    # extract, create and insert a dict with project information
    #print("find_in_repository: ")
    #print(response.text)
    return repositoryGit_dict

#Crear fichero json e insertar en mong
def CreateFileJson(reponseJson):
    connection = pymongo.MongoClient('localhost', 27017)
    dbname = connection[DB_NAME]
    repos = connection[DB_NAME][COLLECTION_REPOS]
    name_file_output_json = "..\\file\\response_git.json"
    f = open(name_file_output_json, "r")
    with open(name_file_output_json, 'w') as file:
        result = json.dump(reponseJson, file)
        for valorKey in reponseJson:
            valor = reponseJson[valorKey]
            #print(valor)
            #items es una lista de dict
            if valorKey =='items':
                d = valor
                print("CreateFileJson: ")
                print(valor)
                #"Recorrer lista por Indices"
                for x in range(0, len(valor)):
                    # dato_instantaneo es dict
                    dato_instantaneo = valor[x]
                    try:
                        dbname.repos.insert_one(dato_instantaneo)
                    except pymongo.errors.BulkWriteError:
                        print('BulkWriteError\n')

def main():
    #buscar en repositorio github
    reponseJson = find_in_repository();
    #crear fichero e insertanr en mongo
    CreateFileJson(reponseJson);

    print('\n\nEnd of program!')

main()



