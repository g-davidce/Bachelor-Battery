from unittest import TestCase

import batDetector.parser as batParser
from helper import ocv_flip_dataframe


class Test(TestCase):
    def test_ocv_orientation(self):
        arr = batParser.read_halfcell_data_csv(r"F:\Uni\Bachelor\Data\Halbzelldaten")
        for cell in arr:
            ocv_flip_dataframe(cell.get_data())
