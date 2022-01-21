#Modified granular tabu search
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
import clustering
from collections import defaultdict

def tour_length(tour:list,dist_matrix:dict) -> float:
    t_lenght = 0
    arcs = list()
    for index, node in enumerate(tour):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour[index-1]
            t_lenght += dist_matrix[str(previous_node)]["destinations"][str(node)]["distance(km)"]
    return t_lenght

def tour_duration(tour:list,dist_matrix:dict) -> float:
    t_duration = 0
    arcs = list()
    for index, node in enumerate(tour):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour[index-1]
            t_duration += dist_matrix[str(previous_node)]["destinations"][str(node)]["time(min)"]
            arcs.append(dist_matrix[str(previous_node)]["destinations"][str(node)]["time(min)"])
    return t_duration

def get_clients(hardware_stores_path):
    clients = pd.read_csv(hardware_stores_path)
    clients.columns = ['lat', 'long', 'id', 'total_deliveries', 'kg_demand']
    c_dict = clients.to_dict(orient='index')
    return c_dict

def get_warehouses(warehouse_path):
    warehouses = pd.read_csv(warehouse_path)
    warehouses.columns = ['lat', 'long', 'cost', 'area', 'own','weight']
    warehouses.filter(items=['lat', 'long', 'cost', 'area', 'own'])
    w_dict = warehouses.to_dict(orient='index')
    return  w_dict

def get_routes(clusters, n_iter, depot_routes,dist_matrix):
    routes = clusters[int(n_iter)]
    r_dict = dict()
    for (w,r) in depot_routes:
        temp = [int(g) for g in routes[r]['route']]
        temp = [w] + temp
        temp.append(w)
        ids = [int(g) for g in routes[r]['id_route']]
        ids = [w] + ids
        ids.append(w)
        tour_length, dist_arc = clustering.tour_length(temp, dist_matrix)
        tour_duration, time_arc = clustering.tour_duration(temp, dist_matrix)
        tour_weight = routes[r]['weight']
        r_dict[(w,r)] = {'indexes':temp,
                        'ids':ids, 
                        'distance':tour_length,
                        'time':tour_duration,
                        'weight':tour_weight}
    return r_dict

def get_coordinates(client_id:int, clients:list):
    c_dict = [value for key,value in clients.items() if value['id'] == client_id]
    return c_dict[0]

def get_lists(vars:dict):
    od = [i for ((var_type,i),value) in vars.items() if var_type == 'y' and int(value) == 1]
    dr = [(key[0],key[1]) for (var_type,key),value in vars.items() if var_type == 'x' and int(value) == 1]
    return od, dr

def find_granular_neighbourhoods(beta:float, dist_matrix:dict) -> dict:
    # lets get the five best posible neighbors
    tour_neighbours = dict()
    avg_distance = float()
    for key, value in dist_matrix.items():
        avg_distance =  round(np.mean([in_val['distance(km)'] 
                                for in_key, in_val in value["destinations"].items()
                                if (in_val['type'] != 'warehouse')]),3)
        candidates = {int(c_key):c_value for c_key,c_value in value["destinations"].items() 
                                    if value["destinations"][str(c_key)]['distance(km)'] <= beta*avg_distance}
        tour_neighbours[int(key)] = candidates    
    return tour_neighbours

def swap():
    return 'hello world'

def customer_insertion():
    return 'hello'

def two_exchange(tour_a:list, tour_b:list, dist_matrix:dict, candidates:dict):
    improved = True
    nserted_tabu_arcs = set() #arcs deleted
    removed_tabu_arcs = set() #arcs added
    tabu_counter = defaultdict(int)
    max_tabu_iterations = 18
    sparsification_factor = 1.9
    #threshold = find_granular_neighbourhoods(dist_matrix)
    while improved:
        improved = False
        for a in tour_a[1:len(tour_a)-1]: 
            for b in tour_b[1:len(tour_b)-1]:
                i = tour_a.index(a)
                j = tour_b.index(b)
                current_distance = (dist_matrix[str(tour_a[i-1])]['destinations'][str(tour_a[i])]['distance(km)'] + 
                                    dist_matrix[str(tour_b[j-1])]['destinations'][str(tour_b[j])]['distance(km)'])
                swap_distance = (dist_matrix[str(tour_a[i-1])]['destinations'][str(tour_b[j])]['distance(km)'] + 
                                dist_matrix[str(tour_b[j-1])]['destinations'][str(tour_a[i])]['distance(km)'])
                # Best gain possible is possitive
                arc_gain = current_distance - swap_distance 
                if arc_gain > 0:
                    tour_a, tour_b = swap((tour_a, a), (tour_b, b))
                    improved = True
                    break
                
    return 'hello'

def two_customer_exchange():
    return 'hello'

def main():
     return 'hello'
 
if __name__=='__main__':
    #get the initial solution
    ins = (860,35)
    flp_model = np.load('optimization_results/flp_results_rcopt_c{}_w{}.npy'.format(ins[0],ins[1]),allow_pickle='TRUE').item()
    clusters = np.load('tsp_clusters/instance_c{}_w{}.npy'.format(ins[0],ins[1]),allow_pickle='TRUE').item()
    distance_matrix= json.load(open('Data/distance_matrix.json'))
    warehouses = get_warehouses('Data/potential_warehouses.csv')
    print('\twarehouses -> ok\n')
    clients = get_clients('Data/client_hardwares.csv')
    print('\tclients -> ok\n')
    open_depots, depot_routes = get_lists(flp_model['variables'])
    routes = get_routes(clusters, flp_model['iteration'], depot_routes, distance_matrix)
    print('\troutes -> ok\n')
    granular_neighbours = find_granular_neighbourhoods(1, distance_matrix)
    print('hello world')
    
    
    
    