import numpy as np
import Numerical_methods
import copy
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Calculations:
    def __init__(self) -> None:
        self.B0:float = None
        self.B_matrix:np.ndarray = None
        self.index_landa:list = None
        self.convolution: Numerical_methods.Convolution = Numerical_methods.Convolution();
        
    def get_B_Coefficients_Bexluded_and_B00(self,DeltaX:float, DeltaY:float ) -> tuple[np.ndarray, float]:
        BCoefficients = np.zeros((3,3))
        B2 = B6 = 1/(DeltaX**2)
        B4 = B8 = 1/(DeltaY**2)
        B0 = (-2)*((1/(DeltaX**2))+(1/(DeltaY**2)))
        BCoefficients[0][1] = B4
        BCoefficients[1][0] = B2
        #BCoefficients[1][1] = B0 #this leaves the B0 equal to zero so it excluded the effect of B0
        BCoefficients[1][2] = B6
        BCoefficients[2][1] = B8

        return (BCoefficients , B0)
    
    def __get_near_contribution_convolved(self, base_array:np.ndarray, kernel:np.ndarray) -> np.ndarray:
        return (self.convolution.get_image_convolve_2d(numpy_array_2d=base_array,kernel=kernel))

    def get_far_contributions(self, Delast_laplacian_ij:float, F00_Pold_ij:float, base_array:np.ndarray, kernel:np.ndarray) -> float:
        return float(Delast_laplacian_ij - F00_Pold_ij - (self.__get_near_contribution_convolved(base_array= base_array, kernel= kernel)[0,0]))
    
    def get_B_landa_summation(self, B_Matrix:np.ndarray, H_Matrix:np.ndarray, 
                                    D_plast_Matrix:np.ndarray,F_kernel:np.ndarray, 
                                    P_Matrix:np.ndarray,):
        if((B_Matrix.shape != H_Matrix.shape) or (B_Matrix.shape != P_Matrix.shape)) or (B_Matrix.shape != D_plast_Matrix.shape):
            raise Exception('The size/shape of the matrices are not the same. Please check the inputs.')
        sum:float = 0.00
        for row in range(B_Matrix.shape[0]):
            for column in range(B_Matrix.shape[1]):
                #Summation[B_landa*(Hij_Landa - Dplast_ij_landa) - F_landa*Pij_Landa]
                innerVar = H_Matrix[row,column] - D_plast_Matrix[row,column]
                outerVar = F_kernel[row,column]*P_Matrix[row,column]
                var = (B_Matrix[row,column]*innerVar) - (outerVar)
                sum += var
        return sum