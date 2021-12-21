from LRPmodel import train, Model

from dataloading import Dataset_train
from data import load_data_cv
import torch as tc
import sys
import os
import pandas as pd
import numpy as np
from joblib import Parallel, delayed

PATH = '.'



model_path = PATH + '/results/crossvalidation/models/'
RESULTPATH = PATH + '/results/crossvalidation/cv.csv'
if os.path.exists(RESULTPATH):
    os.remove(RESULTPATH)

nepochs = 801

def crossval(loop):
    for learning_rate in [0.01, 0.005, 0.001]:
        for hidden_depth in [3,4,5,6]:
            for hidden_factor in [3, 5, 10, 20]:
                print(learning_rate, hidden_depth, hidden_factor)
                train_data, test_data, featurenames, train_names, test_names = load_data_cv(loop,5)
                model = Model(train_data.shape[1] * 2, train_data.shape[1], hidden=(train_data.shape[1]) * hidden_factor,
                    hidden_depth=hidden_depth)

                losses = train(model, train_data, test_data, epochs=nepochs, lr=learning_rate, batch_size=25,
                    device=tc.device("cuda:0"))

                losses[['lr', 'depth', 'neurons', 'loop']] = learning_rate, hidden_depth, hidden_factor, loop
                
                print(losses)

                if not os.path.exists(model_path):
                    os.makedirs(model_path)
                model.cpu()


                tc.save(model.cpu(), model_path + '_' + str(nepochs) + '_' + str(learning_rate) + '_' + str(hidden_depth) + '_' + 
                    str(hidden_factor) +   '.pt')

                losses.to_csv(RESULTPATH, mode='a', header=not os.path.exists(RESULTPATH))

Parallel(n_jobs=5)(delayed(crossval)(loop) for loop in range(5))
