import pandas as pd
import matplotlib.pyplot as plt

from batDetector.constants import VOLTAGE,SOC
class cellData:
    """
    This class represents cell data
    """
    def __init__(self,comp,curve):
        """
        @param comp: Name of 1/2 cell composition
        @type comp: string
        @param curve: Dataframe from 1/2 ocv
        @type curve: pandas.DataFrame
        """
        self.cell_compositon=comp
        self.curve=curve
        self.rename_columns([SOC, VOLTAGE])

    def plot_data(self):
        df=self.curve.copy()
        df.plot(x=SOC,y=VOLTAGE)
        plt.show()

    def rename_columns(self, new_columns):
        old_cols=self.curve.columns
        for i in range(len(old_cols)):
            self.curve.rename(columns={old_cols[i]: new_columns[i]},inplace=True)