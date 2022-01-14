from gurobipy import Model,GRB,quicksum
import clustering
import json
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import sys

def tour_length(tour:list,dist_matrix:dict) -> int:
    t_lenght = 0
    for index, node in enumerate(tour):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour[index-1]
            t_lenght += dist_matrix[str(previous_node)]["destinations"][str(node)]["distance(km)"]
    return t_lenght

def get_client_set(clients:dict):
    new_clients = list()
    for c in clients:
        if c['point_type'] == 'client':
            new_clients.append(int(c['id']))
    return new_clients 

def get_warehouse_set(warehouses:object, w_sample:int):
    np.random.seed()
    w_dict = warehouses.to_dict(orient='index')
    W = list()
    for key,value in w_dict.items():
        if value['own'] == 1:
            W.append(key)
            break   #Do not cover whole loop, let's stop once we find the conditions
    do_science = True
    w_list = [key for key in w_dict.keys() if w_dict[key]['own']==0]
    while do_science:
        w_length = len(W)
        rand_wh = random.choice(w_list)
        if rand_wh not in W and w_length <= w_sample:
            W.append(rand_wh) 
        if w_length == w_sample:  
            do_science = False        
    return W

def get_routes_matrix(W, cluster_routes):
    cr = dict()
    for w in W:
        for r in cluster_routes.keys():
            cr[(w,int(r))] = [str(w)] + cluster_routes[r]['id_route']
            cr[(w,int(r))].append(str(w))
    return cr

def open_costs(W:list, warehouses:object):
    w_dict = warehouses.to_dict(orient='index')
    oc = {w:w_dict[w]['cost'] for w in W}
    return oc

def route_variable_cost(W, cluster_routes, dist_matrix):
    route_costs = dict()
    for w in W:
        for r in cluster_routes.keys(): 
            tour = cluster_routes[r]['route']
            #Add warehouse in the beggining and the end
            tour = [w] + tour
            tour.append(w)
            #cost per km * kms
            rc = round(tour_length(tour, dist_matrix)*2000 + (300000),3)
            route_costs[(w,int(r))] = rc*365 
    return route_costs  

def routes_weight(cluster_routes:dict):
    routes_weight = dict()
    for r in cluster_routes.keys(): 
        routes_weight[int(r)] = cluster_routes[r]['weight']
    return routes_weight

def warehouse_capacity(W:list, warehouses:object):
    # if 4500, can supply for 300.000 kgs, how much can supply other warehouses
    wc = dict()
    cap = int()
    ftbn_capacity = 400000
    ftbn_area = 4500
    for w in W:
        area = int(warehouses.iloc[int(w)]['area'])
        wc[w] = round(area*(ftbn_capacity/ftbn_area), 3)
    return wc

def var_split(name:str, type_:str):
    result = dict()
    if type_ == 'x':
        s1 = name.split('=')
        s2 = s1[0].split(']')
        s3 = s2[0].split('[')
        var = s3[0]
        w = s3[1].split(',')[0]
        r = s3[1].split(',')[1] 

        result = {'type': var,
                  'key': (int(w),int(r))}
    elif type_ == 'y':
        s1 = name.split('=')
        s2 = s1[0].split(']')
        s3 = s2[0].split('[')
        var = s3[0]
        w = s3[1]
        result = {'type': var,
                  'key': int(w)}
    return result

def optimize(sets:dict, params:dict):
    result_dict = dict()
    # Add datasets
    W = sets['warehouses']
    G = sets['routes']
    # optimization model
    fl_model = Model('Facility location')
    fl_model.Params.LogToConsole = 0
    # Add decision variables
    X = [(i,int(j)) for i in W for j in G]
    Y = [i for i in W]
    y = fl_model.addVars(Y, vtype=GRB.BINARY, name='y')
    x = fl_model.addVars(X, vtype=GRB.BINARY, name='x')

    # Add parameters to the problem
    oc = params['opening costs']
    rc = params['route distance cost']
    rw = params['route weights']
    mc = params['max capacity']

    # Add objective function
    fl_model.setObjective(quicksum(oc[i]*y[i] for i in W) + 
                        quicksum(rc[(i,j)]*x[(i,j)] for i in W for j in G),
                        GRB.MINIMIZE)
    fl_model.addConstrs(quicksum(x[(i,j)] for i in W) == 1 for j in G)
    fl_model.addConstrs(quicksum(rw[j]*x[(i,j)] for j in G ) <= mc[i]*y[i] for i in W)
    fl_model.addConstr(y[0] == 1)
    fl_model.optimize()
    
    result_dict = {'fo': str(round(fl_model.Objval, 2)),
                    'vars': dict()}
    for v in fl_model.getVars():
        res = var_split(v.VarName, v.VarName[0])
        result_dict['vars'][(res['type'],res['key'])] = str(round(v.x))
    return result_dict 

def main(params:dict):
    warehouse_path = {'tul_pc': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/potential_warehouses.csv',
                    'home_pc': 'E:/Main User/Documents/Repositories/VRP/Data/potential_warehouses.csv'}

    distance_matrix_path = {'tul_pc':'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/distance_matrix_slow.json',
                            'home_pc':'E:/Main User/Documents/Repositories/VRP/Data/distance_matrix_slow.json'}
    
    hardware_stores_path = {'tul_pc': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/client_hardwares.csv'}
    nodes_path = {'tul_pc': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/problem_set.json'}
    clusters_path = {'tul_pc': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/tsp_clusters.json'}
    loc = 'tul_pc'
    warehouses = pd.read_csv(warehouse_path[loc])
    warehouses.columns = ['lat', 'long', 'cost', 'area', 'own','weight']
    warehouses.filter(items=['lat', 'long', 'cost', 'area', 'own'])
    nodes_json = open(nodes_path[loc])
    nodes_set = json.load(nodes_json)
    clients_hardware = pd.read_csv(hardware_stores_path[loc])
    d_matrix_json = open(distance_matrix_path[loc])
    distance_matrix = json.load(d_matrix_json)
    clust_json = open(clusters_path[loc])
    clusters = json.load(clust_json)
        
    W = get_warehouse_set(warehouses, params['warehouse_sample'])
    C = get_client_set(nodes_set)
    W_capacity = warehouse_capacity(W, warehouses)
    O = open_costs(W, warehouses)
    
    #iterate through all clusters and find best results
    best_model = {'fo':0,'variables':None,'iteration':0}
    
    for n_iter,g in enumerate(clusters.keys()):
        G = [int(j) for j in clusters[g].keys()]
        R = route_variable_cost(W, clusters[g], distance_matrix)
        R_weight = routes_weight(clusters[g])
        sets = {'warehouses': W,
                'clients': C,
                'routes':G}
        params = {'opening costs': O,
                'route distance cost': R,
                'route weights': R_weight,
                'max capacity': W_capacity}
        iter_weight = np.sum([weight for g,weight in R_weight.items()])
        results = optimize(sets, params)
        if n_iter < 1: 
            best_model['fo'] = results['fo'] 
            best_model['variables'] = results['vars']
        else:
            if best_model['fo'] > results['fo']:
                best_model['fo'] = results['fo'] 
                best_model['variables'] = results['vars']
                best_model['iteration'] = n_iter
                best_model['total weight'] = iter_weight 
    return best_model

if __name__=='__main__':
    print('facility location optimization')
    params = {'client_sample': 860,
                'warehouse_sample': 35,
                'max_distance': 25,
                'max_duration': 7*60, #between 7 and 8 hours
                'max_weight': 9000}
    results = main(params)
    np.save('flp_results_rcopt_c860_w35.npy', results)
    print('finished...')