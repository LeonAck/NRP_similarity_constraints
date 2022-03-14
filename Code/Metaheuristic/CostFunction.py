import numpy as np


class ObjectiveValue:
    """Class for the cost function
    Containing constraint violations and functions to recalculate the cost function"""

    def __init__(self, settings=None):

        self.soft_constraints = None

        # save constraint violations

        self.current_solution_obj = None
        self.best_solution_obj = None

        # skill counter. Object with dimensions
        self.skill_counter = None

    def calc_objective(self):
        """
        Function to calculate cost function
        """
        # use matrix multiplication of violations x weights

    def calc_objective_incremental(self, increment, constraint):
        """
        Function to recalculate value based on change in constraints
        and old value
        :return:
        New value cost function
        """
        # use matrix multiplication of violations increments x weights + old_value
        return None

    def create_skill_counter(self, num_days, num_shift_types, num_skill_sets):
        """
        Function to create skill counter
        :return:
        Array with dimensions num_days x num_shift_types x (sum of skill sets x skills per skill set)
        """
        return np.zeros((num_days, num_shift_types, num_skill_sets))


