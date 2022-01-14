import json
import random
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
import itertools
import time
import sys
from collections import defaultdict

def closest_distance(client:str, matrix:dict, clients_list:list):
    client_matrix = matrix[str(client)]['destinations']
    min_distance = min(client_matrix.items(), key = lambda x: x[1]['distance(km)'] 
                                                            if x[0] in clients_list 
                                                            else 1000)
    return min_distance

def closest_time(client:str, matrix:dict, clients_list:list):
    client_matrix = matrix[str(client)]['destinations']
    min_distance = min(client_matrix.items(), key = lambda x: x[1]['time(min)']
                                                            if x[0] in clients_list 
                                                            else 1000)
    return min_distance

def data_sample(matrix:dict, client_sample:int) -> list:
    C = list()
    do_science = True
    c_list = [key for key in matrix.keys() 
                if matrix[key]['type'] == 'client']
    while do_science:
        c_length = len(C)
        rand_client = random.choice(c_list)
        if rand_client not in C and c_length <= client_sample:
            C.append(rand_client) 
        if c_length == client_sample:  
            do_science = False        
    return C

def plot_main(data_json:dict,dist_matrix:dict,clients:int):
    clients = data_sample(dist_matrix,clients)
    for c in clients:
        plt.scatter(data_json[int(c)]['long'], data_json[int(c)]['lat'], marker='o', color='black')
    visited = list()
    tour_length = 0
    do_magic = True
    temp_clients = clients.copy()
    first_client = random.choice(temp_clients)
    visited.append(first_client)
    temp_clients.remove(first_client) 
    to_visit = closest_distance(first_client, dist_matrix, temp_clients)
    counter = 0
    while do_magic:
        plt.title('Nearest neighbour heuristic')
        if len(visited) < 2:
            plt.plot([data_json[int(first_client)]['long'], data_json[int(to_visit[0])]['long']],
                    [data_json[int(first_client)]['lat'], data_json[int(to_visit[0])]['lat']],
                    'b--')
            from_client = to_visit[0] #client already visited, new starting point
            temp_clients.remove(from_client) 
            visited.append(from_client)
            tour_length += to_visit[1]['distance(km)']
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
        else: 
            plt.plot([data_json[int(from_client)]['long'], data_json[int(to_visit[0])]['long']],
                    [data_json[int(from_client)]['lat'], data_json[int(to_visit[0])]['lat']],
                    'b--')
            visited.append(to_visit[0])
            from_client = to_visit[0]
            temp_clients.remove(from_client) 
            tour_length += to_visit[1]['distance(km)']
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
            if len(temp_clients) == 0:
                plt.plot([data_json[int(from_client)]['long'], data_json[int(first_client)]['long']],
                    [data_json[int(from_client)]['lat'], data_json[int(first_client)]['lat']],
                    'b--')
                do_magic = False 
        counter = counter + 1 
    plt.show()

def main(dist_matrix:dict,clients:int):
    clients = data_sample(dist_matrix, clients)
    visited = list()
    tour_length = 0
    do_magic = True
    temp_clients = clients.copy()
    first_client = random.choice(temp_clients)
    visited.append(first_client)
    temp_clients.remove(first_client) 
    to_visit = closest_distance(first_client, dist_matrix, temp_clients)
    counter = 0
    while do_magic:
        if len(visited) < 2:
            from_client = to_visit[0] #client already visited, new starting point
            temp_clients.remove(from_client) 
            visited.append(from_client)
            tour_length += to_visit[1]['distance(km)']
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
        else: 
            visited.append(to_visit[0])
            from_client = to_visit[0]
            temp_clients.remove(from_client) 
            tour_length += to_visit[1]['distance(km)']
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
            if len(temp_clients) == 0:
                do_magic = False 
        counter = counter + 1 
    return visited, tour_length

def clusters(dist_matrix:dict,tour:list):
    visited = list()
    id_visited = list()
    do_magic = True
    temp_clients = tour.copy()
    first_client = temp_clients[0]
    visited.append(first_client)
    id_visited.append(dist_matrix[str(first_client)]['id'])
    temp_clients.remove(first_client) 
    to_visit = closest_distance(first_client, dist_matrix, temp_clients)
    while do_magic:
        if len(visited) < 2:
            from_client = to_visit[0] #client already visited, new starting point
            temp_clients.remove(from_client) 
            visited.append(from_client)
            id_visited.append(dist_matrix[str(from_client)]['id'])
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
        else: 
            visited.append(to_visit[0])
            id_visited.append(dist_matrix[str(to_visit[0])]['id'])
            from_client = to_visit[0]
            temp_clients.remove(from_client) 
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
            if len(temp_clients) == 0:
                do_magic = False 
    return visited, id_visited

if __name__=='__main__':
    
    data_path = {'tul': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/problem_set.json',
                'home': 'E:/Main User/Documents/Repositories/VRP/Data/problem_set.json'}
    distance_matrix_path = {'tul':'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/distance_matrix_all_nodes.json',
                            'home':'E:/Main User/Documents/Repositories/VRP/Data/distance_matrix_all_nodes.json'}
    place = 'tul'
    print('hello nn heuristic')
                    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            

    