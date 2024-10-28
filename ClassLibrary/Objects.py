import numpy as np
from ClassLibrary import Preprocess
from ClassLibrary import Configuration

import copy
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class claculation_parameters:
    def __init__(self) -> None:
        self.P_kernel:np.ndarray = None
        self.P_kernel_fourier:np.ndarray = None
        self.Delast_ij_2d_array_DDMethod:np.ndarray = None
        self.Dplast_ij_2d_array_DDMethod:np.ndarray = None
        self.Delast_ij_value_DDMethod:float = None
        self.Delast_laplace_ij_value_DDMethod:float = None
        self.Dplast_ij_value_DDMethod:float = None
        self.Delast_i0j0:float = None
        self.Hmax:float = None
        self.Hi0j0:float = None
        self.Hij_old:float = None
        #For inner Loop - Steps 9 to 12
        self.neighbors_relative_index:list = None
        self.neighbors_height_kernel_3x3:np.ndarray = np.zeros((Configuration.outerloop_calculations_kernel_size,Configuration.outerloop_calculations_kernel_size))
        self.F_Kernel_IJexcluded_3x3:np.ndarray = np.zeros((Configuration.outerloop_calculations_kernel_size,Configuration.outerloop_calculations_kernel_size))
        self.P_Kernel_3x3:np.ndarray = np.zeros((Configuration.outerloop_calculations_kernel_size,Configuration.outerloop_calculations_kernel_size))
        self.F00:float = None
        self.Pij:float = None
        self.F00_Pold_ij:float = None
        self.B_coefficient_B00excluded:np.ndarray = None
        self.B0:float = None
        self.RHSij:float = None
        self.far_contributions:float = None
        self.Dplast_near_neighbors_3x3:np.ndarray = None
        self.B_landa_summation:float = None
        self.Aij_eq20:float = None
        self.Aij_eq21:float = None
        #Steps 11 ahead
        self.Pij_new:float = None
        self.Hij_new:float = None
        self.Dplast_ij_new:float = None
        self.F0_Pmax:float = None
        self.Aij:float = None
        self.Aij_previous:float = 1000
        self.centerindex_5x5:int = 2
        self.centerindex_3x3:int = 1
        self.landa_index:list = [   (self.centerindex_3x3+1,self.centerindex_3x3-1),(self.centerindex_3x3 +0,self.centerindex_3x3-1),(self.centerindex_3x3-1,self.centerindex_3x3-1),
                                    (self.centerindex_3x3-1,self.centerindex_3x3 +0),(self.centerindex_3x3-1,self.centerindex_3x3+1),
                                    (self.centerindex_3x3+0,self.centerindex_3x3+1),(self.centerindex_3x3+1,self.centerindex_3x3+1),
                                    (self.centerindex_3x3+1,self.centerindex_3x3+0),
                                    (self.centerindex_3x3+0,self.centerindex_3x3+0)   ] #the last one is the Center point (i,j) means 1 cycle is done
        self.Hij_cached_5x5:np.ndarray = None
        self.Pij_cached_5x5:np.ndarray = None
        self.Dplast_cached_5x5:np.ndarray = None

        #initialize essential paramaters

    def update_neighbors_relative_index_3x3(self,location:tuple) -> None:
        i,j = location
        self.parameters.neighbors_relative_index = [(i+1,j-1),(i +0,j-1),(i-1,j-1),
                                                                (i-1,j +0),(i-1,j+1),
                                                                (i+0,j+1),(i+1,j+1),
                                                                (i+1,j+0),
                                                                (i+0,j+0)]
    
    def update_H_P_Dplast_cached_5x5(self, location:tuple, preprocessor:Preprocess.Preprocessor) -> None:
        i,j = location
        self.Hij_cached_5x5:np.ndarray = copy.deepcopy(preprocessor.Height_Matrix[i-2:i+3,j-2:j+3])
        self.Pij_cached_5x5:np.ndarray = copy.deepcopy(preprocessor.Height_Matrix[i-2:i+3,j-2:j+3])
        self.Dplast_cached_5x5:np.ndarray = copy.deepcopy(preprocessor.Height_Matrix[i-2:i+3,j-2:j+3])


    def update_F00(self, F_Coefficient:np.ndarray) -> None:
        if(F_Coefficient.shape[0] % 2 == 0):
            raise Exception('F Matrix is not Axy-Symmetric.')
        center = int((F_Coefficient.shape[0]-1)/2)
        self.F00 = float(F_Coefficient[center,center])
        return self.F00
    
    def update_F_Kernel_IJexcluded_3x3(self,Fij:np.ndarray) -> np.ndarray:
        fij_center:int = int(Fij.shape[0])
        if(fij_center%2 == 0):
            fij_center = int(fij_center/2)
        else:
            fij_center = int((fij_center-1)/2)
        self.F_Kernel_IJexcluded_3x3 = copy.deepcopy(Fij[fij_center-1:fij_center+2,fij_center-1:fij_center+2])
        #reset index if necessary
        return self.F_Kernel_IJexcluded_3x3
    
    def crop_P_Kernel_3x3(self, P_Matrix:np.ndarray, location:tuple) -> None:
        i,j = location
        self.P_Kernel_3x3 = copy.deepcopy(P_Matrix[i-1:i+2,j-1:j+2])
        self.P_Kernel_3x3[1,1] = 0 #Exclude P00
        return self.P_Kernel_3x3
    
    def update_P_kernel_3x3(self, approach:int) -> None:
        if(approach == 1):
             for item in self.P_Kernel_3x3:
                  item = self.Pij_new
        elif(approach == 2):
            for index, location in enumerate(self.landa_index):
                if(index > 3 and index != 8):
                                self.P_Kernel_3x3[location[0], location[1]] = self.Pij_new
        elif(approach == 3):
             pij:float = self.P_Kernel_3x3[0,0] + self.P_Kernel_3x3[0,1] + self.P_Kernel_3x3[0,2] + self.P_Kernel_3x3[1,0] #Summation of the first four neighbors which are calculated and fixed already
             pij = ((self.Pij_new * 8) - pij ) / 4
             for index, location in enumerate(self.landa_index):
                if(index > 3 and index != 8):
                                self.P_Kernel_3x3[location[0], location[1]] = pij
        else:
             pass

    def update_Dplast_near_neighbors_3x3(self, Dplast_matrix:np.ndarray, location:tuple) -> np.ndarray:
        i,j = location
        self.Dplast_near_neighbors_3x3 = np.zeros((3,3))
        self.Dplast_near_neighbors_3x3 = copy.deepcopy(Dplast_matrix[i-1:i+2,j-1:j+2])
        return self.Dplast_near_neighbors_3x3

    def update_height_kernel_3x3(self,location:tuple, Hmax:float, Rmin:float,  Delast_i0j0, Preprocessor:Preprocess.Preprocessor,) -> None:
        i,j = location
        c_i = -2
        for i_t in range(3):
            c_i += 1
            c_j = -1
            for j_t in range(3):
                if(i < 1) or (i==1 and j == 0):
                    continue
                self.neighbors_height_kernel_3x3[i_t,j_t] = Hmax + Rmin - Preprocessor.Roughness_Matrix[i+c_i,j+c_j] + Preprocessor.Delast_Matrix[i+c_i,j+c_j] - Delast_i0j0 + Preprocessor.Dplast_Matrix[i+c_i,j+c_j]
                c_j += 1

