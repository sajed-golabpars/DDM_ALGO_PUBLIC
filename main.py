from ClassLibrary import BusinessLayer
from ClassLibrary import Configuration
import traceback
import datetime
import time
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
if __name__ == "__main__":
    try:

        businnes = BusinessLayer.algorithm_logic()
        businnes.run()
    except Exception as ex:
        # Extract and the traceback details
        tb = traceback.extract_tb(ex.__traceback__)
        frame = tb[-1]
        # Print the exception type, message, and trace back
        print("=============!!!!ERROR!!!!==============")
        print(f"Exception type: {type(ex).__name__}")
        print(f"Exception message: {ex}")
        print(f"Exception Details: File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}")
        print("==========EXECUTION TERMINATED==========")
        