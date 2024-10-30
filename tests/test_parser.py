import pandas as pd
import batDetector.parser as batParser
from unittest import TestCase

from cellData import cellData
from helper import interpolate_halfcellData


class Test(TestCase):
    def test_read_halfcell_data_csv(self):
        arr = batParser.read_halfcell_data_csv(r"F:\Uni\Bachelor\Data\Halbzelldaten")
        interpolate_halfcellData(arr,100)
        # test for graphite
        for cell in arr:
            if "LFP" in cell.getComposition().upper():
                cell.plot_data()



# class Test(TestCase):
#     def test_read_basytec(self):
#         batParser.read_basytec(r"G:\GitHub\Bachelor-Battery\iOCVData\TC23LFP01_CU_25deg.txt")
