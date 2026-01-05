import json

from Constraints import *
from enums import *
from SudokuBoard import SudokuBoard

PREDEFINED_SUDOKUS_FILE = "predefined_sudokus.json"

def create_predefined_sudokus():
    #Return a list of SudokueBoard objects so that we cna loop through them with Load Sudoku button
    loaded_sudokus = []
    with open(PREDEFINED_SUDOKUS_FILE, 'r') as data:
        sudoku_data = json.load(data)
        predefined_sudokus = sudoku_data['predefined_sudokus']

        for predefined_sudoku in predefined_sudokus:
            sudoku_board = SudokuBoard()
            for row in range(9):
                for col in range(9):
                    value = predefined_sudoku['board'][row][col]
                    if value != 0:
                        sudoku_board.board[row][col].set_value(value)

            for constraint_type, constraint in predefined_sudoku['constraints'].items():
                match constraint_type:
                    case ConstraintsEnum.WHITE_KROPKI_DOT.value:
                        for affected_cells in constraint:
                            cell1_row, cell1_col = affected_cells[0]
                            cell2_row, cell2_col = affected_cells[1]

                            cell1 = sudoku_board.board[cell1_row][cell1_col]
                            cell2 = sudoku_board.board[cell2_row][cell2_col]

                            new_constraint = KropkiDotConstraint(
                                cells=[cell1, cell2],
                                type=KropkiTypeEnum.WHITE_DOT
                            )

                            sudoku_board.constraints.append(new_constraint)
                            cell1.constraints.append(new_constraint)
                            cell2.constraints.append(new_constraint)

                    case ConstraintsEnum.BLACK_KROPKI_DOT.value:
                        for affected_cells in constraint:
                            cell1_row, cell1_col = affected_cells[0]
                            cell2_row, cell2_col = affected_cells[1]

                            cell1 = sudoku_board.board[cell1_row][cell1_col]
                            cell2 = sudoku_board.board[cell2_row][cell2_col]

                            new_constraint = KropkiDotConstraint(
                                cells=[cell1, cell2],
                                type=KropkiTypeEnum.BLACK_DOT
                            )

                            sudoku_board.constraints.append(new_constraint)
                            cell1.constraints.append(new_constraint)
                            cell2.constraints.append(new_constraint)
                    case ConstraintsEnum.KILLER_CAGE.value:
                        print("IMPLEMENT FUNCTIONALITY TO LOAD KILLER AGE CONSTRAINTS")
                    case _:
                        continue

            loaded_sudokus.append(sudoku_board)
    return loaded_sudokus

def save_predefined_sudoku(board_values, board_constraints):
    new_predefined_sudoku = {
        'board': board_values,
        'constraints': board_constraints
    }

    try:
        with open(PREDEFINED_SUDOKUS_FILE, 'r') as data:
            sudoku_data = json.load(data)
        
        sudoku_data['predefined_sudokus'].append(new_predefined_sudoku)

        with open(PREDEFINED_SUDOKUS_FILE, 'w') as data:
            json.dump(sudoku_data, data, indent=4)


        sudoku_board = SudokuBoard()
        for row in range(9):
            for col in range(9):
                value = new_predefined_sudoku['board'][row][col]
                if value != 0:
                    sudoku_board.board[row][col].set_value(value)
        return True
    except Exception as e:
        return False
    
