class SudokuCell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.id = (row * 10) + col
        self.value = 0 # 0 indicates an empty cell
        self.possible_values = set(range(1, 10)) # Possible values from 1 to 9
        self.constraints = [] # List of constraint objects affecting this cell

    def set_value(self, value):
        self.value = value
        for constraint in self.constraints:
            constraint.propagate()

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        constraint.propagate()