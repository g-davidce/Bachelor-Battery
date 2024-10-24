import pandas as pd

from batDetector.constants import TIME,COMMAND,VOLTAGE,CURRENT
from os import listdir
from os.path import isfile, join

from helper import string_is_float

names_dictionary={
    "Time[h]":TIME,
    "Command":COMMAND,
    "U[V]":VOLTAGE,
    "I[A]":CURRENT,

}

def lithiation_ok(val1: float):
    """
    Check if Lithitiation is below 1 and higher than 0
    @param val1: Lithitiation Value
    @type val1: float
    @return: Returns True if Lithitiation is in given Range
    @rtype: Boolean
    """
    if val1 >= 0 and val1 < 1:
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
    if val1 >= 0 and val1 < 6:
        return True
    else:
        return False

def read_halfcell_data_csv(path: str):
    """
    Read all data files from given directory and appends it to dictionary.
    Current Limitation are CSV with "," as delimiter

    @param path: Enter path to halfcell Data Path
    @type path: String
    @return: Dictionary with Halfcell Data, Name of Dataset is Key
    @rtype: dictionary
    """
    try:
        halfcellFiles = [files for files in listdir(path) if isfile(join(path,files))]
        dfList = {}
        for halfcellFile in halfcellFiles:
            if halfcellFile.endswith(".csv"):
                with open(join(path,halfcellFile),'r') as file:

                    dataOk=False
                    valArr=[]

                    for line in file:
                        lineSplit = line.split(",")

                        #check if first and second value are castable to float
                        if not string_is_float(lineSplit[0]) and not string_is_float(lineSplit[1]):
                            continue
                        else:
                            lithiationVal = float(lineSplit[0])
                            voltageVal = float(lineSplit[1])
                            if not lithiation_ok(lithiationVal) or not ocv_ok(voltageVal):
                                dataOk=False
                                break
                            else:
                                valArr.append((lithiationVal,voltageVal))
                                dataOk=True
                    if dataOk:
                        df=pd.DataFrame(valArr,columns=['Lithiation','Voltage'])
                        dfList[halfcellFile.split(".")[0]]=df
        return dfList




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
