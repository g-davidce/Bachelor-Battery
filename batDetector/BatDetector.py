from logging import fatal

import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt
import Celldata
import time

from os import listdir
from os.path import isfile, join
from pathlib import Path

from constants import LITHIATION
from helper import interpolate_cell_data

from parser import read_halfcell_data_csv, read_cell_data_csv

"""
Data Section
"""
anodes_dir=r"../halfCellAnodes"
cathodes_dir= r"../halfCellCathodes"
ocv_dir=r"../iOCVData"
cwd=Path.cwd()

#define delta for steps
deltaSteps=0.1
num_data_points=int(100 / deltaSteps)

def calc_composition(delta:float=0.1, order:int=5, parameter_guess:[float]=[0.1, 0.99, 0.99, 0.01]):
    path_anodes=(cwd / anodes_dir).resolve()
    path_cathodes=(cwd / cathodes_dir).resolve()
    path_iocv=(cwd / ocv_dir).resolve()

    halfcell_anodes = read_cell_data_csv(path_anodes,True,True)
    halfcell_cathodes = read_cell_data_csv(path_cathodes, True,False)

    i_ocv_data = read_cell_data_csv(path_iocv,False,delimiter=" ")
    ocv_cell_soc = np.linspace(0, 1, num_data_points)

    def objective(full_cell:Celldata, half_cell_pos:Celldata, half_cell_neg:Celldata, initial_guess=None):
        if initial_guess is None:
            initial_guess = [0.1, 0.99, 0.99, 0.01]
        interpolate_cell_data([full_cell], num_data_points)
        interpolate_cell_data([half_cell_pos], num_data_points, bounds=initial_guess[:2])
        interpolate_cell_data([half_cell_neg], num_data_points, bounds=initial_guess[-2:])

        return NotImplemented

    for cell_i_ocv in i_ocv_data:
        for cell_anode in halfcell_anodes:
            for cell_cathode in halfcell_cathodes:

                objective(cell_i_ocv,cell_anode,cell_cathode)




    #interpolate_cell_data(halfcell_anodes, num_data_points, order=order)
    #interpolate_cell_data(halfcell_cathodes, num_data_points, order=order)
    #interpolate_cell_data(i_ocv_data, num_data_points, order=order)

def calc_rmse(cell_full:pd.DataFrame, cell_half_pos:pd.DataFrame, cell_half_neg:pd.DataFrame):
    return NotImplemented

if __name__ == "__main__":
    start_time = time.time()
    calc_composition(order=5)
    end_time = time.time()
    print(end_time - start_time)