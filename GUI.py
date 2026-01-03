import copy
import json
import time
import tkinter as tk
from collections import defaultdict
from enum import Enum
from tkinter import messagebox



from Constraints import *
from enums import *
from SudokuBoard import SudokuBoard

PREDEFINED_SUDOKUS_FILE = "predefined_sudokus.json"

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.config(bg='lightblue')

        #Define which buttons are enabled during which states
        self.state_button_config = {
            GUIState.EMPTY_BOARD: ['solve', 'clear', 'load_sudoku', 'add_constraints'],
            GUIState.SOLVING: [],
            GUIState.SOLVED: ['clear', 'load_sudoku', 'add_constraints'],
            GUIState.INCORRECT_SOLVE: ['clear', 'load_sudoku'],
            GUIState.EDITED: ['solve', 'clear', 'load_sudoku', 'save', 'add_constraints'],
            GUIState.LOADING_SUDOKU: ['solve', 'clear', 'right_arrow', 'left_arrow', 'add_constraints'],
            GUIState.ADDING_CONSTRAINTS: ['white_kropki_dot', 'black_kropki_dot', 'killer_cage', 'done_adding_constraints'],
            GUIState.ADDING_WHITE_KROPKI_DOT: ['add', 'cancel'],
            GUIState.ADDING_BLACK_KROPKI_DOT: ['add', 'cancel'],
            GUIState.ADDING_KILLER_CAGE: ['add', 'cancel'],
        }
        self.state = GUIState.EMPTY_BOARD

        # 2D array to store entry widgets
        self.cells = [[None for _ in range(9)] for _ in range(9)]

        self.buttons = {}

        #Create the main UI
        self.create_grid()
        self.create_buttons()

        self.sudoku_board = SudokuBoard()

        self.predefined_sudokus = self.create_predefined_sudokus()
        self.current_predefined_index = 1

        self.constraint_selected_cells = []
        self.selected_constraint_type = None

    def set_state(self, new_state):
        prev_state = self.state
        self.state = new_state
    
        print(new_state)

        #Hide/show buttons based on state transitions
        if new_state == GUIState.LOADING_SUDOKU:
            #Show arrow buttons
            self.buttons['right_arrow'].grid()
            self.buttons['left_arrow'].grid()

            #Hide Load Sudoku button text
            self.buttons['load_sudoku'].grid_remove()
        elif prev_state == GUIState.LOADING_SUDOKU and new_state != GUIState.LOADING_SUDOKU:
            #Hide arrow buttons
            self.buttons['right_arrow'].grid_remove()
            self.buttons['left_arrow'].grid_remove()

            #Unhide Load Sudoku button text
            self.buttons['load_sudoku'].grid()


        if new_state == GUIState.ADDING_CONSTRAINTS:
            #Show constraint buttons
            self.buttons['white_kropki_dot'].grid()
            self.buttons['black_kropki_dot'].grid()
            self.buttons['killer_cage'].grid()
            self.buttons['done_adding_constraints'].grid()

            #Hide other buttons
            if prev_state == GUIState.ADDING_BLACK_KROPKI_DOT or prev_state == GUIState.ADDING_WHITE_KROPKI_DOT or prev_state == GUIState.ADDING_KILLER_CAGE:
                self.buttons['add'].grid_remove()
                self.buttons['cancel'].grid_remove()
            else:
                self.buttons['solve'].grid_remove()
                self.buttons['clear'].grid_remove()
                self.buttons['load_sudoku'].grid_remove()
                self.buttons['save'].grid_remove()
                self.buttons['add_constraints'].grid_remove()
        elif new_state != GUIState.ADDING_CONSTRAINTS and prev_state == GUIState.ADDING_CONSTRAINTS:
            #Hide constraint buttons
            self.buttons['white_kropki_dot'].grid_remove()
            self.buttons['black_kropki_dot'].grid_remove()
            self.buttons['killer_cage'].grid_remove()
            self.buttons['done_adding_constraints'].grid_remove()

            #Show other buttons
            if new_state == GUIState.ADDING_BLACK_KROPKI_DOT or new_state == GUIState.ADDING_WHITE_KROPKI_DOT or new_state == GUIState.ADDING_KILLER_CAGE:
                self.buttons['add'].grid()
                self.buttons['cancel'].grid()
            else:
                self.buttons['solve'].grid()
                self.buttons['clear'].grid()
                self.buttons['load_sudoku'].grid()
                self.buttons['save'].grid()
                self.buttons['add_constraints'].grid()

        state_config = self.state_button_config.get(new_state, {})
        #Disable/enable buttons based on new state
        for btn_key, btn in self.buttons.items():
            if btn_key in state_config:
                btn.config(state=tk.NORMAL)
            else:
                btn.config(state=tk.DISABLED, disabledforeground='black')

    def create_predefined_sudokus(self):
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

    def create_grid(self):
        #Main grid frame
        grid_frame = tk.Frame(self.root, bg="black")
        grid_frame.pack(padx=10, pady=10)

        #Create boxes
        for box_row in range(3):
            for box_col in range(3):
                box_frame  =tk.Frame(grid_frame, borderwidth=0, relief="solid", bg="gray")
                box_frame.grid(row=box_row, column=box_col, padx=0.5, pady=0.5)

                #Create cells within box
                for cell_row in range(3):
                    for cell_col in range(3):
                        cell = tk.Entry(
                            box_frame,
                            width=3,
                            font=('Arial', 18, 'bold'),
                            justify='center',
                            borderwidth=0,
                            relief="solid"
                        )
                        cell.grid(row=cell_row, column=cell_col, padx=1, pady=1)

                        cell.bind('<KeyRelease>', lambda event: self.set_state(GUIState.EDITED))

                        #Validate that value in cell is 1-9
                        validate_cmd = (self.root.register(self.validate_input), '%P')
                        cell.config(validate='key', validatecommand=validate_cmd)
                        
                        actual_row = box_row * 3 + cell_row
                        actual_col = box_col * 3 + cell_col
                        self.cells[actual_row][actual_col] = cell
        self.root.update()
    
    def validate_input(self, value):
        if value == "":
            return True
        if len(value) == 1 and value in "123456789":
            return True
        return False
    
    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        button_frame.config(bg='lightblue')

        solve_btn = tk.Button(
            button_frame,
            text="Solve",
            command=self.solve,
            font=('Arial', 12),
            width=15,
            bg="#4CAF50",
            fg="white"
        )
        solve_btn.grid(row=0, column=0, padx=5)
        self.buttons['solve'] = solve_btn

        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_board,
            font=('Arial', 12),
            width=15,
            bg="#f44336",
            fg="white"
        )
        clear_btn.grid(row=0, column=1, padx=5)
        self.buttons['clear'] = clear_btn

        load_sudoku_btn = tk.Button(
            button_frame,
            text="Load Sudoku",
            command=self.load_sudoku,
            font=('Arial', 12),
            width=30,
            bg="#2196F3",
            fg="white"
        )
        load_sudoku_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.buttons['load_sudoku'] = load_sudoku_btn

        right_arrow_btn = tk.Button(
            button_frame,
            text="→",
            command=self.increment_predefined_index,
            font=('Arial', 12),
            width=3,
            bg="#2196F3",
            fg="white"
        )
        right_arrow_btn.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        right_arrow_btn.grid_remove()
        self.buttons['right_arrow'] = right_arrow_btn

        left_arrow_btn = tk.Button(
            button_frame,
            text="←",
            command=self.decrement_predefined_index,
            font=('Arial', 12),
            width=3,
            bg="#2196F3",
            fg="white"
        )
        left_arrow_btn.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        left_arrow_btn.grid_remove()
        self.buttons['left_arrow'] = left_arrow_btn

        add_constraints_btn = tk.Button(
            button_frame,
            text="Add Constraints",
            command=lambda: self.set_state(GUIState.ADDING_CONSTRAINTS),
            font=('Arial', 12),
            width=15,
            bg="#FF9800",
            fg="white"
        )
        add_constraints_btn.grid(row=3, column=0, padx=5)
        self.buttons['add_constraints'] = add_constraints_btn

        white_kropki_dot_btn = tk.Button(
            button_frame,
            text="White Kropki Dot",
            command=lambda: self.select_constraint(ConstraintsEnum.WHITE_KROPKI_DOT),
            font=('Arial', 12),
            width=15,
            bg="#FFFFFF",
            fg="black"
        )
        white_kropki_dot_btn.grid(row=0, column=0, padx=5, pady=5)
        white_kropki_dot_btn.grid_remove()
        self.buttons['white_kropki_dot'] = white_kropki_dot_btn

        black_kropki_dot_btn = tk.Button(
            button_frame,
            text="Black Kropki Dot",
            command=lambda: self.select_constraint(ConstraintsEnum.BLACK_KROPKI_DOT),
            font=('Arial', 12),
            width=15,
            bg="#FFFFFF",
            fg="black"
        )
        black_kropki_dot_btn.grid(row=0, column=1, padx=5, pady=5)
        black_kropki_dot_btn.grid_remove()
        self.buttons['black_kropki_dot'] = black_kropki_dot_btn

        killer_cage_btn = tk.Button(
            button_frame,
            text="Killer Cage",
            command=lambda: self.select_constraint(ConstraintsEnum.KILLER_CAGE),
            font=('Arial', 12),
            width=30,
            bg="#FFFFFF",
            fg="black"
        )
        killer_cage_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        killer_cage_btn.grid_remove()
        self.buttons['killer_cage'] = killer_cage_btn

        add_btn = tk.Button(
            button_frame,
            text="Add",
            command=self.add_constraint,
            font=('Arial', 12),
            width=15,
            bg="green",
            fg="white"
        )
        add_btn.grid(row=0, column=0, columnspan=2, pady=5, padx=5)
        add_btn.grid_remove()
        self.buttons['add'] = add_btn

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_adding_costraint,
            font=('Arial', 12),
            width=15,
            bg="red",
            fg="white"
        )
        cancel_btn.grid(row=1, column=0, columnspan=2, padx=5)
        cancel_btn.grid_remove()
        self.buttons['cancel'] = cancel_btn

        done_adding_constraints_btn = tk.Button(
            button_frame,
            text="Done",
            command=lambda: self.set_state(GUIState.EDITED),
            font=('Arial', 12),
            width=30,
            bg="#9C27B0",
            fg="white"
        )
        done_adding_constraints_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        done_adding_constraints_btn.grid_remove()
        self.buttons['done_adding_constraints'] = done_adding_constraints_btn

        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self.save_board,
            font=('Arial', 12),
            width=15,
            bg="#9C27B0",
            fg="white"
        )
        save_btn.grid(row=3, column=1, padx=5)
        save_btn.config(state=tk.DISABLED, disabledforeground='black')
        self.buttons['save'] = save_btn

        button_frame.grid_columnconfigure(0, weight=1, uniform="col")
        button_frame.grid_columnconfigure(1, weight=1, uniform="col")

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
        self.root.update()

    def clear_board(self):
        self.set_state(GUIState.EMPTY_BOARD)
        for row in range(9):
            for col in range(9):
                self.cells[row][col].delete(0, tk.END)
                self.cells[row][col].config(fg='black')
        self.sudoku_board = SudokuBoard()

    def load_sudoku(self):
        predfined_sudoku = self.predefined_sudokus[self.current_predefined_index]
        self.clear_board()

        self.set_state(GUIState.LOADING_SUDOKU)

        self.sudoku_board = copy.deepcopy(predfined_sudoku)
        for row in range(9):
            for col in range(9):
                value = predfined_sudoku.board[row][col].value
                if value != 0:
                    cell = self.cells[row][col]
                    cell.delete(0, tk.END)
                    cell.insert(0, str(value))
                    cell.config(fg='black')

    def increment_predefined_index(self):
        self.current_predefined_index += 1
        if self.current_predefined_index >= len(self.predefined_sudokus):
            self.current_predefined_index = 0

        self.load_sudoku()

    def decrement_predefined_index(self):
        self.current_predefined_index -= 1
        if self.current_predefined_index < 0:
            self.current_predefined_index = len(self.predefined_sudokus) - 1

        self.load_sudoku()

    def select_constraint(self, constraint_type):
        self.enable_cell_selection()
        match constraint_type:
            case ConstraintsEnum.WHITE_KROPKI_DOT:
                self.set_state(GUIState.ADDING_WHITE_KROPKI_DOT)
                self.selected_constraint_type = ConstraintsEnum.WHITE_KROPKI_DOT
            case ConstraintsEnum.BLACK_KROPKI_DOT:
                self.set_state(GUIState.ADDING_BLACK_KROPKI_DOT)
                self.selected_constraint_type = ConstraintsEnum.BLACK_KROPKI_DOT
            case ConstraintsEnum.KILLER_CAGE:
                self.set_state(GUIState.ADDING_KILLER_CAGE)
                self.selected_constraint_type = ConstraintsEnum.KILLER_CAGE

    def add_constraint(self):
        def is_valid_kropki_selection(cells):
            if len(cells) != 2:
                return False
            
            #Ensure they are adjacent
            row1, col1 = cells[0]
            row2, col2 = cells[1]
            if abs(row1 - row2) + abs(col1 - col2) != 1:
                return False
            
            return True

        match self.selected_constraint_type:
            case ConstraintsEnum.WHITE_KROPKI_DOT:
                if is_valid_kropki_selection(self.constraint_selected_cells):
                    #Add white kropki dot constraint to SudokuBoard
                    affected_cells = [self.sudoku_board.board[r][c] for r, c in self.constraint_selected_cells]
                    new_constraint = KropkiDotConstraint(
                        cells=affected_cells,
                        type=KropkiTypeEnum.WHITE_DOT
                    )
                    self.sudoku_board.constraints.append(new_constraint)

                    self.draw_kropki_dot(
                        cell1=self.constraint_selected_cells[0],
                        cell2=self.constraint_selected_cells[1],
                        dot_type='white'
                    )

                    self.root.update()

                    #add constraint to the cells
                    for cell in affected_cells:
                        cell.constraints.append(new_constraint)
                else:
                    self.root.update()
                    return
            case ConstraintsEnum.BLACK_KROPKI_DOT:
                if is_valid_kropki_selection(self.constraint_selected_cells):
                    #Add black kropki dot constraint to SudokuBoard
                    affected_cells = [self.sudoku_board.board[r][c] for r, c in self.constraint_selected_cells]
                    new_constraint = KropkiDotConstraint(
                        cells=affected_cells,
                        type=KropkiTypeEnum.BLACK_DOT
                    )
                    self.sudoku_board.constraints.append(new_constraint)
                    self.root.update()

                    #Add constraint to the cells
                    for cell in affected_cells:
                        cell.constraints.append(new_constraint)
                else:
                    self.root.update()
                    return
            case ConstraintsEnum.KILLER_CAGE:
                pass 

        self.cancel_adding_costraint()

    def cancel_adding_costraint(self):
        self.constraint_selected_cells = []
        self.disable_cell_selection()
        self.set_state(GUIState.ADDING_CONSTRAINTS)

    def enable_cell_selection(self):
        #Enable cells to be selected, but not edited
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.config(state=tk.DISABLED, disabledbackground='white', disabledforeground='black', cursor='hand2')
                cell.bind('<Button-1>', lambda event, r=row, c=col: self.on_cell_click(r, c))

    def disable_cell_selection(self):
        #Disable cell selection and re-enable editing
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.config(state=tk.NORMAL, cursor='xterm')
                cell.unbind('<Button-1>')

    def on_cell_click(self, row, col):
        if (row, col) in self.constraint_selected_cells:
            self.constraint_selected_cells.remove((row, col))
            self.cells[row][col].config(disabledbackground='white')
        else:
            self.constraint_selected_cells.append((row, col))
            self.cells[row][col].config(disabledbackground='lightblue')
        self.root.update()

    def convert_constraints_to_json(self):
        constraints_json = defaultdict(list)

        for constraint in self.sudoku_board.constraints:
            match constraint:
                case KropkiDotConstraint():
                    cell1 = constraint.affected_cells[0]
                    cell2 = constraint.affected_cells[1]
                    cells = [(cell1.row, cell1.col), (cell2.row, cell2.col)]

                    constraints_json[constraint.type.value].append(cells)
                case KillerCageConstraint():
                    print("IMPLEMENT FUNCTIONALITY TO SAVE KILLER CAGE CONSTRAINTS")
                case _:
                    continue
        return constraints_json

    def save_board(self):
        board_values = self.get_board_values()
        board_constraints = self.convert_constraints_to_json()
        sudoku_to_save = {
            'board': board_values,
            'constraints': board_constraints
        }

        try:
            with open(PREDEFINED_SUDOKUS_FILE, 'r') as data:
                sudoku_data = json.load(data)
            
            sudoku_data['predefined_sudokus'].append(sudoku_to_save)

            with open(PREDEFINED_SUDOKUS_FILE, 'w') as data:
                json.dump(sudoku_data, data, indent=4)

            messagebox.showinfo("Save Successful", "Sudoku saved successfully!")

            sudoku_board = SudokuBoard()
            for row in range(9):
                for col in range(9):
                    value = sudoku_to_save['board'][row][col]
                    if value != 0:
                        sudoku_board.board[row][col].set_value(value)
            self.predefined_sudokus.append(sudoku_board)
        except Exception as e:
            messagebox.showerror("Save Failed", f"An error occurred while saving the Sudoku: {e}")

    def solve(self):
        self.set_state(GUIState.SOLVING)

        self.root.update()

        #Set values in SudokuBoard
        board = self.get_board_values()
        for row in range(9):
            for col in range(9):
                value = board[row][col]
                if value != 0:
                    self.sudoku_board.board[row][col].set_value(value)

        sudoku_board_copy = copy.deepcopy(self.sudoku_board)
        final_board = self.recursive_solve(sudoku_board_copy)
        if final_board:
            self.set_state(GUIState.SOLVED)
        else:
            self.set_state(GUIState.INCORRECT_SOLVE)
        self.root.update()

    def recursive_solve(self, sudoku_board):
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
            self.update_cell(least_cell.row, least_cell.col, value)
            # print(f"Trying {value} in cell at row {least_cell.row + 1} and col {least_cell.col + 1}")

            if self.recursive_solve(sudoku_board_copy):
                return sudoku_board_copy
            
            #Backtrack
            # print(f"{value} does not work in cell at row {least_cell.row + 1} and col {least_cell.col + 1}")
            least_cell.set_value(0)
            self.update_cell(least_cell.row, least_cell.col, 0)
