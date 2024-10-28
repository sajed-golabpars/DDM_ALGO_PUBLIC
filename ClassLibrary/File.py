import numpy as np
import pandas as pd
from ClassLibrary import extensions
from ClassLibrary import Configuration
from ClassLibrary import Pressure
import datetime
import copy
import traceback
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#Note for optimisation:
#1. Reduce the ndarray datatype from float64 to smaller size data types



class __Load__:
    loaded_CSV:pd.DataFrame = None
    loaded_CSV_header:pd.DataFrame = None
    file_full_path:str = None
    separator:str = None
    decimal_character:str = None
    encode_type:str = None
    basic_encode_type:str = None
    skip_rows:int = None
    nrows:int = None
    def __init__(self,source_name:str=None) -> None:
        if(source_name == None):
            self.file_full_path = None
            raise Exception("Please insert the file name.")
        elif(source_name.count('.') == 0):
                source_name = source_name + ".csv"
        self.file_full_path = os.path.join(Configuration.source_directory,source_name)
        self.separator:str = Configuration.separator
        self.decimal_character:str = Configuration.decimal_character
        self.encode_type:str = Configuration.encode_type
        self.basic_encode_type:str = Configuration.basic_encode_type
        self.skip_rows:int = Configuration.skip_rows
        self.nrows:int = Configuration.take_these_rows
    
    def from_csv(self, file_path:str = None,
                encode_type:str = None,
                skip: int= None,
                separator_charcacter: str = None,
                decimal_character:str = None,
                header = None,
                ):
        """ 
        Load CSV file and store it into class global variable "Loaded_CSV"
        Note: the default values are set based on the outputs of the device provided by the Micro-machining Department.

        Args:
            file_path (str, optional): Full pass to the csv file.
            encode_type (str, optional): by default it is set to "ISO-8859-1", but in case you would like to use different encoding, change it to the desired one.
            skip (int, optional): Some CSV files have redundan details in the first rows. Using this item you can determine how many rows should be ignored and skipped. Default: 15
            separator_charcacter (str, optional): Some CSV files provided by old versions, use ";" as separator or even other characters or symbols. you can change this if you need to. default: ','
            decimal_character (str, optional): Decimal character in different systems are determine with different punctuations. Default: ','
            header (_type_, optional): If there is any header in the CSV file and it should be loaded. Default: None
        """
        try:
            #Verify the Parameters
            if(file_path == None):
                file_path = self.file_full_path
            if (encode_type is None):
                encode_type = Configuration.basic_encode_type
            if(skip == None):
                skip = Configuration.skip_rows
            if(separator_charcacter == None):
                separator_charcacter = Configuration.separator
            if(decimal_character == None):
                decimal_character = Configuration.decimal_character

            if(not is_path_correct(file_path)):
                raise Exception(f'The file path ({file_path}) is not in a correct form or the file does not exist!. Please retry using a correct path.')
            
            #Load CSV file into Class Variable
            self.loaded_CSV = pd.read_csv(file_path,  
                                                encoding=encode_type,
                                                skiprows=skip,
                                                sep=separator_charcacter,
                                                decimal= decimal_character,
                                                header= header,
                                                )
            self.loaded_CSV_header = pd.read_csv(file_path, 
                                                encoding= encode_type,
                                                nrows=self.nrows, 
                                                sep=separator_charcacter,
                                                header=header,
                                                decimal=decimal_character,
                                                usecols=range(2)
                                                )
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Files>Load>load_from_csv: Line No. {str(line_number)}, {str(ex)}')

class __Save__:
    def __init__(self) -> None:        
        pass

    def to_csv(self,file_name:str,ndarray:np.ndarray,id_index_included:bool=False,is_header_included:bool=False):
        try:
            if(file_name.count('.') == 0):
                file_name = file_name + ".csv" 
            file_path = os.path.join(Configuration.destination_directory,file_name)
            pd.DataFrame(ndarray).to_csv(file_path,index=id_index_included,header=is_header_included)        
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Files>Save>to_csv: Line No. {str(line_number)}, {str(ex)}')

    def to_csv_make_auto_directory(self,file_name:str,ndarray:list,id_index_included:bool=False,is_header_included:bool=False):
        try:
            now = datetime.datetime.now()
            # Define the custom format pattern
            custom_format = '%d_%m_%Y'
            # Format the current time using the custom pattern
            formatted_time = now.strftime(custom_format)
            lastDigit = 1
            for directory in os.listdir(Configuration.destination_directory):
                directory = directory.split("_exp_")
                if(directory[0] == formatted_time):
                    lastDigit = int(directory[1]) + 1
            
            new_directory = formatted_time + "_exp_" + str(lastDigit).zfill(5)
            # Create the full path to the new directory
            new_directory_path = os.path.join(Configuration.destination_directory, new_directory)
            # Create the directory
            os.makedirs(new_directory_path, exist_ok=True)
            if(file_name.count('.') == 0):
                file_name = file_name + ".csv"
            file_path = os.path.join(new_directory_path,file_name)
            pd.DataFrame(ndarray).to_csv(file_path,index=id_index_included,header=is_header_included)        
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Files>Save>to_csv: Line No. {str(line_number)}, {str(ex)}')

    def to_csv_make_auto_directory(self,ndarrays_dictionary:dict,id_index_included:bool=False,is_header_included:bool=False) -> str:
        try:
            now = datetime.datetime.now()
            # Define the custom format pattern
            custom_format = '%Y_%m_%d'
            # Format the current time using the custom pattern
            formatted_time = now.strftime(custom_format)
            lastDigit = 1
            for directory in os.listdir(Configuration.destination_directory):
                directory = directory.split("_exp_")
                if(directory[0] == formatted_time):
                    lastDigit = int(directory[1]) + 1
            
            new_directory = formatted_time + "_exp_" + str(lastDigit).zfill(5)
            # Create the full path to the new directory
            new_directory_path = os.path.join(Configuration.destination_directory, new_directory)
            # Create the directory
            os.makedirs(new_directory_path, exist_ok=True)
                
            for key,value in ndarrays_dictionary.items():
                file_name = key + ".csv"
                file_path = os.path.join(new_directory_path,file_name)    
                pd.DataFrame(value).to_csv(file_path,index=id_index_included,header=is_header_included)    

            return  new_directory_path      #Output directory    
        except Exception as ex:
            line_number = traceback.extract_tb(ex.__traceback__)[-1].lineno
            raise Exception(f'Files>Save>to_csv: Line No. {str(line_number)}, {str(ex)}')

class Manager:
    separator:str = None
    decimal_character:str = None
    encode_type:str = None
    basic_encode_type:str = None
    skip_rows:int = None
    Save:__Save__ = None
    Load:__Load__ = None

    def __init__(self,source_directory:str=None,destination_directory:str=None,source_file_name:str=None) -> None:
        if(source_directory == None):
            source_directory = Configuration.source_directory
        if(destination_directory == None):
            destination_directory = Configuration.destination_directory
        if(source_file_name == None):
            source_file_name = Configuration.input_file_name
        self._loaded_CSV:pd.DataFrame = None
        self._loaded_CSV_header:pd.DataFrame = None
        self.separator:str = Configuration.separator
        self.decimal_character:str = Configuration.decimal_character
        self.encode_type:str = Configuration.encode_type
        self.basic_encode_type:str = Configuration.basic_encode_type
        self.skip_rows:int = Configuration.skip_rows
        self.Save = __Save__()
        self.Load = __Load__(source_file_name)
    
    @property
    def Loaded_CSV(self,) -> pd.DataFrame:
        return self.Load.loaded_CSV
    @property
    def Loaded_CSV_header(self,) -> pd.DataFrame:
        return self.Load.loaded_CSV_header

#==================================================================== Global Functions =================================================================

def is_path_correct(file_path:str = None) -> bool:
    if not os.path.exists(file_path):
        return False
    return True


#=======================================================================================================================================================

