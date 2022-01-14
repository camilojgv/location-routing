from routing_api import *
import json
import time
import sys
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import traceback
import sys
plt.style.use('seaborn-whitegrid')

def time_frames():
        business_hours = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
        tomorrow =  datetime.today() + timedelta(days=1)
        day = datetime.strftime(tomorrow, "%d")
        month = datetime.strftime(tomorrow, "%m")
        year = datetime.strftime(tomorrow, "%Y")
    
        departure_times = list()
        
        for hour in business_hours:
            departure_times.append("{}-{}-{}T{}:00:00".format(year, month, day, hour))
        
        return departure_times

def run_distance_matrix(main_data: list, params: dict, json_name:str, avg_speed:int) -> dict:
    counter = 0
    result_json = {}
    n = len(main_data)
    for i, i_value in enumerate(main_data):
        result_json[i] = {}
        result_json[i] = {'type': i_value['point_type'],
                            'id': i_value['id'],
                            'destinations': {} }
        for j, j_value in enumerate(main_data):
            if i == j:
                continue
            else:
                origin = [i_value['lat'], i_value['long']]
                destination = [j_value['lat'], j_value['long']]
                arc = Route(origin,
                            destination,
                            params['transport_mode'],
                            params['departure_times'][0])
                
                results = arc.linearDistance(avg_speed)
                result_json[i]['destinations'][j] = {'type': j_value['point_type'],
                                                    'id': j_value['id'],
                                                    'distance(km)': round(results['route_summary']['length(kms)'], 4),
                                                    'time(min)': round(results['route_summary']['duration(min)'])}
                counter = counter + 1
            sys.stdout.write('\r')
            sys.stdout.write('iteration {}-{}, Matrix progress {} %'.format(i,j, round(counter/(n*n),2)))
            sys.stdout.flush()  
    with open(json_name, "w+") as f:
        json.dump(result_json, f)

def run_hereapi_distance_matrix(main_data:dict, params: dict):
    counter = 0
    result_json = {}
    n = len(main_data['lat'].keys())
    end_now = False
    for i in main_data['lat'].keys():
        result_json[i] = {}
        result_json[i] = {'type': main_data['point_type'][str(i)],
                            'destinations': {}}
        for j in main_data['lat'].keys():
            if i == j:
                continue
            else:
                origin = [main_data['lat'][str(i)], float(main_data['long'][str(i)])]
                destination = [main_data['lat'][str(j)], float(main_data['long'][str(j)])]
                arc = Route(origin,
                            destination,
                            params['transport_mode'],
                            params['departure_times'][0])
                results = arc.linearDistance(18)
                if results['route_summary']['length(kms)'] > 50:
                    result_json[i]['destinations'][j] = {'type': main_data['point_type'][str(j)],
                                                        'distance(km)': round(results['route_summary']['length(kms)'], 4),
                                                        'time(min)': round(results['route_summary']['duration(min)'])}
                   
                else:
                    api_results = arc.here_maps_api()
                    result_json[i]['destinations'][j] = {'type': main_data['point_type'][str(j)],
                                                        'distance(km)': round(api_results['route_summary']['length(kms)'], 4),
                                                        'time(min)': round(api_results['route_summary']['duration(min)'])}         
                    if result_json[i]['destinations'][j]['distance(km)'] == 1234:
                        end_now = True
                counter = counter + 1
                
            sys.stdout.write('\r')
            sys.stdout.write('iteration {}-{}, Matrix progress {}'.format(i,j, round(counter/(n*n),4)))
            sys.stdout.flush()

            if end_now:
                print('\n', 'end suddenly.')
                break
    
    saving_path = {'home':'E:/Main User/Documents/Repositories/VRP/Data/the_api_matrix.json',
                'tul': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/the_api_matrix.json'}
    
    # with open(saving_path['home'], 'w') as json_file:
    #     json.dump(result_json, json_file) 

# Import data from local files
if __name__ == '__main__':
    start_time = time.time()
    locations_json_path = {'tul': 'C:/Users/NECSOFT/Documents/Repositories/LRP/Data/problem_set.json',
                           'home':'E:/Main User/Documents/Repositories/VRP/Data/problem_set.json'}
    f = open(locations_json_path['tul'])
    locations_data = json.load(f)
    params = {'transport_mode':'truck',
              'departure_times': time_frames()}
    print('Pitagorical distance ---------------------')
    json_fname = "Data/distance_matrix_slow.json"
    speeds = {'7am': 22,'8am': 17,
              '9am': 19,'10am': 22,
              '11am': 23,'12am': 24,
              '1pm': 23,'2pm': 22,
              '3pm': 21,'4pm': 19,
              '5pm': 15}
    run_distance_matrix(locations_data, params, json_fname, speeds['8am'])
    print('\nrunning time: {}'.format(time.time()-start_time))


    
                                
    # print('Here API distance ---------------------')
    # run_hereapi_distance_matrix(locations_data, params)
    # print('\nrunning time: {}'.format(time.time()-start_time))
    
    # origin = [locations_data['lat']['72'], locations_data['long']['72']]
    # destination = [locations_data['lat']['211'], locations_data['long']['211']]
    # route = Route(origin, destination, params['transport_mode'], params['departure_times'][0])
    # results = route.here_maps_api()
    

    # print(results)



    
    
    
    
    
    
