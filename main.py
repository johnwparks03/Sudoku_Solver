from Constraints import *
from SudokuBoard import SudokuBoard
from SudokuCell import SudokuCell
from GUI import SudokuGUI
import tkinter as tk

root = tk.Tk()
app = SudokuGUI(root)
root.mainloop()