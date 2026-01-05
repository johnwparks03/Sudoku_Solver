import copy

from enums import *


def solve(sudoku_board, state_update_callback, cell_update_callback):
    state_update_callback(GUIState.SOLVING)

    sudoku_board_copy = copy.deepcopy(sudoku_board)
    final_board = recursive_solve(sudoku_board_copy, cell_update_callback)
    if final_board:
        state_update_callback(GUIState.SOLVED)
    else:
        state_update_callback(GUIState.INCORRECT_SOLVE)
    return final_board


def recursive_solve(sudoku_board, cell_update_callback):
    if sudoku_board.is_solved():
        return sudoku_board

    least_cell = sudoku_board.find_least_num_possible_cell()
    possible_values = least_cell.possible_values.copy()

    #If it has 0 possible values -> backtrack
    if len(possible_values) == 0:
        return None

    #Try each possible value
    for value in possible_values:

        sudoku_board_copy = copy.deepcopy(sudoku_board)
        least_cell = sudoku_board_copy.board[least_cell.row][least_cell.col]

        least_cell.set_value(value)
        cell_update_callback(least_cell.row, least_cell.col, value)

        if recursive_solve(sudoku_board_copy, cell_update_callback):
            return sudoku_board_copy
        
        least_cell.set_value(0)
        cell_update_callback(least_cell.row, least_cell.col, 0)