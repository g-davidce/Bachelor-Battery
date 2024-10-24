import numpy as np
import pandas as pd


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

def interpolate_halfcellData(halfcellData:dict[str,pd.DataFrame], steps:int):
    for key in halfcellData.keys():

        df = halfcellData[key].copy(deep=True)
        dfNew = np.linspace(df['Lithiation'].min(), df['Lithiation'].max(),steps)

        # Interpolate to extend granularity
        dfInterp=pd.DataFrame({'Lithiation':dfNew})
        dfInterp['Voltage']=np.interp(dfNew,df['Lithiation'],df['Voltage'])

        # Replace old Dataframe with more points
        halfcellData[key] = dfInterp