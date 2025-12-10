# Sudoku Solver

## Workflow

1. Constraint propagation to eliminate impossible value using rules such as 1-9 in each row/column, kropki dots, killer cage, etc.
2. Choose square with least amount of possible numbers
3. Choose a number for the square
    1. Propagate constraints for affected squares
    2. Recursively solve
    3. Backtrack when
        - A contradiction against one of the rules is found
        - A square has no more possible values

### Important Notes

- Make rulesets modular so new rulesets can be added

### Things to add

- Visual Interface
- Sudoku Creator/Generator

## Notes

Board: 9x9 array of SudokuCell objects

SudokuCell:

- row, col
- value
- possibilities (set of possible values)
- constraints (list of Constraint objects)

Constraint (base class):

- affected_cells (list of SudokuCell objects)
- verify() method (abstract/to be implemented)

Specific constraint classes extend Constraint:

- RowConstraint
- ColumnConstraint
- BoxConstraint
- KillerCageConstraint (with sum requirement)
- KropkiConstraint (with dot type: white/black)
- etc.
