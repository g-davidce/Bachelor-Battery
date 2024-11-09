from logging import fatal

import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt
import Celldata

from os import listdir
from os.path import isfile, join
from pathlib import Path
from helper import interpolate_halfcell_data

from parser import read_halfcell_data_csv

"""
Data Section
"""
anodes_dir=r"../halfCellAnodes"
cathodes_dir= r"../halfCellCathodes"
cwd=Path.cwd()

#define delta for steps
deltaSteps=0.1
points=int(100 / deltaSteps)

def calculate_composition(delta=0.1):
    path_anodes=(cwd / anodes_dir).resolve()
    path_cathodes=(cwd / cathodes_dir).resolve()

    halfcell_anodes = read_halfcell_data_csv(path_anodes,True)
    halfcell_cathodes = read_halfcell_data_csv(path_cathodes, False)

    #interpolate_halfcell_data(halfcell_data_dict, points)
    print()

if __name__ == "__main__":
    calculate_composition()