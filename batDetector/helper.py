import numpy as np
import pandas as pd

import Celldata
from scipy.interpolate import CubicSpline as CSP
from constants import LITHIATION, VOLTAGE, SOC


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
    return (arr - arr.min(arr)) / (arr.max(arr) - arr.min(arr))


# Function to interpolate and normalize a dataframe
def interpolate_and_norm(df: pd.DataFrame, colm: str, voltage_col: str, steps: int, bounds: [float] = None):
    # Check if bounds are provided
    if bounds is not None:
        # Interpolate the values using cubic spline method within specified bounds
        x_new = np.linspace(bounds[0], bounds[1], steps)
        spl = CSP(df[colm], df[voltage_col])
        df_int_norm = pd.DataFrame({
                colm: x_new,
                voltage_col: spl(x_new)
        })
        # Normalize the interpolated column values
        df_int_norm[colm] = (df_int_norm[colm] - df_int_norm[colm].min()) / (df_int_norm[colm].max() - df_int_norm[colm].min())
        return df_int_norm
    else:
        # Interpolate the values using cubic spline method within the minimum and maximum values of the first column
        x_new = np.linspace(df[colm].min(), df[colm].max(), steps)
        spl = CSP(df[colm], df[voltage_col])
        result = pd.DataFrame({
                colm: x_new,
                voltage_col: spl(x_new)
        })
        # Normalize the interpolated column values
        result[colm] = (result[colm] - result[colm].min()) / (result[colm].max() - result[colm].min())
        return result

def interpolate(df: pd.DataFrame, colm: str, voltage_col: str, steps: int, bounds: [float]):
    x_new = np.linspace(bounds[0], bounds[1], steps)

    spl = CSP(df[colm], df[voltage_col])
    return pd.DataFrame(
        {
            colm: x_new,
            # voltage_col:np.interp(x_new,df[colm],df[voltage_col])
            voltage_col: spl(x_new)
        }
    )

def interpolate_halfcell(df: pd.DataFrame, steps: int, bounds=None):
    if bounds is None:
        bounds = [0.1, 0.99]
    df_int = interpolate_and_norm(df, colm=LITHIATION, voltage_col=VOLTAGE, steps=steps, bounds=bounds)
    # df_int_norm
    return df_int


def interpolate_fullcell(df: pd.DataFrame, steps: int):
    return interpolate_and_norm(df, colm=SOC, voltage_col=VOLTAGE, steps=steps)


def interpolate_cell_data(cell_data_list: list[Celldata], steps: int, bounds=None):
    if bounds is None:
        bounds = [0.1, 0.99, 0.01, 0.99]  # pos_min, pos_max, neg_min, neg_max

    for index, cell in enumerate(cell_data_list):
        if cell.get_is_halfcell():
            if cell.get_is_neg():
                df = interpolate_halfcell(cell.get_data(), steps, bounds=bounds[:2])
            else:
                df = interpolate_halfcell(cell.get_data(), steps, bounds=bounds[-2:])
        else:
            df = interpolate_fullcell(cell.get_data(), steps)
        cell_data_list[index].set_data(df)