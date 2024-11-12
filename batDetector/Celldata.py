import pandas as pd
import matplotlib.pyplot as plt

from batDetector.constants import VOLTAGE, SOC, LITHIATION


class Celldata:
    """
    This class represents cell data
    """

    def __init__(self, comp: str, curve: pd.DataFrame, is_half_cell: bool, is_pos: bool = False):
        """
        @param comp: Name of 1/2 cell composition
        @type comp: string
        @param curve: Dataframe
        @type curve: pandas.DataFrame
        """
        self.cell_composition = comp
        self.curve = curve
        self.is_half_cell = is_half_cell
        self.is_pos = is_pos

        if not is_half_cell:
            self.rename_columns([SOC, VOLTAGE])
            self.curve[SOC] = self.norm_curve(SOC)
        else:
            self.rename_columns([LITHIATION, VOLTAGE])
            self.curve[LITHIATION] = self.norm_curve(LITHIATION)

        if self.is_half_cell:
            self.check_orientation()

    def plot_data(self):
        if not self.is_half_cell:
            self.curve.plot(x=SOC, y=VOLTAGE)
        else:
            self.curve.plot(x=LITHIATION, y=VOLTAGE)

        plt.show()
        plt.close()

    def rename_columns(self, new_columns: list[str]):
        old_cols = self.curve.columns
        for i in range(len(old_cols)):
            self.curve.rename(columns={old_cols[i]: new_columns[i]}, inplace=True)

    def check_orientation(self):
       self.ocv_flip_dataframe()

    def get_composition(self):
        return self.cell_composition

    def get_data(self):
        return self.curve

    def set_data(self, dataframe: pd.DataFrame):
        self.curve = dataframe

    def set_composition(self, comp: str):
        self.cell_composition = comp

    def ocv_flip_dataframe(self):
        start = self.curve[VOLTAGE].iat[0]
        end = self.curve[VOLTAGE].iat[-1]
        if self.is_pos:
            if start < end:
                self.curve[VOLTAGE] = self.curve[VOLTAGE].values[::-1]
        else:
            if start > end:
                self.curve[VOLTAGE] = self.curve[VOLTAGE].values[::-1]

    def get_is_halfcell(self):
        return self.is_half_cell

    def get_is_pos(self):
        return self.is_pos

    def norm_curve(self,colm):
        return (self.curve[colm] - self.curve[colm].min()) / (self.curve[colm].max() - self.curve[colm].min())
