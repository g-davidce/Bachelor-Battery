from os import listdir
from shutil import move
from os.path import isfile, join, basename, exists

from sympy.physics.units import current

import batDetector.parser as batParser
import matplotlib.pyplot as plt
import pandas as pd
import batDetector.constants as constants
from batDetector.helper import normalize
def list_has_dupes(mylist):
    myset=set(mylist)
    if len(myset)!=len(mylist):
        return True
    else:
        return False
clearing_dir=r"F:\Uni\Bachelor\Data\CU_BOL_Basytec_qOCV"
data_dir=r"F:\Uni\Bachelor\Data\CU_BOL_Basytec"

def logFilter(dataframe, filterVal,colName):
    if filterVal>=0:
        return dataframe[dataframe[colName]>filterVal]
    else:
        return dataframe[dataframe[colName] <= abs(filterVal)]

def displayLog(dataframe,xCol ,yCol ,fname):
    dataframe.plot(x=xCol,y=yCol)
    plt.title(fname)
    plt.show()

def readLog(path):
    return batParser.read_basytec(path)

def saveDataframe(path,dataframe):
    dataframe.to_csv(
        path_or_buf=path,
        sep=' ',
        header=True,
        mode='w',
        index=False
    )

def extract_qOCV(file_path,time_val=None):
    user_input="0"
    filterVal=0.0
    df = readLog(file_path)
    df_display=df.copy()
    if time_val is not None:
        df = logFilter(df, time_val, "~Time[h]")
    else:
        while True:
            user_input=input("Enter Value or press a \n")
            if user_input=="a":
                del df_display
                df = logFilter(df, filterVal, "~Time[h]")
                break
            else:
                filterVal=float(user_input)
            df_display=logFilter(df_display,filterVal,"~Time[h]")
            displayLog(df_display,xCol="~Time[h]",yCol="U[V]")
            df_display=df.copy()

    prev_command=""
    prev_voltage=""
    qOCV=[]

    for index, row in df.iterrows():
        current_command=row["Command"]
        current_voltage=row["U[V]"]
        if index==0:
            prev_command=current_command
            prev_voltage=current_voltage

        if prev_command.lower() == "pause":
            if current_command!=prev_command:
                qOCV.append([row["~Time[h]"],current_voltage])

        prev_command=current_command
        prev_voltage=current_voltage

    return create_df_from_data(qOCV)

def worker(path):
    data_files = [files for files in listdir(path) if isfile(join(path, files))]
    data_files = [join(path,files) for files in data_files]

    for file in data_files:
        print(file)
        str_path = join(clearing_dir, basename(file))
        print(str_path)
        df = extract_qOCV(file)
        saveDataframe(str_path,df)
        move(file,r"F:\Uni\Bachelor\Data\CU_BOL_Basytec_archieve")

def create_df_from_data(q_ocv, fname):
    df_qocv = pd.DataFrame(q_ocv, columns=["SOC in %", "U[V]"])
    min_time = df_qocv["SOC in %"].min()
    max_time = df_qocv["SOC in %"].max()
    df_qocv["SOC in %"] = (df_qocv["SOC in %"] - min_time) / (max_time - min_time)
    displayLog(df_qocv, xCol="SOC in %", yCol="U[V]",fname=fname)
    return df_qocv

def post_process(path):
    files = [files for files in listdir(path) if isfile(join(path, files))]
    for file in files:
        with open(join(path, file), 'r') as q_ocv_data:
            #first=q_ocv_data.readline().split(" ")
            q_ocv_data.readline()
            mov_avg=0.0
            last_10_volts=[]
            qOCV=[]
            #qOCV.append([first[0],first[1]])
            idx=0
            for line in q_ocv_data:
                vals=line.split(" ")
                current_volt=float(vals[1])
                soc=float(vals[0])
                last_10_volts.append(current_volt)
                if mov_avg<current_volt:
                    qOCV.append([soc,current_volt])
                    if len(last_10_volts)>10:
                        last_10_volts.pop(0)
                    mov_avg=sum(last_10_volts)/len(last_10_volts)
                    idx+=1
                else:
                    break
            df_qocv = create_df_from_data(qOCV,file)
            fullpath=join(path,file)
            #saveDataframe(fullpath,df_qocv)

# df=extract_qOCV(90)
# saveDataframe(clearing_dir+r"\TC23LFP01_CU_25deg.csv",df)
#worker(data_dir)
post_process(clearing_dir)
#displayLog()