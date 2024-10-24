import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join

from helper import interpolate_halfcellData
from parser import read_halfcell_data_csv

"""
Data Section
"""

halfcellDataPath=r"F:\Uni\Bachelor\Data\Halbzelldaten"
halfcellDataDict=read_halfcell_data_csv(halfcellDataPath)

#define delta for steps
delta=0.1
points=int(100/delta)

interpolate_halfcellData(halfcellDataDict, points)

#def calculate_composition(delta=0.1):
