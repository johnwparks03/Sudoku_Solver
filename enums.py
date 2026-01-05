from enum import Enum

class ConstraintsEnum(Enum):
    ROW = "row"
    COLUMN = "column"
    BOX = "box"
    WHITE_KROPKI_DOT = "white_kropki_dot"
    BLACK_KROPKI_DOT = "black_kropki_dot"
    KILLER_CAGE = "killer cage"

class KropkiTypeEnum(Enum):
    WHITE_DOT = 'white_kropki_dot'
    BLACK_DOT = 'black_kropki_dot'

class GUIState(Enum):
    EMPTY_BOARD = 'empty_board' #After clearing the borrd or the initial empty board
    SOLVING = 'solving' #While the solver is running
    SOLVED = 'solved' #After the board has been successfully solved
    INCORRECT_SOLVE = 'incorrect_solve' #After the solver fails to solve the board
    EDITED = 'edited' #When the user is manually editing the board
    LOADING_SUDOKU = 'loading_sudoku' #When the user is loading a predefined sudoku
    ADDING_CONSTRAINTS = 'adding_constraints' #When the user is adding constraints to the board
    ADDING_WHITE_KROPKI_DOT = 'adding_white_kropki_dot' #When the user is adding white kropki dot constraints
    ADDING_BLACK_KROPKI_DOT = 'adding_black_kropki_dot' #When the user is adding black kropki dot constraints
    ADDING_KILLER_CAGE = 'adding_killer_cage' #When the user is adding killer cage constraints

class GUIButtons(Enum):
    SOLVE = 'solve'
    CLEAR = 'clear'
    LOAD_SUDOKU = 'load_sudoku'
    LEFT_ARROW = 'left_arrow'
    RIGHT_ARROW = 'right_arrow'
    ADD_CONSTRAINTS = 'add_constraints'
    WHITE_KROPKI_DOT = 'white_kropki_dot'
    BLACK_KROPKI_DOT = 'black_kropki_dot'
    KILLER_CAGE = 'killer_cage'
    DONE_ADDING_CONSTRAINTS = 'done_adding_constrains'
    ADD_SELECTED_CONSTRAINT = 'add_selected_constraint'
    CANCEL_SELECTED_CONSTRAINT = 'cancel_selected_constraint'
    SAVE = 'SAVE'