import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import time
import nearest_neighbour
import clustering
import os

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

def get_routes(clusters, n_iter, depot_routes, dist_matrix):
    routes = clusters[n_iter]
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
        r_dict[(w,r)] = {'ids':ids, 
                        'distance':tour_length,
                        'time':tour_duration,
                        'weight':tour_weight}
    return r_dict

def get_coordinates(client_id:int, clients:list):
    c_dict = [value for key,value in clients.items() if value['id'] == client_id]
    return c_dict[0]

def plot_open_depots(open_w, warehouses):
    for key,value in warehouses.items():
        if key in open_w:
            plt.scatter(value['long'], value['lat'], marker='^', color='red')
        else:
            plt.scatter(value['long'], value['lat'], marker='o', color='white')
    plt.show()

def scatter_cr(route_clients:list, clients:dict, col:str):
    for rc in route_clients[1:len(route_clients)-2]:
        client = get_coordinates(rc,clients)
        plt.scatter(client['long'], client['lat'], marker='.', color=col)

def plot_client_coverage(open_w, warehouses, routes, clients):
    colors = ['black','green','purple','orange']
    counter = 0
    for ow in open_w:
        plt.scatter(warehouses[ow]['long'], warehouses[ow]['lat'], marker='D', color='red')
        #plot routes that start from the depot
        depot_routes = [r for (w,r) in routes.keys() if w == ow]
        for dr in depot_routes:
            route_clients = routes[(ow,dr)]['ids']
            scatter_cr(route_clients, clients, colors[counter])
        counter += 1
    plt.show()
   
def tour_length(tour:list,dist_matrix:dict) -> int:
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

def tour_duration(tour:list,dist_matrix:dict) -> int:
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
    return t_duration, arcs

def get_lists(vars:dict):
    od = [i for ((var_type,i),value) in vars.items() if var_type == 'y' and int(value) == 1]
    dr = [(key[0],key[1]) for (var_type,key),value in vars.items() if var_type == 'x' and int(value) == 1]
    return od, dr

if __name__=='__main__':
    start_time = time.time()
    ins = (860,35)
    print('get results hybrid algorithm\n')
    fl_model = np.load('optimization_results/flp_results_rcopt_c{}_w{}.npy'.format(ins[0],ins[1]),allow_pickle='TRUE').item()
    print('get other information, warehouses, clients, routes\n')
    
    clusters_path = np.load('tsp_clusters/instance_c{}_w{}.npy'.format(ins[0],ins[1]),allow_pickle='TRUE').item()
    distance_matrix = json.load(open( 'Data/distance_matrix.json'))
    warehouses = get_warehouses('Data/potential_warehouses.csv')
    print('\twarehouses -> ok\n')
    clients = get_clients('Data/client_hardwares.csv')
    print('\tclients -> ok\n')
    open_depots, depot_routes = get_lists(fl_model['variables'])
    routes = get_routes(clusters_path, fl_model['iteration'], depot_routes, distance_matrix)
    print('\troutes -> ok\n')
    
    #plot_open_depots(open_depots, warehouses)
    plot_client_coverage(open_depots, warehouses, routes, clients)
    summarize_dict = dict()
    for od in open_depots:
        summarize_dict[od] = {'avg_distance': np.mean([routes[(w,r)]['distance'] for (w,r) in routes.keys() if w == od]),
                                'avg_weight': np.mean([routes[(w,r)]['weight'] for (w,r) in routes.keys() if w == od]),
                                'avg_time': np.mean([routes[(w,r)]['time'] for (w,r) in routes.keys() if w == od])}
    print('lets go, execution time -> {}'.format(time.time()-start_time)) 