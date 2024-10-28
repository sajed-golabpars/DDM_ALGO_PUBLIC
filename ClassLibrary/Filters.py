import Configuration
import Numerical_methods
import extensions
import copy
import traceback
import math
import numpy as np
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Coefficients:
    G_coefficint_axisymmetric:np.ndarray = None
    F_coefficint_axisymmetric:np.ndarray = None
    G_coefficint_wrapped_around:np.ndarray = None
    F_coefficint_wrapped_around:np.ndarray = None
    G_Fourier_coefficint_wrapped_around:np.ndarray = None
    F_Fourier_coefficint_wrapped_around:np.ndarray = None
    mesh_row_x_axis:list = None
    mesh_row_y_axis:list = None
    def __init__(self) -> None:
        pass

    def generate_G_coeficient_axisymmetric(self, kernel_length:int = None, x_interval:float = None,y_interval:float = None,EPrime:float=None):
        
        try:
            if(kernel_length is None):
                kernel_length = Configuration.coefficient_kernel_length
            if(x_interval is None):
                x_interval = Configuration.x_interval
            if(y_interval is None):
                y_interval = Configuration.y_interval
            if(EPrime is None):
                EPrime = Configuration.EPrime
            if(not (kernel_length % 2)):
                raise Exception("Filters>Coefficients>generate_G_Coeficient_axisymmetric: The filter size sould be an even number. Please insert an ODD number like: 3 or 5 or 7 or 65 or etc.")   
            
            half_length = int((kernel_length-1)/2)
            x_values = []
            y_values = []
            for i in range(-half_length,half_length+1):
                x_values.append(round(i*x_interval, Configuration.decimal_accuracy))
                y_values.append(round(i*y_interval, Configuration.decimal_accuracy))

            self.mesh_row_x_axis = x_values.copy()
            self.mesh_row_y_axis = y_values.copy()

            g_function_analytical = lambda x,y: round((2/((np.pi*EPrime)*(math.sqrt(x**2 + y**2)))),Configuration.decimal_accuracy)
            _row = []
            _discreet_g = []
            np.ones((kernel_length,kernel_length))
            for y_distance in y_values:
                _row.clear()
                for x_distance in x_values:
                    if(x_distance == 0 and y_distance == 0):
                        _row.append(g_function_analytical(x=Configuration.instead_of_zero, y=Configuration.instead_of_zero))
                    else:
                        _row.append(g_function_analytical(x=x_distance, y=y_distance))
                _discreet_g.append(copy.deepcopy(_row))
            
            self.G_coefficint_axisymmetric:np.ndarray = np.array(_discreet_g)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Filters>Coefficients>generate_G_coeficient_wrapped_around: Line No. {str(line_number)}, {str(ex)}')

    def generate_F_coefficient_axisymmetric(self,):
        try:
            if(self.G_coefficint_axisymmetric is None):
                raise Exception("Please first generate the axi-symmetric G coefficient using the function generate_G_coeficient_axisymmetric()")
            laplace = Numerical_methods.Laplace()
            self.F_coefficint_axisymmetric = laplace.get_laplace(numpy_array_2d = self.G_coefficint_axisymmetric)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Filters>Coefficients>generate_G_coeficient_wrapped_around: Line No. {str(line_number)}, {str(ex)}')

    def generate_G_coeficient_wrapped_around(self,):
        try:
            if(self.G_coefficint_axisymmetric is None):
                raise Exception("Please first generate the axi-symmetric G coefficient using the function generate_G_coeficient_axisymmetric()")   
            self.G_coefficint_wrapped_around = extensions.generate_wrap_around(axi_symmetric_2d_matrix=self.G_coefficint_axisymmetric)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Filters>Coefficients>generate_G_coeficient_wrapped_around: Line No. {str(line_number)}, {str(ex)}')

    def generate_F_coeficient_wrapped_around(self,):
        try:
            if(self.G_coefficint_axisymmetric is None):
                raise Exception("Please first generate the axi-symmetric G coefficient using the function generate_G_coeficient_axisymmetric()")   
            self.F_coefficint_wrapped_around = extensions.generate_wrap_around(axi_symmetric_2d_matrix=self.F_coefficint_axisymmetric)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Filters>Coefficients>generate_F_coeficient_wrapped_around: Line No. {str(line_number)}, {str(ex)}')
