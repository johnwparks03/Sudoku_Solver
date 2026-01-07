import copy

from Constraints import *
from SudokuCell import SudokuCell


class SudokuBoard():
    def __init__(self):
        self.constraints = []  # List of all constraints on the board
        self.board = self.create_empty_board()  # 2D list of SudokuCell objects

    def is_board_empty(self):
        if len(self.constraints) > 27: #27 is the number of row, column, and box constraints
            return False
        
        for row in self.board:
            for cell in row:
                if cell.value != 0:
                    return False
        return True

    def find_least_num_possible_cell(self):
        empty_cells = [cell for row in self.board for cell in row if cell.value == 0]

        #Sort empty cells by number of constrains
        empty_cells.sort(key=lambda cell: (len(cell.possible_values), -len(cell.constraints)))

        return empty_cells[0]

    
    def is_solved(self):
        #Check that each cell is filled
        for row in self.board:
            for cell in row:
                if cell.value == 0:
                    return False

        #Now check that all constraints are satisfied
        for constraint in self.constraints:
            if not constraint.verify_constraint():
                return False

        return True    

    def create_empty_board(self):
        #Create empty board
        board = [[SudokuCell(row, col) for col in range(9)] for row in range(9)]

        #Now add constraints
        for i in range(9):
            #Row constraints
            row_cells = [board[i][col] for col in range(9)]
            row_constraint = RowConstraint(row_cells)
            self.constraints.append(row_constraint)
            for cell in row_cells:
                cell.constraints.append(row_constraint)

            #Column constraints
            col_cells = [board[row][i] for row in range(9)]
            col_constraint = ColumnConstraint(col_cells)
            self.constraints.append(col_constraint)
            for cell in col_cells:
                cell.constraints.append(col_constraint)
        
        #Box constraints
        for box_row in range(3):
            for box_col in range(3):
                box_cells = []
                for i in range(3):
                    for j in range(3):
                        box_cells.append(board[box_row*3 + i][box_col*3 + j])
                box_constraint = BoxConstraint(box_cells)
                self.constraints.append(box_constraint)
                for cell in box_cells:
                    cell.constraints.append(box_constraint)
        
        return board
