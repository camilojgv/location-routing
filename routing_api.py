import requests
import json
import math
import datetime
from here_api_oauth_token import get_token
import traceback
import sys

response = json.loads(get_token())

access = "Bearer {}".format(response["access_token"])

request_headers = {'Authorization': access}

class Route:
    def __init__(self, origin, destination, transport_mode, departure_time):
        self.origin = {
                        'lat': origin[0], 
                        'long': origin[1]
                      }
        self.destination = {
                            'lat': destination[0],
                            'long': destination[1]
                           }
        self.mode = transport_mode
        self.departure_time = departure_time

    def get_url(self):
        initial_url = 'https://router.hereapi.com/v8/routes?transport'
        transportation_mode = 'Mode=' + str(self.mode)
        origin_point = '&origin=' + str(self.origin['lat']) + ',' + str(self.origin['long'])
        arrival_point = '&destination=' + str(self.destination['lat']) + ',' + str(self.destination['long'])
        results = '&return=summary'
        departure_time = '&departuretime='+ str(self.departure_time)
        
        url = initial_url + transportation_mode + origin_point + arrival_point + results + departure_time
        self.url = url
        
    def here_maps_api(self):
        self.get_url()
        url = self.url
        times = {}
        request = requests.get(url, headers = request_headers)
        python_dict = json.loads(request.text)
        
        try:
            summary = python_dict['routes'][0]['sections'][0]['summary']
            departure_time = python_dict['routes'][0]['sections'][0]['departure']['time']
            arrival_time = python_dict['routes'][0]['sections'][0]['arrival']['time']
            times = {'route_summary': {'duration(min)': round(summary['duration']/60, 2),
                                    'length(kms)': summary['length']/1000,
                                    'base duration(min)': round(summary['duration']/60, 2)},
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'transportation_mode': self.mode}
        except:
            print(traceback.format_exc())
            print(sys.exc_info())
            print(python_dict)
            times = {'route summary': {'duration(min)': 1234,
                                        'length(kms)': 1234,
                                        'base duration(min)': 1234}
                                      }     
        return times

    def linearDistance(self, velocity):
        # approximate radius of earth in km
        results = dict()
        R = 6373.0
        origin = self.origin
        destination = self.destination
        lat1 = math.radians(origin['lat'])
        lon1 = math.radians(origin['long'])
        lat2 = math.radians(destination['lat'])
        lon2 = math.radians(destination['long'])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c         # Distance in km
        vel = velocity
        t_hours = distance/vel
        t_mins = t_hours*60 
        results = {'route_summary': {'duration(min)': round(t_mins, 2),
                                     'length(kms)': round(distance, 2),
                                     'avg_velocity(kph)': vel},
                                     'transportation_mode': self.mode}
        return results 

if __name__ == '__main__':
    print('Save all the calculations to use the routing api :)')
