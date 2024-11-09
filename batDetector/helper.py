import numpy as np
import pandas as pd

import Celldata
from constants import LITHIATION,VOLTAGE

def string_is_float(string: str):
    try:
        float(string)
        return True
    except ValueError:
        return False

def normalize(arr):
    """
    Normalize given input of type array

    @param arr: Input Array of various types
    @return: Normalized Array
    """
    return (arr - np.min(arr))/(np.max(arr) - np.min(arr))

def interpolate_halfcell_data(halfcell_data_list:list[Celldata], steps:int):
    for index,cell in enumerate(halfcell_data_list):

        df = cell.get_data().copy(deep=True)
        df_new = np.linspace(df[LITHIATION].min(), df[LITHIATION].max(),steps)

        # Interpolate to extend granularity
        df_interp=pd.DataFrame({LITHIATION:df_new})
        df_interp[VOLTAGE]=np.interp(df_new,df[LITHIATION],df[VOLTAGE])

        # Replace old Dataframe with more points
        halfcell_data_list[index].set_data(df_interp)

def read_halfcell_data(dirname: str):
    return NotImplemented