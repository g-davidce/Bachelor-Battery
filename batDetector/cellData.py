import pandas as pd
import matplotlib.pyplot as plt

from batDetector.constants import VOLTAGE,SOC,LITHIATION
class cellData:
    """
    This class represents cell data
    """
    def __init__(self,comp:str, curve:pd.DataFrame, is_half_cell:bool):
        """
        @param comp: Name of 1/2 cell composition
        @type comp: string
        @param curve: Dataframe
        @type curve: pandas.DataFrame
        """
        self.cell_compositon=comp
        self.curve=curve
        self.is_half_cell=is_half_cell
        if not is_half_cell:
            self.rename_columns([SOC, VOLTAGE])
        else:
            self.rename_columns([LITHIATION,VOLTAGE])

    def plot_data(self):
        df=self.curve.copy()
        if not self.is_half_cell:
            df.plot(x=SOC,y=VOLTAGE)
        else:
            df.plot(x=LITHIATION, y=VOLTAGE)
        plt.show()

    def rename_columns(self, new_columns:list[str]):
        old_cols=self.curve.columns
        for i in range(len(old_cols)):
            self.curve.rename(columns={old_cols[i]: new_columns[i]},inplace=True)

    def getComposition(self):
        return self.cell_compositon

    def getData(self):
        return self.curve

    def setData(self,dataframe:pd.DataFrame):
        self.curve=dataframe

    def setComposition(self,comp:str):
        self.cell_compositon=comp