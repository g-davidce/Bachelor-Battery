from os import listdir
from shutil import move
from os.path import isfile, join, basename, exists

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

anodes_dir=r"G:\GitHub\Bachelor-Battery\halfCellAnodes"
kathodes_dir= r"/halfCellCathodes"
halfCells_dir=r"F:\Uni\Bachelor\Data\Halbzelldaten"

def log_filter(dataframe, filter_val, colName):
    if filter_val>=0:
        return dataframe[dataframe[colName] > filter_val]
    else:
        return dataframe[dataframe[colName] <= abs(filter_val)]

def display_log(dataframe, xCol, yCol, fname):
    dataframe.plot(x=xCol,y=yCol)
    plt.title(fname)
    plt.show()

def read_log(path):
    return batParser.read_basytec(path)

def save_dataframe(path, dataframe):
    dataframe.to_csv(
        path_or_buf=path,
        sep=' ',
        header=True,
        mode='w',
        index=False
    )

def extract_q_ocv(file_path, time_val=None):
    user_input="0"
    filter_val=0.0
    df = read_log(file_path)
    df_display=df.copy()
    if time_val is not None:
        df = log_filter(df, time_val, "~Time[h]")
    else:
        while True:
            user_input=input("Enter Value or press a \n")
            if user_input=="a":
                del df_display
                df = log_filter(df, filter_val, "~Time[h]")
                break
            else:
                filter_val=float(user_input)
            df_display=log_filter(df_display, filter_val, "~Time[h]")
            display_log(df_display, xCol="~Time[h]", yCol="U[V]")
            df_display=df.copy()

    prev_command=""
    prev_voltage=""
    q_ocv=[]

    for index, row in df.iterrows():
        current_command=row["Command"]
        current_voltage=row["U[V]"]
        if index==0:
            prev_command=current_command
            prev_voltage=current_voltage

        if prev_command.lower() == "pause":
            if current_command!=prev_command:
                q_ocv.append([row["~Time[h]"],current_voltage])

        prev_command=current_command
        prev_voltage=current_voltage

    return create_df_from_data(q_ocv)

def worker(path):
    data_files = [files for files in listdir(path) if isfile(join(path, files))]
    data_files = [join(path,files) for files in data_files]

    for file in data_files:
        print(file)
        str_path = join(clearing_dir, basename(file))
        print(str_path)
        df = extract_q_ocv(file)
        save_dataframe(str_path, df)
        move(file,r"F:\Uni\Bachelor\Data\CU_BOL_Basytec_archieve")

def create_df_from_data(q_ocv, fname):
    df_qocv = pd.DataFrame(q_ocv, columns=["SOC in %", "U[V]"])
    min_time = df_qocv["SOC in %"].min()
    max_time = df_qocv["SOC in %"].max()
    df_qocv["SOC in %"] = (df_qocv["SOC in %"] - min_time) / (max_time - min_time)
    display_log(df_qocv, xCol="SOC in %", yCol="U[V]", fname=fname)
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

def readHalfCellData():
    halfcellFiles = [files for files in listdir(halfCells_dir) if isfile(join(halfCells_dir, files))]
    for halfCell in halfcellFiles:
        filename=join(halfCells_dir,halfCell)
        df=pd.read_csv(
            filename,
        sep=",",
        encoding="ansi")
        maximum=df["OCV"].max()
        minimum=df["OCV"].min()
        if minimum > 0.0 and maximum < 2.0:
            moveToAnodes(halfCell)
        if minimum > 0.0 and maximum > 2.0 and not "graphite" in halfCell.lower():
            moveToKathodes(halfCell)
def moveToAnodes(fname):
    print("Moving to Anodes")
    move(join(halfCells_dir,fname),join(anodes_dir,fname))
    return  NotImplemented

def moveToKathodes(fname):
    print("Moving to Kathodes")
    move(join(halfCells_dir, fname), join(kathodes_dir, fname))
    return NotImplemented
# df=extract_qOCV(90)
# saveDataframe(clearing_dir+r"\TC23LFP01_CU_25deg.csv",df)
# worker(data_dir)
# post_process(clearing_dir
# displayLog()
readHalfCellData()