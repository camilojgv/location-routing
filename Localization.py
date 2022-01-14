# -*- coding: utf-8 -*-
"""
Localización de Bodegas en Mexico
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import math
import random
import requests
from shapely.geometry import Polygon, Point

# =============================================================================
# Recolección de información
# =============================================================================

CDMX = pd.read_csv('E:\Main User\Documents\Repositories\Hub location\cdmx.csv', sep = ";", encoding = 'latin-1', index_col = 'id').to_dict(orient='index')
EMX1 = pd.read_csv('E:\Main User\Documents\Repositories\Hub location\edomx.csv', sep = ";", encoding = 'latin-1', index_col = 'id').to_dict(orient='index')
EMX2 = pd.read_csv('E:\Main User\Documents\Repositories\Hub location\edomx2.csv', sep = ";", encoding = 'latin-1', index_col = 'id').to_dict(orient='index')

actividades = {"Comercio al por mayor de materiales metálicos para la construcción y la manufactura": 3,
                "Comercio al por mayor de otros materiales para la construcción, excepto de madera y metálicos": 3,
                "Comercio al por mayor de pintura": 3,
                "Comercio al por menor de artículos para albercas y otros artículos": 1,
                "Comercio al por menor de materiales para la construcción en tiendas de autoservicio especializadas": 1,
                "Comercio al por menor de pintura": 5,
                "Comercio al por menor en ferreterías y tlapalerías": 5}
municipios = ["Acolman",
                "Álvaro Obregón",
                "Atenco",
                "Atizapán de Zaragoza",
                "Azcapotzalco",
                "Benito Juárez",
                "Chalco",
                "Chicoloapan",
                "Chimalhuacán",
                "Coacalco de Berriozábal",
                "Coyoacán",
                "Cuauhtémoc",
                "Cuajimalpa de Morelos",
                "Cuautitlán",
                "Cuautitlán Izcalli",
                "Ecatepec de Morelos",
                "Gustavo A. Madero",
                "Ixtapaluca",
                "Iztacalco",
                "Iztapalapa",
                "La Magdalena Contreras",
                "La Paz",
                "Miguel Hidalgo",
                "Naucalpan de Juárez",
                "Nezahualcóyotl",
                "Álvaro Obregón",
                "Tecámac",
                "Texcoco",
                "Tezoyuca",
                "Tláhuac",
                "Tlalpan",
                "Tlalnepantla de Baz",
                "Tultepec",
                "Tultitlán",
                "Venustiano Carranza",
                "Nicolás Romero",
                "Xochimilco",]

data = {}

for i in [CDMX, EMX1, EMX2]:
    for j in i:
        if (i[j]['nombre_act'] in actividades.keys() and i[j]['municipio'] in municipios and i[j]['longitud']>-100):
                      
            data[j] = i[j]
            
df = pd.DataFrame.from_dict(data, orient = 'index')
df.to_csv('dataF.csv')

# Plot MAP
x = [data[i]['longitud'] for i in data]
y = [data[i]['latitud'] for i in data]
plt.scatter(x,y)

# Encontrar los mejores puntos para poner bodegas. Dado que ya existe una bodega.
def linearDistance(a:list, b:list, vel:float=12)-> tuple:
    
    # approximate radius of earth in km
    R = 6373.0
    lat1 = math.radians(a[0])
    lon1 = math.radians(a[1])
    lat2 = math.radians(b[0])
    lon2 = math.radians(b[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c         # Distance in km
    
    return distance

def objective(bodegas: list, data:dict):
    
    cost = 0
    for i in data:
        destination = [data[i]['latitud'], data[i]['longitud']]
        minCost = min([linearDistance(origin,destination) for origin in bodegas])
        cost += minCost
        
    return cost

# Todos los puntos pueden ser bodegas.
minCost = float('inf')
minBodegas = []

count = 0


posibilities = random.choices(list(data.items()), k=100)
posibilities = { i[0]: i[1] for i in posibilities }
x = [posibilities[i]['longitud'] for i in posibilities]
y = [posibilities[i]['latitud'] for i in posibilities]
plt.scatter(x,y)
plt.show()
n = len(posibilities)*len(posibilities)

df2 = pd.DataFrame.from_dict(posibilities, orient = 'index')
df2.to_csv('posibilitiesWH.csv')

for i in posibilities:
    for j in posibilities:
        bod1 = [data[i]['latitud'], data[i]['longitud']]
        bod2 = [data[j]['latitud'], data[j]['longitud']]
        bodegasTest = [[19.5653203,-99.2016332], bod1, bod2]      
        
        testCost = objective(bodegasTest, data)
        
        if testCost < minCost:
            minCost = testCost
            minBodegas = bodegasTest
    
        count+=1
        
        if count%100 == 0:
            print('iteracion ', count,  ' de ', n)
            
         
x = [data[i]['longitud'] for i in data]
y = [data[i]['latitud'] for i in data]
plt.scatter(x,y)

x = [posibilities[i]['longitud'] for i in posibilities]
y = [posibilities[i]['latitud'] for i in posibilities]
plt.scatter(x,y)

bestsX = [ i[1] for i in minBodegas]
bestsY = [ i[0] for i in minBodegas]
plt.scatter(bestsX, bestsY)
plt.show()
            
# Se crea la función que genera poligonos de cobertura a partir de coordenadas
def isolineGeneration(lat:float, lng: float, cov_type: str, value: float):
    
    coordinates = 'geo!' + str(lat) + ',' + str(lng)
    api_structure = 'https://isoline.route.ls.hereapi.com/routing/7.2/calculateisoline.json'
    payload = {
    		'apiKey' : 'A6oKk5QyLYkxJ4efaUoDQZjjRNQ2bibTpYA2SE0oxiM',
    		'start' : coordinates,
            'range': value,
            'rangetype':cov_type,
            'mode': 'shortest;car;traffic:disabled'
        }
    response=requests.get(api_structure, params=payload)
    response=response.json()
    polygon = response['response']['isoline'][0]['component'][0]['shape']
    
    listPoints = []
    for i in polygon:
        coors = i.split(",")
        listPoints.append([ float(coors[1]), float(coors[0])])
    
    return listPoints

"""
Procedimiento que borra los puntos que no se encuentran dentro de la cobertura de la bodega
"""
def inside(polygon, lat: float, lng: float):
    
    testPoint = Point(lng,lat) # Los poligonos están en lng, lat
    polTest = Polygon(polygon)
    
    # Si el punto está en la cobertura no pasa nada, de lo contrario se borra
    if polTest.contains(testPoint):
        return True
    else:
        return False

# Se crean los poligonos de cobertura de 18km en carro y se verifican que clientes están dentro
bodegasDef = {str(i):{} for i in minBodegas}

for i in minBodegas:
    bodegasDef[str(i)]['polygon'] = isolineGeneration(i[0], i[1], 'distance', 18000)
    
# Se crea un archivo json con los poligonos para graficarlos
jsonOut = {"type": "FeatureCollection", "name": "Homecenters Bogota", "features": []}

for i in bodegasDef:
    jsonOut['features'].append({"type": "Feature", 
                                "properties": {"name": i},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [bodegasDef[i]['polygon']]
                                }})

with open('WH2_Polygons.json', 'w') as fp:
    json.dump(jsonOut, fp)
        

            
        
