from abc import ABC, abstractmethod
from itertools import combinations


class Constraint(ABC):
    def __init__(self, cells):
        self.affected_cells = cells # List of cells affected by the constraint

    @abstractmethod
    def verify_constraint(self):
        #Returns True or False if constraint is satisfied based on current values in affected cells
        pass

    @abstractmethod
    def propagate(self):
        #Removes impossible values from affected cells based on current values
        pass

class RowConstraint(Constraint):
    def __init__(self, cells):
        super().__init__(cells)

    def verify_constraint(self):
        #Numbers within row must not repeat
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        set_nums_seen = set(nums_seen)

        return len(nums_seen) == len(set_nums_seen)
    
    def propagate(self):
        #Seen nums can be removed from possible values of other affected cells
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        for cell in self.affected_cells:
            if cell.value == 0:
                cell.possible_values -= set(nums_seen)

class ColumnConstraint(Constraint):
    def __init__(self, cells):
        super().__init__(cells)

    def verify_constraint(self):
        #Numbers within column must not repeat
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        set_nums_seen = set(nums_seen)

        return len(nums_seen) == len(set_nums_seen)
    
    def propagate(self):
        #Seen nums can be removed from possible values of other affected cells
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        for cell in self.affected_cells:
            if cell.value == 0:
                cell.possible_values -= set(nums_seen)
                
class BoxConstraint(Constraint):
    def __init__(self, cells):
        super().__init__(cells)

    def verify_constraint(self):
        #Numbers within box must not repeat
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        set_nums_seen = set(nums_seen)

        return len(nums_seen) == len(set_nums_seen)
    
    def propagate(self):
        #Seen nums can be removed from possible values of other affected cells
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        for cell in self.affected_cells:
            if cell.value == 0:
                cell.possible_values -= set(nums_seen)

class KillerCageConstraint(Constraint):
    def __init__(self, cells, target):
        super().__init__(cells)
        self.target_sum = target
        self.cells_in_cage = len(cells)
        self.possible_sums = self.find_possible_sums(target, self.cells_in_cage)

    def find_possible_sums(self, target, num_cells):
        #Return a list of sets of possible combinations that add up to target sum
        return [set(combo) for combo in combinations(range(1,10), num_cells) if sum(combo) == target]


    def verify_constraint(self):
        # Need to verify
        # 1. No repeating numbers within killer cage
        # 2. If all cells are filled, their sum equals target sum
        # 3. If not all cells are filled, the current sum does not exceed target sum
        # 4. The combination of numbers in the cage are part of a possible sum to the target sum
        # Return true if all conditions are met, else false

        #Numbers within killer cage must not repeat and must add up to target sum
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        set_nums_seen = set(nums_seen)

        #Check to ensure there are no repeating digits
        if len(nums_seen) != len(set_nums_seen):
            return False
        
        current_sum = sum(nums_seen)
        if len(nums_seen) == len(self.affected_cells):
            #All cells filled, check if sum matches target
            if current_sum != self.target_sum:
                return False
        else:
            #Not all cells filled, check if current sum exceeds target
            if current_sum >= self.target_sum:
                return False
            
        is_possible_sum = [set_nums_seen.issubset(p) for p in self.possible_sums]
        if not any(is_possible_sum):
            return False
        
        return True
        

        
    
    def propagate(self):
        #Seen nums can be removed from possible values of other affected cells
        nums_seen = [cell.value for cell in self.affected_cells if cell.value != 0]
        for cell in self.affected_cells:
            if cell.value == 0:
                cell.possible_values -= set(nums_seen)

        #TO-DO: Additional logic to limit possible values based on target sum can be added here
        #   Nums seen must be a part of a summation to the target sum, so then remaining possible values
        #   can be found from the possible summations that include the nums seen.

class KropkiDotConstraint(Constraint):
    def __init__(self, cells, type):
        super().__init__(cells)
        self.type = type # 'white' or 'black'

    def verify_constraint(self):
        # Need to verify
        # 1. For white dot, numbers must be consecutive
        # 2. For black dot, one number must be double the other
        val1 = self.affected_cells[0].value
        val2 = self.affected_cells[1].value

        if self.type == 'white':
            if val1 == 0 or val2 == 0:
                return True # Cannot verify yet
            return abs(val1 - val2) == 1
        elif self.type == 'black':
            impossible_nums = [5, 7, 9]
            if val1 in impossible_nums or val2 in impossible_nums:
                return False
            if val1 == 0 or val2 == 0:
                return True # Cannot verify yet
            return (val1 == 2 * val2) or (val2 == 2 * val1)
    
    def propagate(self):
        if self.type == 'white':
            # For white dot, possible values must be consecutive
            cell1, cell2 = self.affected_cells
            if cell1.value == 0 and cell2.value == 0:
                new_possibles1 = set()
                new_possibles2 = set()
                for val in cell1.possible_values:
                    if val + 1 in cell2.possible_values:
                        new_possibles1.add(val)
                        new_possibles2.add(val + 1)
                    if val - 1 in cell2.possible_values:
                        new_possibles1.add(val)
                        new_possibles2.add(val - 1)
                cell1.possible_values = new_possibles1
                cell2.possible_values = new_possibles2
            elif cell1.value == 0:
                cell1.possible_values = {cell2.value - 1, cell2.value + 1} & cell1.possible_values
            elif cell2.value == 0:
                cell2.possible_values = {cell1.value - 1, cell1.value + 1} & cell2.possible_values
        elif self.type == 'black':
            # For black dot, one number must be double the other
            cell1, cell2 = self.affected_cells
            if cell1.value == 0 and cell2.value == 0:
                new_possibles1 = set()
                new_possibles2 = set()
                for val in cell1.possible_values:
                    if val * 2 in cell2.possible_values:
                        new_possibles1.add(val)
                        new_possibles2.add(val * 2)
                    if val % 2 == 0 and (val // 2) in cell2.possible_values:
                        new_possibles1.add(val)
                        new_possibles2.add(val // 2)
                cell1.possible_values = new_possibles1
                cell2.possible_values = new_possibles2
            elif cell1.value == 0:
                possible_vals = set()
                if cell2.value % 2 == 0:
                    possible_vals.add(cell2.value // 2)
                possible_vals.add(cell2.value * 2)
                cell1.possible_values = possible_vals & cell1.possible_values
            elif cell2.value == 0:
                possible_vals = set()
                if cell1.value % 2 == 0:
                    possible_vals.add(cell1.value // 2)
                possible_vals.add(cell1.value * 2)
                cell2.possible_values = possible_vals & cell2.possible_values