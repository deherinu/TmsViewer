__author__ = 'jc.forero47'
from PyQt4 import uic
import os

directory = os.path.dirname(__file__)
ui_file = os.path.join(directory,"tms_viewer_gui.ui")
out_file_name = os.path.join(directory,"tms_viewer_gui.py")
out_file = open(out_file_name,"w")
uic.compileUi(ui_file,out_file)

