import sys

from PyQt5.QtWidgets import QApplication

from Constraints import *
from GUI import SudokuGUI
from SudokuBoard import SudokuBoard
from SudokuCell import SudokuCell

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SudokuGUI()
    window.show()
    sys.exit(app.exec_())