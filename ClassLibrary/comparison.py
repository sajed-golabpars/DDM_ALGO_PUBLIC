import numpy as np
import pandas as pd
import Preprocess 
import Configuration

def get_s_aggregate(preprocessor:Preprocess.Preprocessor, Rmax=None) -> dict:
    if(Rmax is None):
        Rmax = Configuration.R_max
    S_matrix = np.zeros(shape = preprocessor.Roughness_Matrix.shape)
    x,y = S_matrix.shape
    for i in range(x):
        for j in range(y):
            approach_distance = Rmax - preprocessor.Roughness_Matrix[i,j] + preprocessor.Delast_Matrix[i,j] - preprocessor.Height_Matrix[i,j]
            S_matrix[i,j] = approach_distance
    S_matrix = S_matrix[Configuration.padding_size:-Configuration.padding_size,Configuration.padding_size:-Configuration.padding_size]
    result_dictionary = {'Max': np.max(S_matrix)
                         ,'Min': np.min(S_matrix)
                         ,'Average': np.average(S_matrix)
                         ,'Pmean': np.mean(preprocessor.P_Matrix)}
    return result_dictionary




