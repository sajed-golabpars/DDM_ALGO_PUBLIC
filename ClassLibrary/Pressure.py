import traceback
import copy
import numpy as np
import Configuration
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class initial_pressure:
    
    def __init__(self, shape) -> None:
        self.P_Matrix:np.ndarray = None
        self.shape:tuple = shape


    def generate_initial_uniform_P(self, shape:tuple = None,initial_pressure:float = None, data_type:str=None):
        try:
            if(shape is None):
                shape = self.shape
            if(data_type is None):
                data_type = Configuration.data_type
            if(initial_pressure is None):
                initial_pressure = Configuration.initial_pressure
            self.P_Matrix = np.full(shape=shape,fill_value=initial_pressure,dtype=data_type)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Pressure>initial_pressure>generate_initial_uniform_P: Line No. {str(line_number)}, {str(ex)}')

    def generate_initial_uniform_P_Considering_pressure_Over_Padded_points(self, is_roughness_padded:bool=False,padding_size:int = None,pressure_over_padded_points:float=None,shape:tuple = None):
        try:
            if(shape is None):
                shape = self.shape
            self.generate_initial_uniform_P(shape=shape)
            if(padding_size is None):
                padding_size = Configuration.padding_size
            if(pressure_over_padded_points is None):
                pressure_over_padded_points:float = Configuration.initial_pressure_over_padded_points
            if(is_roughness_padded):
                self.P_Matrix[0:padding_size,:] = pressure_over_padded_points                                   #Top part
                self.P_Matrix[-padding_size-1:,:] = pressure_over_padded_points                                 #Bottom Part
                self.P_Matrix[padding_size:-padding_size,0:padding_size] = pressure_over_padded_points          #Left Part
                self.P_Matrix[padding_size:-padding_size,-padding_size:] = pressure_over_padded_points          #Right Part
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Pressure>initial_pressure>generate_initial_uniform_P_Considering_pressure_Over_Padded_points: Line No. {str(line_number)}, {str(ex)}')
    

class Pressure_kernel:
    def __init__(self) -> None:
        pass
    
    def get_p_kernel(self, pressure_matrix:np.ndarray, location:tuple = None, padding_size:int = None, p_type:str=None, ) -> np.ndarray:
        """
            Generates P kernel (a determined windows of the p matrix) out of the pressure Matrix.
        Args:
            pressure_matrix (np.ndarray): gets the reference of the pressure matrix
            location (tuple, optional): get the location of the point under computation as a tuple. e,g => (2,3)
            padding_size (int, optional): if the matrix is padded, it indicates the length of the padding for each direction. e.g => padding_size = 4 means the matrix is padded in each direction with 4 columns or rows.
            p_type (str, optional): determine how to generate the P_Kernel.
            accepted values: 
            None : checkes the configuration and retrieves the O kernel according to the configuration settings.
            'None': Retrieves the Pressures over the initial P with kernel size (for e.g. 7*7 numpy array), 
            'mirrored_rb': means mirrored considering repeating the right-bottom points considering (i,j) location as the center point, e.g. :
                                abcdef012345                                                  rqp pqr
            main matrix:        ghijkl012345      => e.g: kernel size is (4*6) =>             lkj|jkl
                                mnopqr012345          and (i,j) is (1,3)                      lkj jkl
                                stuwxy012345          and kernel half size is: (2*3)          rqp pqr
            'mirrored_lt': means mirrored considering repeating the left-top points considering (i,j) location as the center point, e.g.: 
                                abcdef012345                                                  bcd dcb
            main matrix:        ghijkl012345      => e.g: kernel size is (4*6) =>             hij|jih
                                mnopqr012345          and (i,j) is (1,3)                      hij jih
                                stuwxy012345          and kernel half size is: (2*3)          bcd dcb
        Raises:
            Exception: shows the line of error and a brief explanation

        Returns:
            np.ndarray: if the method runs without error, it returns a 2d numpy array with size of the kernel.
        """

        try:
            #inputs verification
            if(pressure_matrix is None):
                raise Exception('pressure matrix is None. Please make sure that the reference to the matrix is correct.')
            if(location is None):
                raise Exception('location is None. Please determine the location of the considering point on the pressure matrix.')
            if(padding_size is None):
                padding_size = Configuration.padding_size
            if(location[0] < padding_size or location[1] < padding_size): #location is equal to (i,j) tuple
                raise Exception('indexes are smaller than padding. No action is applied.')
            if(p_type is None):
                p_type = Configuration.p_type
            if(p_type is None):
                raise Exception('Please determine the p_type parameter.')
            
            _to_Cut = (int)((Configuration.coefficient_kernel_length + 1)/2)
            _i , _j = location
            _kernel:np.ndarray = None
            if(p_type.lower() == 'none'):
                _kernel = copy.deepcopy(pressure_matrix[_i -_to_Cut: _i + _to_Cut , _j - _to_Cut: _j + _to_Cut]) #e.g: for to_cut = 4 it retrieves 4 rows&columns before (i,j), till 4 rows&columns after (i,j) including (i,j) which then the kernel will be of size 8x8.
            elif(p_type.lower() == 'mirrored_rb'):
                _kernel = self.__get_P_kernel_mirrored_rightBottom_Side_Of_P_Matrix(p_matrix=pressure_matrix,padding=padding_size,i=_i,j=_j)
            elif(p_type.lower() == 'mirrored_lt'):
                _kernel = self.__get_P_kernel_Mirrored_LeftTop_Side_Of_P_Matrix(p_matrix=pressure_matrix,padding=padding_size,i=_i,j=_j)
            return _kernel
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Pressure>initial_pressure>get_p_kernel: Line No. {str(line_number)}, {str(ex)}')

    def __get_P_kernel_Mirrored_LeftTop_Side_Of_P_Matrix(self,
                        p_matrix:np.ndarray,
                        padding:int,
                        i:int = 0,
                        j:int = 0)-> np.ndarray:
        try:
            chunk_length = (int)((Configuration.coefficient_kernel_length + 1)/2)
            base_chunk = copy.deepcopy(p_matrix[i- chunk_length+1:i+1, j-chunk_length+1:j+1])
            kernel = np.zeros((2*chunk_length,2*chunk_length))
            kernel[0:chunk_length, 0: chunk_length ] = base_chunk
            #mirror to right side
            kernel_mirrored_left = np.flip(base_chunk, axis=1)
            kernel[0: chunk_length, chunk_length: ] = kernel_mirrored_left
            #mirror to botoom side
            kernel_mirrored_top = np.flip(base_chunk, axis=0)
            kernel[chunk_length:, 0: chunk_length] = kernel_mirrored_top
            #mirror to right-buttom corner
            kernel_mirrored_rb = np.flip(kernel_mirrored_left, axis=0)
            kernel[chunk_length:, chunk_length:] = kernel_mirrored_rb
            return copy.deepcopy(kernel)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Pressure>initial_pressure>__get_P_kernel_Mirrored_LeftTop_Side_Of_P_Matrix: Line No. {str(line_number)}, {str(ex)}')

    def __get_P_kernel_mirrored_rightBottom_Side_Of_P_Matrix(self,
                    p_matrix:np.ndarray,
                    padding:int,
                    i:int = 0,
                    j:int = 0) -> np.ndarray:
        try:
            chunk_length = (int)((Configuration.coefficient_kernel_length + 1)/2)
            base_chunk = copy.deepcopy(p_matrix[i:i+chunk_length, j:j+chunk_length])
            kernel = np.ones((2*chunk_length,2*chunk_length))
            kernel[chunk_length:, chunk_length: ] = base_chunk
            #mirror to left side
            kernel_mirrored_left = np.flip(base_chunk, axis=0)
            kernel[chunk_length:, 0: chunk_length ] = kernel_mirrored_left
            #mirror to top side
            kernel_mirrored_right = np.flip(base_chunk, axis=1)
            kernel[0: chunk_length, chunk_length: ] = kernel_mirrored_right
            #mirror to left-top corner
            kernel_mirrored_lt = np.flip(kernel_mirrored_right, axis=0)
            kernel[0:chunk_length, 0: chunk_length] = kernel_mirrored_lt
            return copy.deepcopy(kernel)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Pressure>initial_pressure>__get_P_kernel_mirrored_rightBottom_Side_Of_P_Matrix: Line No. {str(line_number)}, {str(ex)}')
        