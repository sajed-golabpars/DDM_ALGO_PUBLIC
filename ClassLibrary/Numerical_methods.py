import Configuration
import numpy as np
import traceback
from scipy import ndimage,fft,optimize
from scipy.signal import convolve2d, convolve
import math
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Transformations:
    def __init__(self) -> None:
        pass

    def get_fast_fourier_transorm_2d(self,numpy_array_2d:np.ndarray, norm = None) -> np.ndarray:
        try:
            if (norm is None):
                norm = Configuration.fast_fourier_transform_norm
            return np.array(fft.fft2(numpy_array_2d, norm=norm))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_methods>Transformations>get_fast_fourier_transorm_2d: Line No. {str(line_number)}, {str(ex)}')

    def get_inverse_fourier_transform(self,numpy_array_2d:np.ndarray, norm = None) -> np.ndarray:
        try:
            if (norm is None):
                norm = Configuration.fast_fourier_transform_norm
            return np.array(fft.ifft2(numpy_array_2d, norm=norm))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_methods>Transformations>get_inverse_fourier_transform: Line No. {str(line_number)}, {str(ex)}')

    def get_real_part(self,numpy_array_2d:np.ndarray) -> np.ndarray:
        try:
            return numpy_array_2d.real
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_method>Transformations>get_real_part: Line No. {str(line_number)}, {str(ex)}')

class Laplace:
    def __init__(self) -> None:
        pass

    def get_laplace(self, numpy_array_2d:np.ndarray, mode=None) -> np.ndarray:
        try:
            if (mode is None):
                mode = Configuration.laplac_padding_mode
            return (ndimage.laplace(numpy_array_2d , mode=mode))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_methods>Laplace>get_laplace: Line No. {str(line_number)}, {str(ex)}')

class Matrix_calculations:
    def __init__(self) -> None:
        pass

    def get_dot_product(self, numpy_array1:np.ndarray, numpy_array2:np.ndarray) -> np.ndarray:
        return numpy_array1.dot(numpy_array2) 

class Convolution:
    def __init__(self) -> None:
        pass

    def get_signal_convolve_2d(self, numpy_array_2d:np.ndarray, kernel:np.ndarray, mode:str = None, boundry:str = None):
        try:
            if (mode is None):
                mode = Configuration.signal_convolve_2d_mode
            if (boundry is None):
                boundry = Configuration.signal_convolve_2d__boundry
            return (convolve2d(numpy_array_2d,kernel,mode=mode,boundary=boundry))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_methods>Laplace>get_signal_convolve_2d: Line No. {str(line_number)}, {str(ex)}')
    def get_signal_convolve_2d(self, numpy_array_2d:np.ndarray, kernel:np.ndarray, mode:str = None, method:str = None):
        try:
            if (mode is None):
                mode = Configuration.signal_convolve_mode
            if (method is None):
                method = Configuration.signal_convolve_method
            return (convolve(numpy_array_2d,kernel,mode=mode,method=method))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_methods>Laplace>get_signal_convolve_2d: Line No. {str(line_number)}, {str(ex)}')
        
    def get_image_convolve_2d(self, numpy_array_2d:np.ndarray, kernel:np.ndarray, mode:str = None,):
        try:
            if (mode is None):
                mode = Configuration.image_convolve_mode
            return (ndimage.convolve(numpy_array_2d,kernel,mode=mode))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Numerical_methods>Laplace>get_image_convolve_2d: Line No. {str(line_number)}, {str(ex)}')
