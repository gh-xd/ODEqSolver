from gui import Solver
from PyQt6.QtWidgets import QApplication
import sys 
from examples import *


app = QApplication(sys.argv)
ex = Solver()
sys.exit(app.exec())