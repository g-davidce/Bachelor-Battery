from unittest import TestCase
import pandas as pd

from cellData import cellData


class TestcellData(TestCase):
    def test_plot_data(self):
        df = pd.read_csv(
            r"G:\GitHub\Bachelor-Battery\HalfcellData\TC23LFP01_CU_25deg.txt",
            sep=" ",
            encoding="utf-8"
        )
        lfp=cellData("LFP",df)
        lfp.plot_data()