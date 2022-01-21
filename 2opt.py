import json
import random
import nearest_neighbour
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
import itertools
import time
import sys
from collections import defaultdict

def data_sample(matrix:dict, warehouse_sample:int, client_sample:int) -> list:
    C = list()
    #W = list()
    counter = 0
    do_science = True
    c_list = [key for (key, val) in matrix.items() if val["type"] == "client"]
    w_list = [key for (key, val) in matrix.items() if val["type"] == "warehouse"
                                                    and val["own"] == 1]
    #and w_length == warehouse_sample:
    #if rand_warehouse not in W and w_length <= warehouse_sample: 
    #W.append(rand_warehouse)
    while do_science:
        c_length = len(C)
        rand_client = random.choice(c_list)
        if rand_client not in C and c_length <= client_sample:
            C.append(rand_client) 
        if c_length == client_sample:  
            do_science = False
        counter = counter + 1
        if counter > 100:
            break
    return C, w_list

def closest_distance(client:str, matrix:dict, clients_list:list):
    client_matrix = matrix[str(client)]['destinations']
    min_distance = min(client_matrix.items(), key = lambda x: x[1]['distance(km)']
                                                        if (x[1]['type'] == 'client'
                                                            and x[0] in clients_list)
                                                            else 1000)
    return min_distance

def closest_time(client:str, matrix:dict, clients_list:list):
    client_matrix = matrix[str(client)]['destinations']
    min_distance = min(client_matrix.items(), key = lambda x: x[1]['time(min)']
                                                        if (x[1]['type'] == 'client'
                                                            and x[0] in clients_list)
                                                            else 1000)
    return min_distance

def swap(tour:list, a:str, b:str):
    temp = tour.copy()
    a_index = temp.index(a)
    b_index = temp.index(b)
    temp[a_index] = b
    temp[b_index] = a
    return temp

def tour_length(tour:list, dist_matrix:dict) -> int:
    t_lenght = 0
    for index, node in enumerate(tour):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour[index-1]
            t_lenght += dist_matrix[previous_node]["destinations"][node]["distance(km)"]
    return t_lenght

def find_granular_neighbourhoods(dist_matrix:dict) -> list:
    # lets get the five best posible neighbors
    tour_neighbours = dict()
    avg_distance = float()
    for key, value in dist_matrix.items():
        avg_distance =  round(np.mean([in_val['distance(km)'] 
                                for in_key, in_val in value["destinations"].items()
                                if (value['type'] != 'warehouse' and in_val['type'] != 'warehouse')]),3)
    return tour_neighbours

def nearest_neighbour_algorithm(data_json:dict, dist_matrix:dict, clients:list, warehouses:list):
    for c in clients:
        plt.scatter(data_json[int(c)]['long'], data_json[int(c)]['lat'], marker='o', color='black')
    for w in warehouses:
        plt.scatter(data_json[int(w)]['long'], data_json[int(w)]['lat'], marker='v', color='red')
    visited = list()
    tour_length = 0
    do_magic = True
    temp_clients = clients.copy()
    to_visit = closest_distance(warehouses[0], dist_matrix, temp_clients)
    counter = 0
    while do_magic:
        plt.title('Nearest neighbour heuristic')
        if len(visited) < 1:
            plt.plot([data_json[int(warehouses[0])]['long'], data_json[int(to_visit[0])]['long']],
                    [data_json[int(warehouses[0])]['lat'], data_json[int(to_visit[0])]['lat']],
                    'b--')
            visited.append(to_visit[0])
            from_client = to_visit[0]
            temp_clients.remove(from_client)
            tour_length += to_visit[1]['distance(km)']
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
        elif len(visited) == (len(clients)-1):
            plt.plot([data_json[int(from_client)]['long'], data_json[int(to_visit[0])]['long']],
                    [data_json[int(from_client)]['lat'], data_json[int(to_visit[0])]['lat']],
                    'b--')
            visited.append(to_visit[0])
            from_client = to_visit[0]
            temp_clients.remove(from_client)
            tour_length += to_visit[1]['distance(km)']
            to_visit = warehouses[0]
        elif len(visited) == len(clients):
            plt.plot([data_json[int(from_client)]['long'], data_json[int(to_visit)]['long']],
                    [data_json[int(from_client)]['lat'], data_json[int(to_visit)]['lat']], 
                    'b--')
            visited.append(to_visit)
            m = dist_matrix[from_client]['destinations']
            tour_length += m[to_visit]['distance(km)']
            do_magic = False
        else: 
            plt.plot([data_json[int(from_client)]['long'], data_json[int(to_visit[0])]['long']],
                    [data_json[int(from_client)]['lat'], data_json[int(to_visit[0])]['lat']],
                    'b--')
            visited.append(to_visit[0])
            from_client = to_visit[0]
            temp_clients.remove(from_client) 
            tour_length += to_visit[1]['distance(km)']
            to_visit = closest_distance(from_client, dist_matrix, temp_clients)
        counter = counter + 1 
    plt.show()
    return visited, tour_length

def two_opt(tour_nearest:list, length_nearest:float, dist_matrix:dict, nodes_json:list) -> list:
    # A broken link must not be added 
    # An added link must not be broken
    best = length_nearest
    size = len(tour_nearest)
    improved = True
    laps = 0
    inserted_tabu_arcs = set() #arcs deleted
    removed_tabu_arcs = set() #arcs added
    tabu_counter = defaultdict(int)
    max_tabu_iterations = 18
    sparsification_factor = 1.9
    threshold = find_granular_neighbourhoods(dist_matrix)

    while improved:
        improved = False
        tour_1 = tour_nearest[0:size-3]
        for i, c_i in enumerate(tour_1): # initial nodes i
            if i+1 < len(tour_1): # dont visit last node 
                tour_2 = tour_nearest[i+2:size]
                for j, c_j in enumerate(tour_2):
                    if j+1 < len(tour_2):
                        if ((tour_1[i],tour_1[i+1]),(tour_2[j],tour_2[j+1])) not in removed_tabu_arcs:
                            # dist = dist_matrix[str(tour_1[i])]['destinations'][str(tour_2[j])]['distance(km)']
                            # if dist < threshold[c_i]*sparsification_factor:
                            current_distance = (dist_matrix[str(tour_1[i])]['destinations'][str(tour_1[i+1])]['distance(km)'] + 
                                                dist_matrix[str(tour_2[j])]['destinations'][str(tour_2[j+1])]['distance(km)'])
                            swap_distance = (dist_matrix[str(tour_1[i])]['destinations'][str(tour_2[j])]['distance(km)'] + 
                                            dist_matrix[str(tour_1[i+1])]['destinations'][str(tour_2[j+1])]['distance(km)'])
                            # Best gain possible is possitive
                            arc_gain = current_distance - swap_distance 
                            if arc_gain > 0:
                                former_best = best
                                print('\ni = {},j = {}'.format(i, j))
                                print('\nswap ({},{}) and ({},{}), for ({},{}) and ({},{})'.format(tour_1[i],tour_1[i+1],
                                                                                                    tour_2[j],tour_2[j+1], 
                                                                                                    tour_1[i],tour_2[j],
                                                                                                    tour_1[i+1],tour_2[j+1]))
                                print('\ncurrent distance is {}, but swap distance is lower, {}'.format(current_distance, swap_distance))
                                print('\nGain obtained with swap = {},\nformer best {}'.format(round(arc_gain, 2), round(former_best, 2)))
                                arc_deleted = ((tour_1[i],tour_1[i+1]),(tour_2[j],tour_2[j+1]))
                                arc_added = ((tour_1[i],tour_2[j]),(tour_1[i+1],tour_2[j+1]))
                                tabu_counter[(arc_added)] = int()
                                print('-'*40)
                                #Save swap into a tabu list, so the move is not performed again
                                #if former_best >= tour_length(swap(tour_nearest, tour_1[i+1], tour_2[j]), dist_matrix):
                                if arc_added not in inserted_tabu_arcs:
                                    inserted_tabu_arcs.add(arc_added)
                                    removed_tabu_arcs.add(arc_deleted)
                                    tabu_counter[arc_added] += 1
                                    # potential_tour = swap(tour_nearest, tour_1[i+1], tour_2[j])
                                    # potential_best = tour_length(potential_tour, dist_matrix)   # Add a negative number
                                    # print('\npotential best {}'.format(potential_best))
                                    # print('-'*40)
                                    # if potential_best < former_best:
                                    tour_nearest = swap(tour_nearest, tour_1[i+1], tour_2[j])
                                    best = tour_length(tour_nearest, dist_matrix)
                                    print('\nimprovement is real\nnew best {}'.format(best))
                                    improved = True
                                    laps += 1
                                    print('='*40)
                                    #assert former_best >= best
                                    break
                                    # else:
                                    #     improved = True
                                    #     break
                                elif tabu_counter[(arc_added)] > max_tabu_iterations:
                                    inserted_tabu_arcs.remove(arc_added)
                                    print('\nSwap is not tabu anymore, therefore, swap {} is now available'.format(arc_added))
                                    continue
                                else:
                                    print('\nSwap is tabu, An added link must not be broken\n')
                                    print('='*40)
                                    continue
                        else:
                            print('\nSwap is tabu, A broken link must not be added \n')
                            print('='*40)
                            continue
                if improved:
                    break  
    # Let's plot the new tour results
    length_best_tour = 0
    plt.title('2-opt')
    
    for node in tour_nearest[:size-1]:
        if node == '0':
            plt.scatter(nodes_json[int(node)]['long'], nodes_json[int(node)]['lat'], marker='v', color='red')
        else:
            plt.scatter(nodes_json[int(node)]['long'], nodes_json[int(node)]['lat'], marker='o', color='black')
            
    for index, node in enumerate(tour_nearest):
        #Don't plot a tour from the first point
        if index == 0:
            continue
        else:
            previous_node = tour_nearest[index-1]
            length_best_tour += dist_matrix[previous_node]["destinations"][node]["distance(km)"]
            plt.plot([nodes_json[int(previous_node)]['long'], nodes_json[int(node)]['long']],
                    [nodes_json[int(previous_node)]['lat'], nodes_json[int(node)]['lat']],
                    'b--')
    plt.show()
    return tour_nearest, length_best_tour

if __name__ == '__main__':
    print('2-opt with tabu')  