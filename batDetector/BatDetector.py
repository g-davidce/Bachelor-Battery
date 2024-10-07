import numpy as np
import pandas as pd
import scipy as sci
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join

from PyQt6.sip import array

"""
Data Section
"""
halfcellDataDict={}
halfcellDataPath=r"F:\Uni\Bachelor\Data\Halbzelldaten"
dataPoints=1500

def normalize(arr: array):
    """
    Normalize given input of type array

    @param arr: Input Array of various types
    @return: Normalized Array
    """
    return (arr - np.min(arr))/(np.max(arr) - np.min(arr))

def checkNumber(string: str):
    try:
        float(string)
        return True
    except ValueError:
        return False

def readHalfcellDataCSV(path: str):
    """
    Read all data files from given directory and appends it to dictionary.
    Current Limitation are CSV with "," as delimiter

    @param path: Enter path to halfcell Data Path
    @type path: String
    @return: List of filenames
    @rtype: Array[Strings]
    """
    try:
        halfcellFiles = [files for files in listdir(path) if isfile(join(path,files))]
        for halfcellFile in halfcellFiles:
            if halfcellFile.endswith(".csv"):
                with open(join(path,halfcellFile),'r') as file:
                    valArr=[]
                    for line in file:
                        lineSplit = line.split(",")

                        #check if first and second value are castable to float
                        if checkNumber(lineSplit[0]) and checkNumber(lineSplit[1]):
                            valArr.append((float(lineSplit[0]),float(lineSplit[1])))

                    halfcellDataDict[halfcellFile.split(".")[0]]=valArr

    except IOError as e :
        print("IOError: %s" % e)
        return []
    return halfcellFiles
