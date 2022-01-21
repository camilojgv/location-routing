import json
from turtle import distance
import nearest_neighbour
import numpy as np
import time
import sys
import pandas as pd

def first_to_last(tour:list):
    swap_node = tour[0]
    tour.pop(0)
    tour.append(swap_node)
    return tour

def get_client_set(clients:list):
    new_clients = list()
    for c in clients:
        if c['point_type'] == 'client':
            new_clients.append(c)
    return new_clients 

def tour_length(tour:list,dist_matrix:dict):
    t_lenght = 0
    arcs = list()
    for index, node in enumerate(tour):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour[index-1]
            t_lenght += dist_matrix[str(previous_node)]["destinations"][str(node)]["distance(km)"]
            arcs.append(dist_matrix[str(previous_node)]["destinations"][str(node)]["distance(km)"])
    return t_lenght, arcs

def tour_duration(tour:list,dist_matrix:dict):
    t_duration = 0
    arcs = list()
    service = np.squeeze(np.random.normal(35,10,1))
    for index, node in enumerate(tour):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour[index-1]
            t_duration += round(dist_matrix[str(previous_node)]["destinations"][str(node)]["time(min)"] + service,1)
            arcs.append(round(dist_matrix[str(previous_node)]["destinations"][str(node)]["time(min)"] + service, 1))
    return t_duration, arcs

def tour_weight(tour:list,clients:object):
    t_weight = 0
    arcs = list()
    for index, node in enumerate(tour):
        weight = clients.iloc[int(node)]
        weight = weight['KG_DEMAND']
        t_weight += round(weight)
        arcs.append(round(weight))
    return t_weight, arcs

def one_clust(nodes_json, dist_matrix, clients, params):
    np.random.seed()
    tour, lenght = nearest_neighbour.main(dist_matrix, params['client_sample'])
    nearest_neighbour.plot_main(nodes_json, dist_matrix, params['client_sample'])
    initial_tour = tour.copy()
    #clustering pointers
    #group into routes
    #No route can be longer than 8 hours
    
    clusters = dict()
    route = list()
    id_route = list()
    r = 0
    route_duration = 0
    route_distance = 0
    service = np.squeeze(np.random.normal(35,10,1))
    for i,node in enumerate(tour):
        weight = clients[ clients['ID'] == dist_matrix[tour[i]]['id'] ]
        if i>0:
            route_duration += dist_matrix[str(tour[i-1])]['destinations'][str(tour[i])]['time(min)'] + service
            route_distance += dist_matrix[str(tour[i-1])]['destinations'][str(tour[i])]['distance(km)']
            route_weight += float(np.squeeze(weight['KG_DEMAND'].values))
            if route_duration < params['max_duration'] and route_weight < params['max_weight']:
                route.append(node) 
                id_route.append(str(dist_matrix[tour[i]]['id']))
            elif (route_duration >= params['max_duration'] or route_weight >= params['max_weight']) or node == tour[len(tour)-1]:
                clusters[str(r)] = {'route': route,
                                    'id_route': id_route,
                                    'duration': round(route_duration,3),
                                    'distance': round(route_distance),
                                    'weight': route_weight} 
                route, id_route = list(), list()
                route_duration, route_weight, route_distance = 0, 0, 0
                r+=1
                route.append(node)
                
        else:
            route.append(node)
            id_route.append(str(dist_matrix[tour[i]]['id']))
            route_weight = float(np.squeeze(weight['KG_DEMAND'].values))
    return clusters   
    
def main_clust(dist_matrix, clients, params): 
    tour, lenght = nearest_neighbour.main(dist_matrix, params['client_sample'])
    #clustering pointers
    #group into routes
    #No route can be longer than 8 hours
    clusters, route, id_route = dict(), list(), list()
    r = 0
    initial_tour = tour.copy()
    route_duration, route_distance, route_weight = 0, 0, 0
    n_clusts = 0
    np.random.seed()
    service = np.squeeze(np.random.normal(35,10,1))
    #run through a loop
    clusters[n_clusts] = dict()
    for i,node in enumerate(tour):
        weight = clients[ clients['ID'] == dist_matrix[tour[i]]['id'] ]
        if i>0:
            route_duration += dist_matrix[str(tour[i-1])]['destinations'][str(tour[i])]['time(min)'] + service
            route_distance += dist_matrix[str(tour[i-1])]['destinations'][str(tour[i])]['distance(km)']
            route_weight += float(np.squeeze(weight['KG_DEMAND'].values))
            if route_duration < params['max_duration'] and route_weight < params['max_weight']:
                route.append(node) 
                id_route.append(str(int(dist_matrix[tour[i]]['id'])))
            elif (route_duration >= params['max_duration'] or route_weight >= params['max_weight']) or node == tour[len(tour)-1]:
                clusters[n_clusts][r] = {'route': route,
                                        'id_route': id_route,
                                        'duration':round(route_duration,3),
                                        'distance': round(route_distance),
                                        'weight': route_weight} 
                route, id_route = list(), list()
                route_duration, route_weight, route_distance = 0, 0, 0
                r+=1
                route.append(node)
                id_route.append(str(int(dist_matrix[tour[i]]['id'])))
        else:
            route.append(node)
            id_route.append(str(dist_matrix[tour[i]]['id']))
            route_weight = float(np.squeeze(weight['KG_DEMAND'].values))
    #Now, lets create a new tour, starting from i = 1 and ending in i = 0
    #Swap positions -> first to last
    tour = first_to_last(tour)
    #swap until tours are equal again
    #while initial_tour != tour:
    while n_clusts < len(tour)-1:
        r = 0
        n_clusts += 1
        clusters[n_clusts] = dict()
        for i,node in enumerate(tour):
            if i>0:
                route_duration += dist_matrix[str(tour[i-1])]['destinations'][str(tour[i])]['time(min)'] + service
                route_distance += dist_matrix[str(tour[i-1])]['destinations'][str(tour[i])]['distance(km)']
                route_weight += float(np.squeeze(weight['KG_DEMAND'].values))
                if route_duration < params['max_duration'] and route_weight < params['max_weight']:
                    route.append(node) 
                    id_route.append(str(int(dist_matrix[tour[i]]['id'])))
                elif (route_duration >= params['max_duration'] or route_weight >= params['max_weight']) or node == tour[len(tour)-1]:
                    clusters[n_clusts][r] = {'route': route, 
                                            'id_route': id_route,
                                            'duration': round(route_duration,3),
                                            'distance': round(route_distance),
                                            'weight': route_weight}
                    route, id_route = list(), list()
                    route_duration, route_weight, route_distance = 0, 0, 0
                    r+=1
                    route.append(node)
            else:
                route.append(node)
                id_route.append(str(int(dist_matrix[tour[i]]['id'])))
                route_weight = float(np.squeeze(weight['KG_DEMAND'].values))
        tour = first_to_last(tour)
    return clusters

def main(dist_matrix, clients, params):
    main_dict = dict()
    clusts = main_clust(dist_matrix, clients, params)
    for key,value in clusts.items():
        main_dict[key] = dict()
        for routes in value.keys():
            tour, id_tour = nearest_neighbour.clusters(dist_matrix, clusts[key][routes]['route'])
            new_length, dist_arcs = tour_length(tour, dist_matrix)
            new_duration, time_arcs = tour_duration(tour, dist_matrix)
            new_weight, weight_arcs = tour_weight(tour, clients)
            main_dict[key][routes] = {'route': tour, 
                                    'id_route': id_tour,
                                    'duration': round(new_duration, 3),
                                    'distance': round(new_length, 3),
                                    'weight': new_weight,
                                    'duration_arcs': time_arcs,
                                    'distance_arcs': dist_arcs,
                                    'weight_demands': weight_arcs}
    return main_dict

if __name__ == '__main__':
    print('clustering module')
    instances = [(20,5),(50,5),(50,10), 
                (100,5),(100,10),(100,20),
                (150,10),(150,20),(200,10),
                (200,20),(300,10),(500,10), 
                (700,10),(860,10),(300,20), 
                (500,20),(700,20),(860,20),
                (300,35),(500,35),(700,35),
                (860,35)]
    
    dm = open('Data/distance_matrix.json')
    distance_matrix = json.load(dm)
    print('\tdistance matrix -> ok\n')
    warehouses = pd.read_csv('Data/potential_warehouses.csv')
    print('\twarehouses -> ok\n')
    clients = pd.read_csv('Data/client_hardwares.csv')
    print('\tclients -> ok\n')
    for (c,w) in instances:
        params = {'client_sample': c,
                    'warehouse_sample': w,
                    'max_distance': 25,
                    'max_duration': 8*60, 
                    'max_weight': 8000}
        print('instance -> \n\tclients -> {}\n\twarehouses -> {}'.format(c,w))
        clusters = main(distance_matrix, clients, params)
        np.save('tsp_clusters/instance_c{}_w{}.npy'.format(c,w), clusters)
    
    

    
