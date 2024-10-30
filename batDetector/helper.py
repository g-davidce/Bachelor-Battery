import numpy as np
import pandas as pd

from cellData import cellData
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

def interpolate_halfcellData(halfcellDataList:list[cellData], steps:int):
    for index,cell in enumerate(halfcellDataList):

        df = cell.getData().copy(deep=True)
        df_new = np.linspace(df[LITHIATION].min(), df[LITHIATION].max(),steps)

        # Interpolate to extend granularity
        df_interp=pd.DataFrame({LITHIATION:df_new})
        df_interp[VOLTAGE]=np.interp(df_new,df[LITHIATION],df[VOLTAGE])

        # Replace old Dataframe with more points
        halfcellDataList[index].setData(df_interp)