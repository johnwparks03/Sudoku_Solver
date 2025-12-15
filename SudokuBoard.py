from Constraints import *
from SudokuCell import SudokuCell


class SudokuBoard():
    def __init__(self):
        self.constraints = []  # List of all constraints on the board
        self.board = self.create_empty_board()  # 2D list of SudokuCell objects

    def find_least_num_possible_cell(self):
        empty_cells = [cell for row in self.board for cell in row if cell.value == 0]
        min_cell = min(empty_cells, key=lambda c: len(c.possible_values), default=None)

        return min_cell
    
    def solve(self, update_callback):
        least_cell = self.find_least_num_possible_cell()
        while len(least_cell.possible_values) == 1:
            least_cell.set_value(least_cell.possible_values.pop())
            update_callback(least_cell.row, least_cell.col, least_cell.value)
            least_cell = self.find_least_num_possible_cell()
            if least_cell is None:
                break

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
