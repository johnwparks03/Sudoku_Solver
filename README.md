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

Sudoku Board Indexing

```txt
| 0,0 | 0,1 | 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | 0,7 | 0,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 1,0 | 1,1 | 1,2 | 1,3 | 1,4 | 1,5 | 1,6 | 1,7 | 1,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 2,0 | 2,1 | 2,2 | 2,3 | 2,4 | 2,5 | 2,6 | 2,7 | 2,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 3,0 | 3,1 | 3,2 | 3,3 | 3,4 | 3,5 | 3,6 | 3,7 | 3,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 4,0 | 4,1 | 4,2 | 4,3 | 4,4 | 4,5 | 4,6 | 4,7 | 4,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 5,0 | 5,1 | 5,2 | 5,3 | 5,4 | 5,5 | 5,6 | 5,7 | 5,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 6,0 | 6,1 | 6,2 | 6,3 | 6,4 | 6,5 | 6,6 | 6,7 | 6,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 7,0 | 7,1 | 7,2 | 7,3 | 7,4 | 7,5 | 7,6 | 7,7 | 7,8 |  
|-----|-----|-----|-----|-----|-----|-----|-----|-----|  
| 8,0 | 8,1 | 8,2 | 8,3 | 8,4 | 8,5 | 8,6 | 8,7 | 8,8 |  
```
