from pandas import DataFrame
import numpy as np
import traceback
from Numerical_methods import Transformations, Matrix_calculations
import Configuration
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Elasto_plastic_deflections:
    def __init__(self) -> None:
        self.Delast_matrix:np.ndarray = None
        self.Dplast_Matrix:np.ndarray = None
        self.Delast_laplace_matrix:np.ndarray = None
        self.Dplast_laplace_Matrix:np.ndarray = None

    def generate_initial_Delast(self,shape:tuple=None):
        self.Delast_matrix = np.zeros(shape=shape)
    def generate_initial_Dplast(self,shape:tuple=None):
        self.Dplast_matrix = np.zeros(shape=shape)
    def generate_initial_Delast_laplace(self,shape:tuple=None):
        self.Delast_laplace_matrix = np.zeros(shape=shape)
    def generate_initial_Delast_laplace(self,shape:tuple=None):
        self.Dplast_laplace_Matrix = np.zeros(shape=shape)


def get_Delast_ij_value(g_coefficient_fourier_2d_array_wrapped_around:np.ndarray, p_kernel_fourier:np.ndarray) -> float:
    try:
        _transformations = Transformations()
        _linear_calculations = Matrix_calculations()
        _dot_product = _linear_calculations.get_dot_product(numpy_array1=g_coefficient_fourier_2d_array_wrapped_around, numpy_array2= p_kernel_fourier)
        _ifft_Delast_ij = _transformations.get_inverse_fourier_transform(numpy_array_2d= _dot_product)
        _ifft_Delast_ij = _transformations.get_real_part(numpy_array_2d=_ifft_Delast_ij)
        return _ifft_Delast_ij.mean()
    except Exception as ex:
        line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
        raise Exception(f'Deflections>get_Delast_ij_value: Line No. {str(line_number)}, {str(ex)}')
def get_Delast_laplace_ij_value(f_coefficient_fourier_2d_array_wrapped_around:np.ndarray, p_kernel_fourier:np.ndarray) -> float:
    try:
        _transformations = Transformations()
        _linear_calculations = Matrix_calculations()
        _dot_product = _linear_calculations.get_dot_product(numpy_array1=f_coefficient_fourier_2d_array_wrapped_around, numpy_array2= p_kernel_fourier)
        _ifft_Delast_ij = _transformations.get_inverse_fourier_transform(numpy_array_2d= _dot_product)
        _ifft_Delast_ij = _transformations.get_real_part(numpy_array_2d=_ifft_Delast_ij)
        return _ifft_Delast_ij.mean()
    except Exception as ex:
        line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
        raise Exception(f'Deflections>get_Delast_ij_value: Line No. {str(line_number)}, {str(ex)}')
    