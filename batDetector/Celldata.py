import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from constants import *


class Celldata:
    """
    This class represents cell data
    """

    def __init__(self, comp: str, curve: pd.DataFrame, is_half_cell: bool, is_neg: bool = False):
        """
        @param comp: Name of 1/2 cell composition
        @type comp: string
        @param curve: Dataframe
        @type curve: pandas.DataFrame
        """
        self._cell_composition = comp
        self._curve = curve
        self._is_half_cell = is_half_cell
        self._is_neg = is_neg

        if not is_half_cell:
            self.rename_columns([SOC, VOLTAGE])
            self._curve[SOC] = self.norm_curve(SOC)
        else:
            self.rename_columns([LITHIATION, VOLTAGE])
            self._curve[LITHIATION] = self.norm_curve(LITHIATION)
            self._curve = self._curve.sort_values(LITHIATION).reset_index()
        if self._is_half_cell:
            self.check_orientation()

    def plot_data(self):
        if not self._is_half_cell:
            self._curve.plot(x=SOC, y=VOLTAGE)
        else:
            self._curve.plot(x=LITHIATION, y=VOLTAGE)

        plt.show()
        plt.close()

    def rename_columns(self, new_columns: list[str]):
        old_cols = self._curve.columns
        for i in range(len(old_cols)):
            self._curve.rename(columns={old_cols[i]: new_columns[i]}, inplace=True)

    def check_orientation(self):
       self.ocv_flip_dataframe()

    def get_composition(self):
        return self._cell_composition

    def get_data(self):
        return self._curve

    def set_data(self, dataframe: pd.DataFrame):
        self._curve = dataframe

    def set_composition(self, comp: str):
        self._cell_composition = comp

    def ocv_flip_dataframe(self):
        start = self._curve[VOLTAGE].iat[0]
        end = self._curve[VOLTAGE].iat[-1]
        if self._is_neg:
            if start < end:
                self._curve[VOLTAGE] = self._curve[VOLTAGE].values[::-1]
        else:
            if start > end:
                self._curve[VOLTAGE] = self._curve[VOLTAGE].values[::-1]

    def get_is_halfcell(self):
        return self._is_half_cell

    def get_is_neg(self):
        return self._is_neg

    def norm_curve(self,colm):
        return (self._curve[colm] - self._curve[colm].min()) / (self._curve[colm].max() - self._curve[colm].min())
