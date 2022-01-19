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

def get_routes(clusters_path, n_iter, depot_routes,dist_matrix):
    clusters_json = open(clusters_path)
    routes_0 = json.load(clusters_json)
    routes = routes_0[str(n_iter)]
    r_dict = dict()
    for (w,r) in depot_routes:
        temp = [int(g) for g in routes[str(r)]['route']]
        temp = [w] + temp
        temp.append(w)
        ids = [int(g) for g in routes[str(r)]['id_route']]
        ids = [w] + ids
        ids.append(w)
        tour_length, dist_arc = clustering.tour_length(temp, dist_matrix)
        tour_duration, time_arc = clustering.tour_duration(temp, dist_matrix)
        tour_weight = routes[str(r)]['weight']
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

def plot_cr(route_clients:list, clients:dict, col:str):
    for rc in route_clients[1:len(route_clients)-2]:
        client = get_coordinates(rc,clients)
        plt.scatter(client['long'], client['lat'], marker=',', color=col)

def plot_client_routes(open_w, warehouses, routes, clients):
    colors = ['black','green','purple','orange']
    counter = 0
    for ow in open_w:
        plt.scatter(warehouses[ow]['long'], warehouses[ow]['lat'], marker='^', color='red')
        #plot routes that start from the depot
        depot_routes = [r for (w,r) in routes.keys() if w == ow]
        for dr in depot_routes:
            route_clients = routes[(ow,dr)]['ids']
            plot_cr(route_clients, clients, colors[counter])
        counter += 1
            # for i,rc in enumerate(route_clients):
            #     if i == 0:
            #         c_0 = [{'lat': warehouses[ow]['lat'],
            #                 'long': warehouses[ow]['long']}]  
            #         c_1 = get_coordinates(route_clients[i+1],clients)
            #         plt.plot([c_0['long'], c_1['long']],[c_0['lat'], c_1['lat']],'b--')
            #     elif i == (len(route_clients)-2):
            #         c_1 = [{'lat': warehouses[ow]['lat'],
            #                 'long': warehouses[ow]['long']}]  
            #         c_0 = get_coordinates(route_clients[i],clients)
            #         plt.plot([c_0['long'], c_1['long']],[c_0['lat'], c_1['lat']],'b--')
            #     else:
            #         c_0 = get_coordinates(route_clients[i], clients)
            #         c_1 = get_coordinates(route_clients[i+1], clients)
            #         plt.plot([c_0['long'], c_1['long']],[c_0['lat'], c_1['lat']],'b--')
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
 
    print('get results from FL problem\n')
    fl_model = np.load('optimization_results/flp_results_rcopt_c860_w35.npy',allow_pickle='TRUE').item()
    print('get other information, warehouses, clients, routes\n')
    warehouse_path = 'Data/potential_warehouses.csv'
    hardware_stores_path = 'Data/client_hardwares.csv'
    clusters_path = 'Data/tsp_clusters.json'
    distance_matrix_path = 'Data/distance_matrix.json'
    dm_json = open(distance_matrix_path)
    dist_matrix = json.load(dm_json)

    warehouses = get_warehouses(warehouse_path)
    print('\twarehouses -> ok\n')
    clients = get_clients(hardware_stores_path)
    print('\tclients -> ok\n')
    open_depots, depot_routes = get_lists(fl_model['variables'])
    routes = get_routes(clusters_path, fl_model['iteration'], depot_routes, dist_matrix)
    print('\troutes -> ok\n')
    
    #plot_open_depots(open_depots, warehouses)
    plot_client_routes(open_depots, warehouses, routes, clients)
    summarize_dict = dict()
    for od in open_depots:
        summarize_dict[od] = {'avg_distance': np.mean([routes[(w,r)]['distance'] for (w,r) in routes.keys() if w == od]),
                                'avg_weight': np.mean([routes[(w,r)]['weight'] for (w,r) in routes.keys() if w == od]),
                                'avg_time': np.mean([routes[(w,r)]['time'] for (w,r) in routes.keys() if w == od])}
    print('lets go, execution time -> {}'.format(time.time()-start_time)) 