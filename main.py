import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import time
import nearest_neighbour
import clustering

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

def plot_open_depots(open_w, warehouses):
    for key,value in warehouses.items():
        if key in open_w:
            plt.scatter(value['long'], value['lat'], marker='^', color='red')
        else:
            plt.scatter(value['long'], value['lat'], marker='o', color='white')
    plt.show()

def plot_client_routes(open_w, warehouses, routes, clients):
    for key,value in warehouses.items():
        if key in open_w:
            plt.scatter(value['long'], value['lat'], marker='^', color='red')
            #plot routes that start from the depot
    
    plt.show()
    
    # for c in clients:
    #     plt.scatter(data_json[int(c)]['long'], data_json[int(c)]['lat'], marker='o', color='black')
    
    # visited = list()
    # tour_length = 0
    # do_magic = True
    # temp_clients = clients.copy()
    # first_client = random.choice(temp_clients)
    # visited.append(first_client)
    # temp_clients.remove(first_client) 
    # to_visit = closest_distance(first_client, dist_matrix, temp_clients)
    # counter = 0
    # while do_magic:
    #     plt.title('Nearest neighbour heuristic')
    #     if len(visited) < 2:
    #         plt.plot([data_json[int(first_client)]['long'], data_json[int(to_visit[0])]['long']],
    #                 [data_json[int(first_client)]['lat'], data_json[int(to_visit[0])]['lat']],
    #                 'b--')
    #         from_client = to_visit[0] #client already visited, new starting point
    #         temp_clients.remove(from_client) 
    #         visited.append(from_client)
    #         tour_length += to_visit[1]['distance(km)']
    #         to_visit = closest_distance(from_client, dist_matrix, temp_clients)
    #     else: 
    #         plt.plot([data_json[int(from_client)]['long'], data_json[int(to_visit[0])]['long']],
    #                 [data_json[int(from_client)]['lat'], data_json[int(to_visit[0])]['lat']],
    #                 'b--')
    #         visited.append(to_visit[0])
    #         from_client = to_visit[0]
    #         temp_clients.remove(from_client) 
    #         tour_length += to_visit[1]['distance(km)']
    #         to_visit = closest_distance(from_client, dist_matrix, temp_clients)
    #         if len(temp_clients) == 0:
    #             plt.plot([data_json[int(from_client)]['long'], data_json[int(first_client)]['long']],
    #                 [data_json[int(from_client)]['lat'], data_json[int(first_client)]['lat']],
    #                 'b--')
    #             do_magic = False 
    #     counter = counter + 1 
    # plt.show()
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
    # params = {'client_sample': 300,
    #             'warehouse_sample': 10,
    #             'max_distance': 25,
    #             'max_duration': 7*60, #between 7 and 8 hours
    #             'max_weight': 9000}

    #fl_model = facility_location.main(params)
    print('get results from FL problem\n')
    fl_model = np.load('flp_results_rcopt_c860_w35.npy',allow_pickle='TRUE').item()
    print('get other information, warehouses, clients, routes\n')
    warehouse_path = 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/potential_warehouses.csv'
    hardware_stores_path = 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/client_hardwares.csv'
    clusters_path = 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/tsp_clusters.json'
    distance_matrix_path = 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/distance_matrix.json'
    dm_json = open(distance_matrix_path)
    dist_matrix = json.load(dm_json)

    warehouses = get_warehouses(warehouse_path)
    print('\twarehouses -> ok\n')
    clients = get_clients(hardware_stores_path)
    print('\tclients -> ok\n')
    open_depots, depot_routes = get_lists(fl_model['variables'])
    routes = get_routes(clusters_path, fl_model['iteration'], depot_routes, dist_matrix)
    print('\troutes -> ok\n')
    
    plot_open_depots(open_depots, warehouses)
    summarize_dict = dict()
    for od in open_depots:
        summarize_dict[od] = {'avg_distance': np.mean([routes[(w,r)]['distance'] for (w,r) in routes.keys() if w == od]),
                                'avg_weight': np.mean([routes[(w,r)]['weight'] for (w,r) in routes.keys() if w == od]),
                                'avg_time': np.mean([routes[(w,r)]['time'] for (w,r) in routes.keys() if w == od])}
    print('lets go, execution time -> {}'.format(time.time()-start_time)) 