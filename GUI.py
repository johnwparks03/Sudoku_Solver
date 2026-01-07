import copy
import sys
from collections import defaultdict

from PyQt5.QtCore import QRectF, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QFont, QIntValidator, QPen, QLinearGradient
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

import predefined_sudoku_utils
import solver
from Constraints import *
from enums import *
from SudokuBoard import SudokuBoard


class SudokuGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        #Define which buttons are enabled during which states
        self.state_button_config = {
            GUIState.EMPTY_BOARD: [GUIButtons.SOLVE.value, GUIButtons.CLEAR.value, GUIButtons.LOAD_SUDOKU.value, GUIButtons.ADD_CONSTRAINTS.value],
            GUIState.SOLVING: [],
            GUIState.SOLVED: [GUIButtons.CLEAR.value, GUIButtons.LOAD_SUDOKU.value, GUIButtons.ADD_CONSTRAINTS.value],
            GUIState.INCORRECT_SOLVE: [GUIButtons.CLEAR.value, GUIButtons.LOAD_SUDOKU.value],
            GUIState.EDITED: [GUIButtons.SOLVE.value, GUIButtons.CLEAR.value, GUIButtons.LOAD_SUDOKU.value, GUIButtons.SAVE.value, GUIButtons.ADD_CONSTRAINTS.value],
            GUIState.LOADING_SUDOKU: [GUIButtons.SOLVE.value, GUIButtons.CLEAR.value, GUIButtons.LEFT_ARROW.value, GUIButtons.RIGHT_ARROW.value, GUIButtons.ADD_CONSTRAINTS.value],
            GUIState.ADDING_CONSTRAINTS: [GUIButtons.WHITE_KROPKI_DOT.value, GUIButtons.BLACK_KROPKI_DOT.value, GUIButtons.KILLER_CAGE.value, GUIButtons.DONE_ADDING_CONSTRAINTS.value],
            GUIState.ADDING_WHITE_KROPKI_DOT: [GUIButtons.ADD_SELECTED_CONSTRAINT.value, GUIButtons.CANCEL_SELECTED_CONSTRAINT.value],
            GUIState.ADDING_BLACK_KROPKI_DOT: [GUIButtons.ADD_SELECTED_CONSTRAINT.value, GUIButtons.CANCEL_SELECTED_CONSTRAINT.value],
            GUIState.ADDING_KILLER_CAGE: [GUIButtons.ADD_SELECTED_CONSTRAINT.value, GUIButtons.CANCEL_SELECTED_CONSTRAINT.value],
        }
        self.state = GUIState.EMPTY_BOARD

        self.cells = []
        self.buttons = {}

        self.sudoku_board = SudokuBoard()

        self.predefined_sudokus = predefined_sudoku_utils.create_predefined_sudokus()
        self.current_predefined_sudoku_index = 0

        self.constraint_selected_cells = []
        self.selected_constraint_type = None
        self.edit_mode = True #True when user can edit cells, False when user can select cells
        self.constraint_drawings = {}

        self.setWindowTitle("Sudoku Solver")
        self.cell_size = 60
        self.grid_size = 9

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: lightblue")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        #Create the graphics view and scene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setBackgroundBrush(QBrush(QColor("#f0f0f0")))

        #Set the size of the scene
        total_size = self.cell_size * self.grid_size
        self.scene.setSceneRect(0, 0, total_size, total_size)
        

        self.draw_grid()
        self.create_cells()

        self.view.setFixedSize(total_size + 3, total_size + 3)
        self.adjustSize()

        main_layout.addWidget(self.view)

        self.button_row_1 = QHBoxLayout()
        self.button_row_2 = QHBoxLayout()
        self.button_row_3 = QHBoxLayout()

        self.create_buttons()

        main_layout.addLayout(self.button_row_1)
        main_layout.addLayout(self.button_row_2)
        main_layout.addLayout(self.button_row_3)

        #Create toast notification label
        self.toast = QLabel(self)
        self.toast.setAlignment(Qt.AlignCenter)
        self.toast.setStyleSheet("""
            QLabel {
                background-color: lightgray;
                color: black;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.toast.hide()

    def refresh(self):
        self.scene.update()
        self.view.viewport().update()
        QApplication.processEvents()

    def show_toast_notification(self, message, duration=1000):
        self.toast.setText(message)
        self.toast.adjustSize()

        x = (self.width() - self.toast.width()) // 2
        y = self.height() - self.toast.height() - self.height() // 2
        self.toast.move(x, y)
        
        self.toast.show()

        self.toast.mousePressEvent = lambda event: self.toast.hide()

        QTimer.singleShot(duration, self.toast.hide)

    def set_state(self, new_state):
        prev_state = self.state
        self.state = new_state

        #Hide/Show arrow buttons to cycle predefined sudokus
        if new_state == GUIState.LOADING_SUDOKU:
            #Hide load sudoku button
            self.buttons[GUIButtons.LOAD_SUDOKU.value].hide()

            #Show arrow buttons
            self.buttons[GUIButtons.LEFT_ARROW.value].show()
            self.buttons[GUIButtons.RIGHT_ARROW.value].show()
        elif prev_state == GUIState.LOADING_SUDOKU:
            #Hide arrow buttons
            self.buttons[GUIButtons.LEFT_ARROW.value].hide()
            self.buttons[GUIButtons.RIGHT_ARROW.value].hide()

            #Show load sudoku button
            self.buttons[GUIButtons.LOAD_SUDOKU.value].show()

        #Hide/Show constraint buttons
        if new_state == GUIState.ADDING_CONSTRAINTS:
            #Hide buttons depending on previous state
            if prev_state in (GUIState.ADDING_WHITE_KROPKI_DOT, GUIState.ADDING_BLACK_KROPKI_DOT, GUIState.ADDING_KILLER_CAGE):
                self.buttons[GUIButtons.ADD_SELECTED_CONSTRAINT.value].hide()
                self.buttons[GUIButtons.CANCEL_SELECTED_CONSTRAINT.value].hide()
            else:
                self.buttons[GUIButtons.SOLVE.value].hide()
                self.buttons[GUIButtons.CLEAR.value].hide()
                self.buttons[GUIButtons.LOAD_SUDOKU.value].hide()
                self.buttons[GUIButtons.ADD_CONSTRAINTS.value].hide()
                self.buttons[GUIButtons.SAVE.value].hide()

            #Show constraint buttons
            self.buttons[GUIButtons.WHITE_KROPKI_DOT.value].show()
            self.buttons[GUIButtons.BLACK_KROPKI_DOT.value].show()
            self.buttons[GUIButtons.KILLER_CAGE.value].show()
            self.buttons[GUIButtons.DONE_ADDING_CONSTRAINTS.value].show()
        elif prev_state == GUIState.ADDING_CONSTRAINTS:
            #Hide constraint buttons
            self.buttons[GUIButtons.WHITE_KROPKI_DOT.value].hide()
            self.buttons[GUIButtons.BLACK_KROPKI_DOT.value].hide()
            self.buttons[GUIButtons.KILLER_CAGE.value].hide()
            self.buttons[GUIButtons.DONE_ADDING_CONSTRAINTS.value].hide()

            #Show buttons depending on new state
            if new_state in (GUIState.ADDING_WHITE_KROPKI_DOT, GUIState.ADDING_BLACK_KROPKI_DOT, GUIState.ADDING_KILLER_CAGE):
                self.buttons[GUIButtons.ADD_SELECTED_CONSTRAINT.value].show()
                self.buttons[GUIButtons.CANCEL_SELECTED_CONSTRAINT.value].show()
            else:
                self.buttons[GUIButtons.SOLVE.value].show()
                self.buttons[GUIButtons.CLEAR.value].show()
                self.buttons[GUIButtons.LOAD_SUDOKU.value].show()
                self.buttons[GUIButtons.ADD_CONSTRAINTS.value].show()
                self.buttons[GUIButtons.SAVE.value].show()

        #Disable/Enable buttons depending on new state
        state_config = self.state_button_config.get(new_state, {})
        for btn_key, btn in self.buttons.items():
            if btn_key in state_config:
                btn.setDisabled(False)
            else:
                btn.setDisabled(True)

    def draw_grid(self):
        for i in range(10):
            if i % 3 == 0:
                pen = QPen(Qt.black, 3)
            else:
                pen = QPen(Qt.gray, 2)

            #Horizontal
            self.scene.addLine(0, i * self.cell_size, self.grid_size * self.cell_size, i * self.cell_size, pen)

            #Vertical
            self.scene.addLine(i * self.cell_size, 0, i * self.cell_size, self.grid_size * self.cell_size, pen)

    def create_cells(self):
        for row in range(9):
            row_cells = []
            for col in range(9):
                cell = QLineEdit()
                cell.setMaxLength(1)
                cell.setAlignment(Qt.AlignCenter)
                cell.setFont(QFont('Arial', 18, QFont.Bold))
                cell.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: transparent;
                        border: none;
                        color: black;
                    }
                    """
                )

                cell.setProperty("row", row)
                cell.setProperty("col", col)
                
                validator = QIntValidator(1, 9, cell)
                cell.setValidator(validator)

                #Cell position
                x = col * self.cell_size
                y = row * self.cell_size

                left_offset = 2 if col % 3 == 0 else 1
                top_offset = 2 if row % 3 == 0 else 1
                right_offset = 2 if (col + 1) % 3 == 0 else 1
                bottom_offset = 2 if (row + 1) % 3 == 0 else 1

                #Add cell to the scene

                proxy = self.scene.addWidget(cell)
                proxy.setMinimumSize(0, 0)
                proxy.setGeometry(QRectF(
                    x + left_offset, 
                    y + top_offset, 
                    self.cell_size - left_offset - right_offset, 
                    self.cell_size - top_offset - bottom_offset
                ))

                cell.textEdited.connect(lambda text, r=row, c=col: self.cell_edited(r, c, text))
                cell.mousePressEvent = lambda event, r=row, c=col: self.on_cell_click(event, r, c)

                row_cells.append(cell)

            self.cells.append(row_cells)

    #region Cell Helper Methods
    def cell_edited(self, row, col, new_value):
        self.set_state(GUIState.EDITED)

        cell = self.cells[row][col]
        cell.setStyleSheet(
            """
            QLineEdit {
                background-color: transparent;
                border: none;
                color: black;
            }
            """
        )

        if new_value == '':
            new_value = 0
        else:
            new_value = int(new_value)
        self.sudoku_board.board[row][col].set_value(new_value)

    def update_cell_value(self, row, col, new_value):
        cell = self.cells[row][col]
        if new_value == 0:
            new_value = ''
        cell.setText(f"{new_value}")
        cell.setStyleSheet(
            """
            QLineEdit {
                background-color: transparent;
                border: none;
                color: blue;
            }
            """
        )
        self.refresh()

    def enable_cell_selection(self):
        self.edit_mode = False
        for row in range(9):
            for col in range(9):
                self.cells[row][col].setReadOnly(True)
        self.clear_cell_selections()

    def disable_cell_selection(self):
        self.edit_mode = True
        for row in range(9):
            for col in range(9):
                self.cells[row][col].setReadOnly(False)
        self.clear_cell_selections()

    def on_cell_click(self, event, row, col):
        if not self.edit_mode:
            cell = self.cells[row][col]

            if (row, col) in self.constraint_selected_cells:
                self.constraint_selected_cells.remove((row, col))
                cell.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: transparent;
                        border: none;
                    }"""
                )
            else:
                self.constraint_selected_cells.append((row, col))
                cell.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: #a4d4e3;
                        border: none;
                    }
                    """
                )
            
    def clear_cell_selections(self):
        for row, col in self.constraint_selected_cells:
            self.cells[row][col].setStyleSheet(
                """
                QLineEdit{
                    background-color: transparent;
                    border: none;
                }
                """
            )
        self.constraint_selected_cells = []
    #endregion

    def create_buttons(self):

        #region Solve Button
        solve_btn = QPushButton("Solve")
        solve_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #009900;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #007700;
            }
            QPushButton:pressed {
                background-color: #005500;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        solve_btn.clicked.connect(self.solve_btn_clicked)
        self.button_row_1.addWidget(solve_btn)
        self.buttons[GUIButtons.SOLVE.value] = solve_btn
        #endregion

        #region Clear Button
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #bb0000;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #990000;
            }
            QPushButton:pressed {
                background-color: #770000;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        clear_btn.clicked.connect(self.clear_btn_clicked)
        self.button_row_1.addWidget(clear_btn)
        self.buttons[GUIButtons.CLEAR.value] = clear_btn
        #endregion

        #region Load Sudoku Button
        load_sudoku_btn = QPushButton("Load Sudoku")
        load_sudoku_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #56aecb;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #3ca2c3;
            }
            QPushButton:pressed {
                background-color: #348ca9;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        load_sudoku_btn.clicked.connect(self.load_sudoku_btn_clicked)
        self.button_row_2.addWidget(load_sudoku_btn)
        self.buttons[GUIButtons.LOAD_SUDOKU.value] = load_sudoku_btn
        #endregion

        #region Arrow Buttons
        left_arrow_btn = QPushButton("←")
        left_arrow_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #56aecb;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #3ca2c3;
            }
            QPushButton:pressed {
                background-color: #348ca9;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        ) 
        left_arrow_btn.clicked.connect(self.left_arrow_btn_clicked)
        self.button_row_2.addWidget(left_arrow_btn)
        self.buttons[GUIButtons.LEFT_ARROW.value] = left_arrow_btn
        left_arrow_btn.hide()

        right_arrow_btn = QPushButton("→")
        right_arrow_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #56aecb;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #3ca2c3;
            }
            QPushButton:pressed {
                background-color: #348ca9;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        ) 
        right_arrow_btn.clicked.connect(self.right_arrow_btn_clicked)
        self.button_row_2.addWidget(right_arrow_btn)
        self.buttons[GUIButtons.RIGHT_ARROW.value] = right_arrow_btn
        right_arrow_btn.hide()
        #endregion

        #region Add Constraints Buttons
        add_constraints_btn = QPushButton("Add Constraints")
        add_constraints_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #dd8f00;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #bb7900;
            }
            QPushButton:pressed {
                background-color: #bb7900;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        add_constraints_btn.clicked.connect(self.add_constraints_btn_clicked)
        self.button_row_3.addWidget(add_constraints_btn)
        self.buttons[GUIButtons.ADD_CONSTRAINTS.value] = add_constraints_btn

        white_kropki_dot_btn = QPushButton("White Kropki Dot")
        white_kropki_dot_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #e6e6e6;
                color: black;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #d4d4d4;
            }
            QPushButton:pressed {
                background-color: #c3c3c3;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        white_kropki_dot_btn.clicked.connect(self.white_kropki_dot_btn_clicked)
        self.button_row_1.addWidget(white_kropki_dot_btn)
        self.buttons[GUIButtons.WHITE_KROPKI_DOT.value] = white_kropki_dot_btn
        white_kropki_dot_btn.hide()

        black_kropki_dot_btn = QPushButton("Black Kropki Dot")
        black_kropki_dot_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #e6e6e6;
                color: black;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #d4d4d4;
            }
            QPushButton:pressed {
                background-color: #c3c3c3;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        black_kropki_dot_btn.clicked.connect(self.black_kropki_dot_btn_clicked)
        self.button_row_1.addWidget(black_kropki_dot_btn)
        self.buttons[GUIButtons.BLACK_KROPKI_DOT.value] = black_kropki_dot_btn
        black_kropki_dot_btn.hide()

        killer_cage_btn = QPushButton("Killer Cage")
        killer_cage_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #e6e6e6;
                color: black;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #d4d4d4;
            }
            QPushButton:pressed {
                background-color: #c3c3c3;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        killer_cage_btn.clicked.connect(self.killer_cage_btn_clicked)
        self.button_row_2.addWidget(killer_cage_btn)
        self.buttons[GUIButtons.KILLER_CAGE.value] = killer_cage_btn
        killer_cage_btn.hide()

        done_adding_constraints_btn = QPushButton("Done")
        done_adding_constraints_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #5d5d5d;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #3b3b3b;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        done_adding_constraints_btn.clicked.connect(self.done_adding_constraints_btn_clicked)
        self.button_row_3.addWidget(done_adding_constraints_btn)
        self.buttons[GUIButtons.DONE_ADDING_CONSTRAINTS.value] = done_adding_constraints_btn
        done_adding_constraints_btn.hide()

        add_selected_constraint_btn = QPushButton("Add")
        add_selected_constraint_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #009900;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #007700;
            }
            QPushButton:pressed {
                background-color: #005500;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        add_selected_constraint_btn.clicked.connect(self.add_selected_constraint_btn_clicked)
        self.button_row_1.addWidget(add_selected_constraint_btn)
        self.buttons[GUIButtons.ADD_SELECTED_CONSTRAINT.value] = add_selected_constraint_btn
        add_selected_constraint_btn.hide()

        cancel_selected_constraint_btn = QPushButton("Cancel")
        cancel_selected_constraint_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #bb0000;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #990000;
            }
            QPushButton:pressed {
                background-color: #770000;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        cancel_selected_constraint_btn.clicked.connect(self.cancel_selected_constraint_btn_clicked)
        self.button_row_2.addWidget(cancel_selected_constraint_btn)
        self.buttons[GUIButtons.CANCEL_SELECTED_CONSTRAINT.value] = cancel_selected_constraint_btn
        cancel_selected_constraint_btn.hide()
        #endregion

        #region Save Button
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
            """
            QPushButton{
                background-color: #bb00bb;
                color: white;
                padding: 10px 20px;
                font-size: 20px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                font-weight:bold;
                background-color: #990099;
            }
            QPushButton:pressed {
                background-color: #770077;
            }
            QPushButton:disabled {
                background-color: #4d4d4d;
            }
            """
        )
        save_btn.clicked.connect(self.save_btn_clicked)
        save_btn.setDisabled(True)
        self.button_row_3.addWidget(save_btn)
        self.buttons[GUIButtons.SAVE.value] = save_btn
        #endregion

    #region Button Click Methods
    def solve_btn_clicked(self):
        solved_board = solver.solve(sudoku_board=self.sudoku_board, state_update_callback=self.set_state, cell_update_callback=self.update_cell_value)

        if solved_board:
            self.show_toast_notification("Solved!")
        else:
            self.show_toast_notification("Failed Solve :(")

    def clear_btn_clicked(self):
        self.set_state(GUIState.EMPTY_BOARD)
        for row in range(9):
            for col in range(9):
                cell = self.cells[row][col]
                cell.setText("")
                cell.setStyleSheet(
                    """

                    QLineEdit {
                        background-color: transparent;
                        border: none;
                        color: black;
                    }
                    """
                )
        self.sudoku_board = SudokuBoard()

        for item in self.constraint_drawings.values():
            if item.scene() == self.scene:
                self.scene.removeItem(item)
        self.refresh()

    def load_sudoku_btn_clicked(self):
        predefined_sudoku = self.predefined_sudokus[self.current_predefined_sudoku_index]
        self.clear_btn_clicked()
        
        self.set_state(GUIState.LOADING_SUDOKU)

        self.sudoku_board = copy.deepcopy(predefined_sudoku)
        for row in range(9):
            for col in range(9):
                value = predefined_sudoku.board[row][col].value
                if value != 0:
                    cell = self.cells[row][col]
                    cell.setText(f"{value}")

        for constraint in self.sudoku_board.constraints:
            if isinstance(constraint, (RowConstraint, ColumnConstraint, BoxConstraint)):
                continue
            elif isinstance(constraint, KropkiDotConstraint):
                row1, col1 = constraint.affected_cells[0].row, constraint.affected_cells[0].col
                row2, col2 = constraint.affected_cells[1].row, constraint.affected_cells[1].col
                if constraint.type == KropkiTypeEnum.WHITE_DOT:
                    self.draw_white_kropki(row1, col1, row2, col2)
                else:
                    self.draw_black_kropki(row1, col1, row2, col2)
            elif isinstance(constraint, KillerCageConstraint):
                pass

    def left_arrow_btn_clicked(self):
        self.current_predefined_sudoku_index -= 1
        if self.current_predefined_sudoku_index < 0:
            self.current_predefined_sudoku_index = len(self.predefined_sudokus) - 1

        self.load_sudoku_btn_clicked()

    def right_arrow_btn_clicked(self):
        self.current_predefined_sudoku_index += 1
        if self.current_predefined_sudoku_index >= len(self.predefined_sudokus):
            self.current_predefined_sudoku_index = 0

        self.load_sudoku_btn_clicked()

    def add_constraints_btn_clicked(self):
        self.set_state(GUIState.ADDING_CONSTRAINTS)
        
    def save_btn_clicked(self):
        board_values = [[0 for _ in range(9)] for _ in range(9)]
        for row in range(9):
            for col in range(9):
                board_values[row][col] = self.sudoku_board.board[row][col].value

        constraints = defaultdict(list)
        for constraint in self.sudoku_board.constraints:
            match constraint:
                case KropkiDotConstraint():
                    cell1 = constraint.affected_cells[0]
                    cell2 = constraint.affected_cells[1]
                    cells = [(cell1.row, cell1.col), (cell2.row, cell2.col)]

                    constraints[constraint.type.value].append(cells)
                case KillerCageConstraint():
                    print("IMPLEMENT FUNCTIONALITY TO SAVE KILLER CAGE CONSTRAINTS")
                case _:
                    continue

        if predefined_sudoku_utils.save_predefined_sudoku(board_values, constraints):
            self.show_toast_notification("Sudoku saved successfully!")
            self.predefined_sudokus.append(self.sudoku_board)
        else:
            self.show_toast_notification("There was an error when saving the sudoku.")

    def white_kropki_dot_btn_clicked(self):
        self.enable_cell_selection()
        self.set_state(GUIState.ADDING_WHITE_KROPKI_DOT)
        self.selected_constraint_type = ConstraintsEnum.WHITE_KROPKI_DOT        
        
    def black_kropki_dot_btn_clicked(self):
        self.enable_cell_selection()
        self.set_state(GUIState.ADDING_BLACK_KROPKI_DOT)
        self.selected_constraint_type = ConstraintsEnum.BLACK_KROPKI_DOT

    def killer_cage_btn_clicked(self):
        self.enable_cell_selection()
        self.set_state(GUIState.ADDING_KILLER_CAGE)
        self.selected_constraint_type = ConstraintsEnum.KILLER_CAGE

    def add_selected_constraint_btn_clicked(self):
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
                    affected_cell_ids = set([affected_cells[0].id, affected_cells[1].id])

                    for c in affected_cells[0].constraints:
                        if isinstance(c, KropkiDotConstraint):
                            c_ids = set([c.affected_cells[0].id, c.affected_cells[1].id])
                            if affected_cell_ids == c_ids:
                                if c.type == KropkiTypeEnum.WHITE_DOT:
                                    #Duplicate constraint
                                    self.show_toast_notification("That Constraint Has Already Been Added")
                                else:
                                    self.show_toast_notification("You Already Have A Black Kropki Dot Constraint There")
                                return

                    new_constraint = KropkiDotConstraint(
                        cells=affected_cells,
                        type=KropkiTypeEnum.WHITE_DOT
                    )

                    self.sudoku_board.constraints.append(new_constraint)

                    self.draw_white_kropki(
                        row1=self.constraint_selected_cells[0][0], 
                        col1=self.constraint_selected_cells[0][1], 
                        row2=self.constraint_selected_cells[1][0], 
                        col2=self.constraint_selected_cells[1][1],
                        constraint_id=new_constraint.constraint_id
                    )

                    for cell in affected_cells:
                        cell.add_constraint(new_constraint)

                    self.show_toast_notification("White Kropki Dot Constraint Added")
                else:
                    self.show_toast_notification("Invalid Cell Selection For Kropki Dot")
                    return
            case ConstraintsEnum.BLACK_KROPKI_DOT:
                if is_valid_kropki_selection(self.constraint_selected_cells):
                    #Add black kropki dot constraint to SudokuBoard
                    affected_cells = [self.sudoku_board.board[r][c] for r, c in self.constraint_selected_cells]
                    affected_cell_ids = set([affected_cells[0].id, affected_cells[1].id])

                    for c in affected_cells[0].constraints:
                        if isinstance(c, KropkiDotConstraint):
                            c_ids = set([c.affected_cells[0].id, c.affected_cells[1].id])
                            if affected_cell_ids == c_ids:
                                if c.type == KropkiTypeEnum.BLACK_DOT:
                                    #Duplicate constraint
                                    self.show_toast_notification("That Constraint Has Already Been Added")
                                else:
                                    self.show_toast_notification("You Already Have A White Kropki Dot Constraint There")
                                return

                    new_constraint = KropkiDotConstraint(
                        cells=affected_cells,
                        type=KropkiTypeEnum.BLACK_DOT
                    )
                    self.sudoku_board.constraints.append(new_constraint)

                    self.draw_black_kropki(
                        row1=self.constraint_selected_cells[0][0], 
                        col1=self.constraint_selected_cells[0][1], 
                        row2=self.constraint_selected_cells[1][0], 
                        col2=self.constraint_selected_cells[1][1],
                        constraint_id=new_constraint.constraint_id
                    )

                    for cell in affected_cells:
                        cell.add_constraint(new_constraint)

                    self.show_toast_notification("Black Kropki Dot Constraint Added")
                else:
                    self.show_toast_notification("Invalid Cell Selection For Kropki Dot")
                    return
            case ConstraintsEnum.KILLER_CAGE:
                print("TO-DO: Implement Killer Cage")
            
        self.cancel_selected_constraint_btn_clicked()

    def cancel_selected_constraint_btn_clicked(self):
        self.disable_cell_selection()
        self.constraint_selected_cells = []
        self.set_state(GUIState.ADDING_CONSTRAINTS)

    def done_adding_constraints_btn_clicked(self):
        if self.sudoku_board.is_board_empty():
            self.set_state(GUIState.EMPTY_BOARD)
        else:
            self.set_state(GUIState.EDITED)

    #endregion Button Click Methods

    #region Draw Constraints
    def _get_border_position(self, row1, col1, row2, col2):
        #Get the center position between two cells
        if row1 == row2:  # Horizontal
            x = (min(col1, col2) + 1) * self.cell_size
            y = (row1 + 0.5) * self.cell_size
        else:  # Vertical
            x = (col1 + 0.5) * self.cell_size
            y = (min(row1, row2) + 1) * self.cell_size
        return x, y

    def draw_white_kropki(self, row1, col1, row2, col2, constraint_id):
        x, y = self._get_border_position(row1, col1, row2, col2)

        # Create white circle with black outline
        ellipse = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
        ellipse.setBrush(QBrush(Qt.white))
        ellipse.setPen(QPen(Qt.black, 2))
        ellipse.setZValue(10)  # Above grid lines

        self.scene.addItem(ellipse)
        self.constraint_drawings[constraint_id] = ellipse
        self.refresh()

    def draw_black_kropki(self, row1, col1, row2, col2, constraint_id):
        x, y = self._get_border_position(row1, col1, row2, col2)

        # Create white circle with black outline
        ellipse = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
        ellipse.setBrush(QBrush(Qt.black))
        ellipse.setPen(QPen(Qt.black, 2))
        ellipse.setZValue(10)  # Above grid lines

        self.scene.addItem(ellipse)
        self.constraint_drawings[constraint_id] = ellipse
        self.refresh()
        


    def draw_killer_cage(self, cells, total):
        print("TO-DO: implement killer cage drawing")
        #Something like this
        
        # if not cells:
        #     return
        
        # # Find bounding box
        # rows = [r for r, c in cells]
        # cols = [c for r, c in cells]
        # min_row, max_row = min(rows), max(rows)
        # min_col, max_col = min(cols), max(cols)
        
        # x1 = min_col * self.cell_size + 3
        # y1 = min_row * self.cell_size + 3
        # x2 = (max_col + 1) * self.cell_size - 3
        # y2 = (max_row + 1) * self.cell_size - 3
        
        # # Create dashed path around the cage
        # path = QPainterPath()
        # path.moveTo(x1, y1)
        # path.lineTo(x2, y1)
        # path.lineTo(x2, y2)
        # path.lineTo(x1, y2)
        # path.lineTo(x1, y1)
        
        # # Add path with dashed pen
        # pen = QPen(Qt.black, 2, Qt.DashLine)
        # path_item = self.scene.addPath(path, pen)
        # path_item.setZValue(5)
        
        # # Add sum text in top-left corner
        # text = QGraphicsTextItem(str(total))
        # text.setFont(QFont('Arial', 10, QFont.Bold))
        # text.setPos(x1 + 2, y1 - 2)
        # text.setZValue(15)
        # self.scene.addItem(text)
    
    #endregion
