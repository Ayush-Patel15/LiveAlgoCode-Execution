"""
- Class to perform CRUD operations on a pickle file
"""

## Necessary import Statements
import pickle


## Pickle class to perform
class PickleClass:
    ## Constructor
    def __init__(self, filepath:str):
        self.filepath = filepath

    ## Method to read the pickle file for credentials
    def read(self) -> dict:
        credentials = {}
        with open(self.filepath, 'rb') as file:
            credentials = pickle.load(file)
        return credentials

    ## Method to write to the pickle file, with updated credentials
    def write(self, data:object) -> bool:
        flag = False
        with open(self.filepath, 'wb') as file:
            pickle.dump(data, file)
            flag = True
        return flag
