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

    def create_skill_counter(self, scenario, num_days, num_shift_types):
        """
        Function to create skill counter
        :return:
        Array with dimensions num_days x num_shift_types x (sum of skill sets x skills per skill set)
        """
        # TODO get right dimensions
        dim_skills = [len(skill_set) for skill_set in scenario.skill_sets]
        return np.zeros((num_days, dim_skills, num_shift_types))

