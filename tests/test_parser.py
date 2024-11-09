import pandas as pd
import batDetector.parser as batParser
from unittest import TestCase

from Celldata import Celldata
from helper import interpolate_halfcell_data


class Test(TestCase):
    def test_read_halfcell_data_csv(self):
        arr = batParser.read_halfcell_data_csv(r"F:\Uni\Bachelor\Data\Halbzelldaten")
        interpolate_halfcell_data(arr, 100)
        # test for graphite
        for cell in arr:
            if "LFP" in cell.get_composition().upper():
                cell.plot_data()



# class Test(TestCase):
#     def test_read_basytec(self):
#         batParser.read_basytec(r"G:\GitHub\Bachelor-Battery\iOCVData\TC23LFP01_CU_25deg.txt")
