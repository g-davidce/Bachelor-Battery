from unittest import TestCase

import pandas as pd

import cellData as cd


class TestcellData(TestCase):
    def init(self,path,sep):
        self.df = pd.read_csv(
            path,
            sep=sep,
            encoding="utf-8"
        )


    def test_plot_data(self):
        self.init(r"G:\GitHub\Bachelor-Battery\iOCVData\TC23LFP01_CU_25deg.txt"," ")
        lfp = cd.cellData("LFP", self.df, is_half_cell=False)
        lfp.plot_data()

    def test_check_orientation(self):
        path=r"G:\GitHub\Bachelor-Battery\HalfCellData\LFP, Prada2012.csv"
        sep=","
        self.init(path,sep)
        lfp = cd.cellData("LFP", self.df, is_half_cell=True,is_pos=False)
        lfp.plot_data()
        self.init(path, sep)
        lfp = cd.cellData("LFP", self.df, is_half_cell=True, is_pos=True)
        lfp.plot_data()