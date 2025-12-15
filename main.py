from Constraints import *
from SudokuBoard import SudokuBoard
from SudokuCell import SudokuCell
from GUI import SudokuGUI
import tkinter as tk




test_board = {
    (0,0):3,
    (0,1):8,
    (0,2):5,
    (0,6):6,
    (0,7):7,
    (0,8):2,
    (1,0):1,
    (1,5):6,
    (1,7):4,
    (1,8):3,
    (2,0):2,
    (2,2):4,
    (2,3):3,
    (2,4):7,
    (2,5):5,
    (3,2):6,
    (3,8):5,
    (4,2):1,
    (4,4):5,
    (4,5):8,
    (4,7):2,
    (5,1):4,
    (5,2):7,
    (5,4):3,
    (5,5):2,
    (5,6):9,
    (5,7):8,
    (6,0):7,
    (6,5):3,
    (6,8):9,
    (7,0):4,
    (7,1):5,
    (7,4):8,
    (7,5):9,
    (7,7):6,
    (7,8):1,
    (8,0):6,
    (8,1):9,
    (8,3):5,
    (8,6):8,
    (8,7):3,
    (8,8):4
}

# for position, value in test_board.items():
#     row, col = position
#     sudoku_board.board[row][col].set_value(value)

# least_cell = sudoku_board.find_least_num_possible_cell()
# print(f"Cell with least possible values is at ({least_cell.row}, {least_cell.col}) with possible values: {least_cell.possible_values}")
# while len(least_cell.possible_values) == 1:
#     least_cell.set_value(least_cell.possible_values.pop())
#     least_cell = sudoku_board.find_least_num_possible_cell()
#     if least_cell is None:
#         break
#     print(f"Cell with least possible values is at ({least_cell.row}, {least_cell.col}) with possible values: {least_cell.possible_values}")

# print()

root = tk.Tk()
app = SudokuGUI(root)
root.mainloop()