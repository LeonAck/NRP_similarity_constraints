import numpy as np

class ObjectiveValue:
    """Class for the cost function
    Containing constraint violations and functions to recalculate the cost function"""

    def __init__(self, settings=None):

        self.soft_constraints = None

        # save constraint violations

        self.current_solution_obj = None
        self.best_solution_obj = None

    def calc_objective(self):
        """
        Function to calculate cost function
        """
        # use matrix multiplication of violations x weights

    def calc_objective_incremental(self, rule_collection, constraint):
        """
        Function to recalculate value based on change in constraints
        and old value
        :return:
        New value cost function
        """
        # use matrix multiplication of violations increments x weights + old_value
        # need object with increments per violation
        return None






