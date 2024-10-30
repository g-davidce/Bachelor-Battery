import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join

from helper import interpolate_halfcellData
#from helper import interpolate_halfcellData
from parser import read_halfcell_data_csv

"""
Data Section
"""

halfcell_data_path= r"F:\Uni\Bachelor\Data\Halbzelldaten"
halfcell_data_dict=read_halfcell_data_csv(halfcell_data_path)

#define delta for steps
delta=0.1
points=int(100/delta)

interpolate_halfcellData(halfcell_data_dict, points)

#def calculate_composition(delta=0.1):
