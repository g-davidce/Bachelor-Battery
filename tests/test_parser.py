import pandas as pd
import batDetector.parser as batParser
from unittest import TestCase



class Test(TestCase):
    def test_read_halfcell_data_csv(self):
        dict = batParser.read_halfcell_data_csv(r"F:\Uni\Bachelor\Data\Halbzelldaten")
        # test for graphite
        for key in dict.keys():
            if "graphite" in key.lower():
                df = dict[key]
                max_val = df['Voltage'].max()
                min_val = df['Voltage'].min()
                if max_val >= 2:
                    self.fail()
                if min_val < 0:
                    self.fail()


class Test(TestCase):
    def test_read_basytec(self):
        batParser.read_basytec(r"F:\Uni\Bachelor\Data\CU_BOL_Basytec\TC23LFP01_CU_25deg.txt")
