from logging import fatal

import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt
import Celldata

from os import listdir
from os.path import isfile, join
from pathlib import Path
from helper import interpolate_cell_data, interpolate_halfcell_data

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

def calculate_composition(delta=0.1):
    path_anodes=(cwd / anodes_dir).resolve()
    path_cathodes=(cwd / cathodes_dir).resolve()
    path_iocv=(cwd / ocv_dir).resolve()

    halfcell_anodes = read_cell_data_csv(path_anodes,True,True)
    halfcell_cathodes = read_cell_data_csv(path_cathodes, True,False)
    i_ocv_data = read_cell_data_csv(path_iocv,False)

    interpolate_cell_data(halfcell_anodes, num_data_points)
    interpolate_cell_data(halfcell_cathodes, num_data_points)


    print()

if __name__ == "__main__":
    calculate_composition()