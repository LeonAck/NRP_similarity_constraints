import numpy as np

class Solution:
    """
    Class to store solutions of the problem
    """

    def __init__(self, initial_solution, solution):
        self.solution = solution
        self.best_solution = solution

        # skill counter. Object with dimensions
        self.skill_counter = None

    def create_skill_counter(self, num_days, num_shift_types, num_skill_sets):
        """
        Function to create skill counter
        :return:
        Array with dimensions num_days x num_shift_types x (sum of skill sets x skills per skill set)
        """
        # TODO get right dimensions
        return np.zeros((num_days, num_shift_types, num_skill_sets))

