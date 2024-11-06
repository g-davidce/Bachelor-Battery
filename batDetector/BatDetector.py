import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt
import cellData
from os import listdir
from os.path import isfile, join

from helper import interpolate_halfcell_data

from parser import read_halfcell_data_csv

"""
Data Section
"""

#define delta for steps
delta=0.1
points=int(100/delta)

def calculate_composition(delta=0.1):
    halfcell_data_path = r"F:\Uni\Bachelor\Data\Halbzelldaten"
    halfcell_data_dict = read_halfcell_data_csv(halfcell_data_path)

    interpolate_halfcell_data(halfcell_data_dict, points)
    print()

if __name__ == "__main__":
    calculate_composition()