import pandas as pd

from constants import *
from os import listdir
from os.path import isfile, join

from Celldata import Celldata
from helper import string_is_float

names_dictionary={
    "Time[h]":TIME,
    "Command":COMMAND,
    "U[V]":VOLTAGE,
    "I[A]":CURRENT,
    "Lithiation":LITHIATION,
}

def lithiation_ok(val1: float):
    """
    Check if Lithiation is below 1 and higher than 0
    @param val1: Lithiation Value
    @type val1: float
    @return: Returns True if Lithiation is in given Range
    @rtype: Boolean
    """
    if 0 <= val1 < 1:
        return True
    else:
        return False

def ocv_ok(val1: float):
    """
    Check if OCV is below 6 and higher than 0
    @param val1: OCV Value
    @type val1: float
    @return: Returns True if OCV is in given Range
    @rtype: Boolean
    """
    if 0 <= val1 < 6:
        return True
    else:
        return False

def read_halfcell_data_csv(path: str, is_pos: bool, precision:int=3):
    """
    Read all data files from given directory and appends it to dictionary.
    Current Limitation are CSV with "," as delimiter

    @param is_pos: Giving cell is of type anode or cathode material
    @type is_pos: Boolean
    @param path: Enter path to halfcell Data Path
    @type path: String
    @return: list with halfcell data objects
    @rtype: list
    """
    try:
        halfcell_files = [files for files in listdir(path) if isfile(join(path,files))]
        df_list = []
        for halfcellFile in halfcell_files:
            if halfcellFile.endswith(".csv"):
                with open(join(path,halfcellFile),'r') as file:

                    data_ok=False
                    val_arr=[]

                    for line in file:
                        line_split = line.split(",")

                        #check if first and second value are castable to float
                        if not string_is_float(line_split[0]) and not string_is_float(line_split[1]):
                            continue
                        else:
                            lithiation_val = float(line_split[0])
                            voltage_val = float(line_split[1])
                            if not lithiation_ok(lithiation_val) or not ocv_ok(voltage_val):
                                data_ok=False
                                break
                            else:
                                val_arr.append((lithiation_val,voltage_val))
                                data_ok=True
                    if data_ok:
                        df=pd.DataFrame(val_arr,columns=[LITHIATION,VOLTAGE])
                        df=df.round(precision)
                        cell = Celldata(halfcellFile.split(".")[0], df, True, is_neg=is_pos)
                        df_list.append(cell)
        return df_list

    except IOError as e :
        print("IOError: %s" % e)
        return []

def read_cell_data_csv(data_dir: str, is_halfcell:bool, is_neg:bool=False, precision:int=5, delimiter:str= ","):
    df_list = []
    try:
        for files in listdir(data_dir):
            df = pd.read_csv(join(data_dir, files,),sep=delimiter)
            df = df.round(precision)
            cell = Celldata(files.split(".")[0], df, is_halfcell, is_neg=is_neg)
            df_list.append(cell)
        return df_list
    except IOError as e :
        print("IOError: %s" % e)
        return []

def read_basytec(filename, skip_delimiter='~', col_override=None, seperator=' '):
    skip_rows=0
    with open(filename,'r') as file:

        for line in file:
            #count skip rows
            if "~Time[h]" in line:
                break
            elif '~' in line:
               skip_rows+=1
            else:
                break
    print("Rows to skip: %s"%skip_rows)
    columns=["~Time[h]","Command","U[V]","I[A]","Cyc-Count"]
    if col_override is not None:
        print("TODO")
    df = pd.read_csv(
        filename,
        skiprows=skip_rows,
        usecols=columns,
        sep=seperator,
        encoding="ansi"
    )
    return df

