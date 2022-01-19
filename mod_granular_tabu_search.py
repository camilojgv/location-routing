import numpy as np
import matplotlib.pyplot as plt
import json

def shift():
    return 'hello'

def swap():
    return 'hello'

def two_opt():
    return 'hello'

def exchange():
    return 'hrllo'

def inter_tour_exchange():
    return 'hello' 

if __name__=='__main__':
    #get the initial solution
    fl_model = np.load('optimization_results/flp_results_rcopt_c860_w35.npy',allow_pickle='TRUE').item()
    print('hello world')