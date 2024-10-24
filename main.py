import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv('TC23NMC03_CU_25deg.txt',
                 delimiter=' ',
                 skiprows=14)
df.columns = ["Time[h]", "DataSet" ,"t-Step[h]" ,"t-Set[h]", "Line", "Command", "U[V]", "I[A]", "Ah[Ah]", "Ah-Step", "Wh[Wh]", "T1[C]", "Cyc-Count", "State"]
df_filthered = df[["Time[h]","Command","U[V]","I[A]","Cyc-Count"]]
by_Command = df_filthered.groupby("Command")

plt.figure(figsize=(15,5))
plt.plot(df_filthered["Time[h]"],df_filthered["U[V]"])
plt.grid(True)
plt.tight_layout()
plt.savefig("myFig.png",format='png',dpi=300)
plt.show()