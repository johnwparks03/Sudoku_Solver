# Sudoku Solver

A Python-based Sudoku solver with GUI support for standard Sudoku puzzles and variant rules including Kropki dots and Killer cages.

## Features

- **Interactive GUI**: Built with PyQt for easy puzzle input and visualization
- **Multiple Solving Techniques**:
  - Constraint propagation
  - Backtracking algorithm
  - Naked singles, hidden singles
- **Variant Rule Support**:
  - Kropki dots (white: consecutive, black: 2:1 ratio)
  - Killer cages (sum constraints)
  - Extensible architecture for adding new constraint types
- **Visual Constraint Editor**: Click to add and remove constraints
- **Predefined Puzzles**: Load sample puzzles from JSON configuration files
- **Step-by-step Visualization**: Watch the solver work through the puzzle

## Installation

### Prerequisites
- Python 3.8+

### Setup
```bash
git clone https://github.com/yourusername/Sudoku_Solver.git
cd Sudoku_Solver
pip install -r requirements.txt
```

## Usage

### Running the Application
```bash
python main.py
```

## Algorithm

The solver uses a combination of techniques:

1. **Constraint Propagation**: Eliminates impossible values based on rules
   - Row/column/box uniqueness
   - Kropki relationships (consecutive or 2:1 ratio)
   - Other constraints

2. **Backtracking**: When propagation isn't sufficient
   - Selects cell with minimum possible values
   - Tries each possibility recursively
   - Backtracks on contradictions

## Future Enhancements

- [ ] Additional constraint types 
- [ ] Performance optimizations
- [ ] Web-based version
