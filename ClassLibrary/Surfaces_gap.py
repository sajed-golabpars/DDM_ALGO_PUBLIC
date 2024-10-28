import traceback
from pandas import DataFrame
import numpy as np
import Configuration
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Gap:
    def __init__(self) -> None:
         self.Height_Matrix = None
    
    def generate_initial_H_Matrix_Considering_s(self,roughnes_matrix:np.ndarray,
                                                R_max:float=None,
                                                approach_distance:float=None):
            try:
                if(roughnes_matrix is None):
                    raise Exception("Sufraces_gap>calculate_initial_H_Matrix_Considering_s: roughnes_matrix is None")
                if(approach_distance is None):
                    approach_distance = Configuration.approach_distance
                if(R_max is None):
                    R_max = Configuration.R_max
                self.Height_Matrix:np.ndarray = R_max - roughnes_matrix - approach_distance
            except Exception as ex:
                line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
                raise Exception(f'Sirface_gap>gap>generate_initial_H_Matrix_Considering_s: Line No. {str(line_number)}, {str(ex)}')
