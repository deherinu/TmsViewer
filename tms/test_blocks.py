from tms import Blocks, read_and_transform

__author__ = 'jc.forero47'
m=25

import os

test_dir = os.path.join(os.path.dirname(__file__),"data")
test_file = os.path.join(test_dir,"TMS-441.csv")


points = read_and_transform.read_csv_file(test_file)

fechas = [p.date for p in points]



my_list= Blocks.get_blocks(fechas)
print len(my_list)
print my_list