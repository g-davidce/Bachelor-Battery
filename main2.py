import matplotlib.pyplot as plt
import pandas as pd
from mpmath import linspace
from scipy.interpolate import make_interp_spline
from sympy.physics.units import voltage
from sympy.stats.sampling.sample_numpy import numpy

df = pd.read_csv('TC23NMC03_CU_25deg.txt',
                 delimiter=' ',
                 skiprows=14)
df.columns = ["Time[h]", "DataSet" ,"t-Step[h]" ,"t-Set[h]", "Line", "Command", "U[V]", "I[A]", "Ah[Ah]", "Ah-Step", "Wh[Wh]", "T1[C]", "Cyc-Count", "State"]
df_filthered = df[["Time[h]","Command","U[V]","I[A]","Cyc-Count"]]
by_Command = df_filthered.groupby("Command")
voltage_filter=df_filthered[(df_filthered["Command"]=="Charge") ]
voltage_filter=voltage_filter[voltage_filter["Time[h]"]>80.0382497584259]

min_time=voltage_filter["Time[h]"].min()
max_time=voltage_filter["Time[h]"].max()
voltage_filter["NormTime"]=(voltage_filter["Time[h]"]-min_time)/(max_time-min_time)

plt.figure(figsize=(15,5))
plt.plot(voltage_filter["NormTime"],voltage_filter["U[V]"])
#plt.scatter(voltage_filter["NormTime"],y,s=3)
plt.grid(True)
plt.tight_layout()
plt.savefig("myFig2.png",format='png',dpi=300)
plt.show()