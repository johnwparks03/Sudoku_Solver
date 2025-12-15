import time
import tkinter as tk
from tkinter import messagebox

from SudokuBoard import SudokuBoard


class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")

        # 2D array to store entry widgets
        self.cells = [[None for _ in range(9)] for _ in range(9)]

        #Create the main UI
        self.create_grid()
        self.create_buttons()

        self.sudoku_board = SudokuBoard()

    def create_grid(self):
        #Main grid frame
        grid_frame = tk.Frame(self.root, bg="black")
        grid_frame.pack(padx=10, pady=10)

        #Create boxes
        for box_row in range(3):
            for box_col in range(3):
                box_frame  =tk.Frame(grid_frame, borderwidth=2, relief="solid", bg="black")
                box_frame.grid(row=box_row, column=box_col, padx=1, pady=1)

                #Create cells within box
                for cell_row in range(3):
                    for cell_col in range(3):
                        cell = tk.Entry(
                            box_frame,
                            width=3,
                            font=('Arial', 18, 'bold'),
                            justify='center',
                            borderwidth=1,
                            relief="solid"
                        )
                        cell.grid(row=cell_row, column=cell_col, padx=1, pady=1)

                        #Validate that value in cell is 1-9
                        validate_cmd = (self.root.register(self.validate_input), '%P')
                        cell.config(validate='key', validatecommand=validate_cmd)
                        
                        actual_row = box_row * 3 + cell_row
                        actual_col = box_col * 3 + cell_col
                        self.cells[actual_row][actual_col] = cell

    def validate_input(self, value):
        if value == "":
            return True
        if len(value) == 1 and value in "123456789":
            return True
        return False
    
    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        solve_btn = tk.Button(
            button_frame,
            text="Solve",
            command=self.solve,
            font=('Arial', 12),
            width=10,
            bg="#4CAF50",
            fg="white"
        )
        solve_btn.grid(row=0, column=0, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_board,
            font=('Arial', 12),
            width=10,
            bg="#f44336",
            fg="white"
        )
        clear_btn.grid(row=0, column=1, padx=5)

        self.status_label = tk.Label(
            self.root,
            text="Enter a valid Sudoku",
            font=('Arial', 10),
            fg='gray'
        )
        self.status_label.pack(pady=5)

    def get_board_values(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for row in range(9):
            for col in range(9):
                value = self.cells[row][col].get()
                if value:
                    board[row][col] = int(value)

        return board
    
    def update_cell(self, row, col, value):
        cell =self.cells[row][col]
        if value != 0:
            cell.delete(0, tk.END)
            cell.insert(0, str(value))
            cell.config(fg='blue')
    
    def clear_board(self):
        for row in range(9):
            for col in range(9):
                self.cells[row][col].delete(0, tk.END)
                self.cells[row][col].config(fg='black')
        self.status_label.config(text="Board cleared", fg='gray')


    def solve(self):
        self.status_label.config(text="Solving...", fg='orange')
        self.root.update()

        #Set values in SudokuBoard
        board = self.get_board_values()
        for row in range(9):
            for col in range(9):
                value = board[row][col]
                if value != 0:
                    self.sudoku_board.board[row][col].set_value(value)

        self.sudoku_board.solve(update_callback=self.update_cell)

        self.status_label.config(text="Solved!", fg='green')
        self.root.update()


