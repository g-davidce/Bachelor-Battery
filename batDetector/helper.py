import numpy as np
import pandas as pd

import Celldata
from constants import LITHIATION,VOLTAGE,SOC

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

def interpolate(df:pd.DataFrame, colm:str, voltage_col:str, steps:int, precision:int=3):
    colm_ext=np.linspace(df[colm].min(),df[colm].max(),steps-len(df),endpoint=False)

    df_colm=pd.DataFrame({colm:colm_ext})
    df_upsampled = pd.concat([df,df_colm])
    df_upsampled=df_upsampled.sort_values(by=[colm],ignore_index=True)
    df_upsampled = df_upsampled.drop(1)
    df_upsampled=df_upsampled.interpolate(method='polynomial',order=5)

    return df_upsampled

def interpolate_halfcell(df:pd.DataFrame, steps:int, precision:int=5):
    return interpolate(df, colm=LITHIATION, voltage_col=VOLTAGE, steps=steps)

def interpolate_fullcell(df:pd.DataFrame, steps:int, precision:int=5):
    return interpolate(df, colm=SOC, voltage_col=VOLTAGE, steps=steps)

def interpolate_cell_data(cell_data_list:list[Celldata], steps:int, precision:int=5):
    for index,cell in enumerate(cell_data_list):
        if cell.get_is_halfcell():
            df = interpolate_halfcell(cell.get_data(), steps)
        else:
            df =interpolate_fullcell(cell.get_data(), steps)
        cell_data_list[index].set_data(df)