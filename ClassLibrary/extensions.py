import numpy as np
import pandas as pd
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Reference:
    """
    Using this extension you can easily store the reference of an object and return it for further uage. It is basically a wrapper that wraps any type. Note that wrappers are getting a copy of the original file. 
    """
    def __new__(cls, value) -> any:
        cls.value = value
        return cls.value

    def __init__(self, value:any) -> None:
        self.value = value

def generate_wrap_around(axi_symmetric_2d_matrix:np.ndarray) -> np.ndarray:
        width = axi_symmetric_2d_matrix.shape[0]
        center:int = int((width -1)/2)
        stack = []
        row = []
        shifted_index = lambda index: (index + center - width ) if( (index + center > width -1) ) else (index + center ) 
        for y_axis_index in range(width):
            index_y = shifted_index(y_axis_index)
            row.clear()
            for x_axis_index in range(width):
                index_x = shifted_index(x_axis_index)
                row.append(axi_symmetric_2d_matrix[index_y][index_x])
                if(index_x == width-1):
                    row.append(0.0)
            stack.append(row.copy())
            if(index_y == width-1):
                stack.append(np.zeros(width+1))
        return np.array(stack)

def print_as_DataFrame(numpy_array:np.ndarray, provide_space:bool=True, caption:str = None):
     data_frame = pd.DataFrame(numpy_array)
     if(provide_space):
          print("\n===================")
     if (caption is not None):
          print(f'{caption}:')

     print(data_frame)

     if(provide_space):
          print("\n-------------------\n")

def safe_float_comparison(a, b, decimal_accuracy:int): #e.g. : for  decimal_accuracy = 3, the difference has to be less than 0.001
    tolerance = 1*10**(-decimal_accuracy)
    return abs(a - b) < tolerance

def format_time(seconds:float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    formated_time:str = f"{hours:02}:{minutes:02}:{seconds:05.2f}"
    return formated_time

def normalize_the_matrix(matrix:np.ndarray, upper_bound=4500, scale=256):
     ratio = scale/upper_bound
     for i in range(matrix.shape[0]):
          for j in range(matrix.shape[1]):
               matrix[i,j] = (ratio)*matrix[i,j]
