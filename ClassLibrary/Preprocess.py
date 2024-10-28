import numpy as np
import pandas as pd
import copy
import Configuration
import Numerical_methods
import Pressure
import Surfaces_gap
import Deflections
import traceback
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Preprocessor:
    Roughness_Matrix:np.ndarray = None
    Roughness_Matrix_Laplacian:np.ndarray = None
    Height_Matrix:np.ndarray = None
    P_Matrix:np.ndarray = None
    Delast_Matrix:np.ndarray = None
    Dplast_Matrix:np.ndarray = None
    Rmax:float = None
    Rmin:float = None
    Max_Point:tuple = None
    Min_Point:tuple = None
    x_interval:float = None
    y_interval:float = None
    def __init__(self) -> None:
        self.Roughness_Matrix:np.ndarray = None
        self.Height_Matrix:np.ndarray = None
        self.__is_roughness_padded__:bool = False
        self.laplac:Numerical_methods.Laplace = Numerical_methods.Laplace()
        
    def run(self,roughness_data_frame:pd.DataFrame,roughness_header_rows:pd.DataFrame=None,pad_size:int=None,data_Type:str=None) -> np.ndarray: 
        try:
            if (pad_size is None):
                pad_size = Configuration.padding_size
            if (data_Type is None):
                data_Type = Configuration.data_type
            #trim data and transform its data type into Configuration.dataType (default = float64)
            print("Data shifting ...")
            self.__shift_Nan_rows_to_left__(inputDataFrame = roughness_data_frame)
            self.Roughness_Matrix = roughness_data_frame.apply(lambda x: x.str.replace(',', '.') if x.dtype == 'object' else x).astype(data_Type)
            self.Roughness_Matrix = self.Roughness_Matrix.values #From now on the Roughness_Matrix is of type np.ndarray
            print("Extracting Details - Rmax, Rmin, (x,y) intervals ...")
            #get intervals
            self.x_interval = self.__check_calibration_information__(header_data_frame=roughness_header_rows)
            self.y_interval = self.x_interval
            Configuration.x_interval = self.x_interval
            Configuration.y_interval = self.y_interval
            #slice the roughness so we can work only on a chunk of the data
            if((Configuration.x_amount is not None) or (Configuration.y_amount is not None)):
                self.Roughness_Matrix = self.Roughness_Matrix[0:Configuration.x_amount,0:Configuration.y_amount]
            else:
                self.Roughness_Matrix = self.Roughness_Matrix
            #get aggregation values
            self.__aggregate__(ndarray_variable=self.Roughness_Matrix)
            Configuration.R_max = self.Rmax
            Configuration.R_min = self.Rmin
            Configuration.R_max_location = self.Max_Point
            Configuration.R_min_location = self.Min_Point
                     
            #add padding -> Roughness would get mirrored
            print("Add Padding ...")
            self.Roughness_Matrix = self.__padding_data_frames_mirrored__(array_to_get_padded=self.Roughness_Matrix,pad_size=pad_size)

            #calculate the laplacian of the roughness
            print("Calculate Laplace of Roughness Matrix ...")
            self.Roughness_Matrix_Laplacian = self.laplac.get_laplace(numpy_array_2d=self.Roughness_Matrix)
            #self.Roughness_Matrix_Laplacian = self.__padding_data_frames_wrapped__(array_to_get_padded=self.Roughness_Matrix_Laplacian,pad_size=pad_size)   

            #set height matrix
            gap = Surfaces_gap.Gap()
            print("Generate H Matrix ...")
            gap.generate_initial_H_Matrix_Considering_s(roughnes_matrix=self.Roughness_Matrix)
            self.Height_Matrix = gap.Height_Matrix
            #set Delast and Dplast Matrices as Zeros
            self.Delast_Matrix = np.zeros(shape= self.Roughness_Matrix.shape)
            self.Dplast_Matrix = np.zeros(shape= self.Roughness_Matrix.shape)
            #set initial pressure
            gap = Surfaces_gap
            initial_pressure = Pressure.initial_pressure(shape = self.Roughness_Matrix.shape)
            print("Generate initial P Matrix ...")
            initial_pressure.generate_initial_uniform_P_Considering_pressure_Over_Padded_points(is_roughness_padded=True,
                                                                                                pressure_over_padded_points=Configuration.initial_pressure_over_padded_points,
                                                                                                padding_size=pad_size,
                                                                                                shape=self.Roughness_Matrix.shape,
                                                                                                )
            self.P_Matrix = initial_pressure.P_Matrix
            #set Delast and Dplast
            deflections = Deflections.Elasto_plastic_deflections()
            deflections.generate_initial_Delast()
            deflections.generate_initial_Dplast()

            
            return self.Roughness_Matrix
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Preprocess>Preprocessor>run: Line No. {str(line_number)}, {str(ex)}')


    def get_Hmax_using_available_S(self, Delast_i0j0:float,
                                   Rmax:float = None, Rmin:float = None, 
                                   S:float = None,
                                   ) -> float:
        try:
            if((self.Rmax is None) or (self.Rmin is None)): #means the preprocess has not done so, the run() method is not called and executed yet.
                raise Exception("Please first call the Run() method so the preprocess will be applied and the values or Rmin and Rmax is calculated.")
            if(Rmax is None):
                Rmax = self.Rmax    #It is also possible to set the Rmax using the configuration settings within the Configuration file.
            if( Rmin is None):
                Rmin = self.Rmin    #It is also possible to set the Rmin using the configuration settings within the Configuration file.
            if(S is None):
                S = Configuration.approach_distance
            return (Rmax - Rmin + Delast_i0j0 - S)
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Preprocess.py>Preprocessor>get_Hmax_using_available_S: Line No. {str(line_number)}, {str(ex)}')
         
    def get_Hmax_using_available_S_with_adjustment(self,  Delast_i0j0:float, 
                                         Rmax:float, Rmin:float,S:float = None, 
                                         adjustmentForS:float = 0.0) -> float:
        try:
            if((self.Rmax is None) or (self.Rmin is None)): #means the preprocess has not done so, the run() method is not called and executed yet.
                raise Exception("Please first call the Run() method so the preprocess will be applied and the values or Rmin and Rmax is calculated.")
            if(Rmax is None):
                Rmax = self.Rmax    #It is also possible to set the Rmax using the configuration settings within the Configuration file.
            if( Rmin is None):
                Rmin = self.Rmin    #It is also possible to set the Rmin using the configuration settings within the Configuration file.
            if(S is None):
                S = Configuration.approach_distance
            return ((Rmax - Rmin + Delast_i0j0 - S) - S*(adjustmentForS))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Preprocess.py>Preprocessor>get_Hmax_using_available_S_with_adjustment: Line No. {str(line_number)}, {str(ex)}')
        
    def get_the_calculated_Hij_old(self, Delast_i0j0:float, point:tuple, Hmax:float) -> float:
        try:
            if((self.Rmax is None) or (self.Rmin is None)): #means the preprocess has not done so, the run() method is not called and executed yet.
                raise Exception("Please first call the Run() method so the preprocess will be applied and the values or Rmin and Rmax is calculated.")
            i,j = point
            return (Hmax + self.Rmin - self.Roughness_Matrix[i,j] - Delast_i0j0 + self.Dplast_Matrix[i,j])
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Preprocess.py>Preprocessor>get_the_calculated_Hij_old: Line No. {str(line_number)}, {str(ex)}')
        
    def __shift_Nan_rows_to_left__(self,inputDataFrame:pd.DataFrame, 
                    doPrintNumberOfAffectedRows:bool=False,)-> pd.DataFrame:
        try:
            i = 0
            counter = 0
            for index, row in inputDataFrame.iterrows():
                for item in row:
                    if(not pd.isna(item)):
                        break
                    i +=1
                if(i > 0):
                    row.shift(-i)
                    counter += 1
                i = 0
                inputDataFrame.iloc[index] = row
            if(doPrintNumberOfAffectedRows):
                print("Number of affected/shifted rows: ",counter)
            return inputDataFrame
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Preprocess>Preprocessor>shift_Nan_rows_to_left: Line No. {str(line_number)}, {str(ex)}')

    def __aggregate__(self, ndarray_variable:np.ndarray):          
        for i, row in enumerate(ndarray_variable):
            for j, value in enumerate(row):
                if self.Rmax is None or value > self.Rmax: #If there are more than one point with max value, only the location of the first one is stored in Max_Point
                    self.Rmax = value
                    self.Max_Point = (i, j)
                if self.Rmin is None or value < self.Rmin: #If there are more than one point with min value, only the location of the first one is stored in Min_Point 
                    self.Rmin = value
                    self.Min_Point = (i, j)                #Can be used as deepest valey
    
    def __check_calibration_information__(self, header_data_frame:pd.DataFrame) -> float:
    
        try:
            return float(str(header_data_frame.iloc[6,1]).replace(',','.'))
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Preprocess>Preprocessor>__CheckCalibrationInformation__: Line No. {str(line_number)}, {str(ex)}')

    def __calculate_initial_H_Matrix_Considering_s__(self,roughnes_matrix:pd.DataFrame = None, R_max:float = None,
                      approach_distance:float=None):
        if(roughnes_matrix is None):
            roughnes_matrix = self.Roughness_Matrix
        if(approach_distance is None):
            approach_distance = Configuration.approach_distance
        if(R_max is None):
            R_max =Configuration.R_max
        self.Height_Matrix = R_max - roughnes_matrix - approach_distance

    def __padding_data_frames_zero__(self,array_to_get_padded:np.ndarray,pad_size:int=1):                 #The border row and columns are excluded (dcb|abcd|cba)
        array_to_get_padded = np.pad(array_to_get_padded, ((pad_size, pad_size), (pad_size, pad_size)), mode='constant',constant_values=0)
        self.__is_roughness_padded__ = True
        return array_to_get_padded

    def __padding_data_frames_mirrored__(self,array_to_get_padded:np.ndarray,pad_size:int=1):                 #The border row and columns are excluded (dcb|abcd|cba)
        array_to_get_padded = np.pad(array_to_get_padded, ((pad_size, pad_size), (pad_size, pad_size)), mode='symmetric')
        self.__is_roughness_padded__ = True
        return array_to_get_padded
    def __padding_data_frames_reflected__(self,array_to_get_padded:np.ndarray,pad_size:int=1):                #The border row and columns are included (dcba|abcd|dcba)
        array_to_get_padded = np.pad(array_to_get_padded, ((pad_size, pad_size), (pad_size, pad_size)), mode='reflect')
        self.__is_roughness_padded__ = True
        return array_to_get_padded
    def __padding_data_frames_wrapped__(self,array_to_get_padded:np.ndarray,pad_size:int=1):                  #The data frame is repeated (abcd|abcd|abcd)
        array_to_get_padded = np.pad(array_to_get_padded, ((pad_size, pad_size), (pad_size, pad_size)), mode='wrap')
        self.__is_roughness_padded__ = True
        return array_to_get_padded
