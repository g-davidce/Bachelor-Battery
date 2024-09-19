import matplotlib.pyplot as plt
from progressbar.terminal.colors import violet

meta_data=14
#[time,voltage]
voltage=[]
time=[]
graph_step=500
def readFile(path):
    try:
        with open(path,"r",encoding="latin1") as log:
            line_cnt=0
            cycle_cnt_prev=1
            last_stamp=0
            for row in log:
                line_cnt+=1
                if line_cnt<=meta_data:
                    continue
                line_split = row.strip().split(" ")
                if line_split[5]=="Charge":
                    voltage.append(float(line_split[6]))
                    time.append(float(line_split[0])-last_stamp)
                    if (int(line_split[12]) != cycle_cnt_prev): #new cycle
                        print(line_split[12])
                        cycle_cnt_prev=line_split[12]
                        last_stamp=time[len(time)-1]
                        plt.plot(time,voltage)
                        break
            plt.show()



    except FileNotFoundError:
        print("Datei konnte nicht geöffnet/gefunden werden")
    except Exception as e:
        print(f"Fehler: {e}")

def plotData(nthPoint):
    subset_volt = voltage[::nthPoint]
    subset_time = time[::nthPoint]
    plt.plot(subset_time,subset_volt)
    plt.show()

readFile("TC23NMC03_CU_25deg.txt")
print("done")
#plotData(5000)