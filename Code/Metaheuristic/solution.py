import numpy as np

class Solution:
    """
    Class to store solutions of the problem
    """

    def __init__(self, scenario):
        self.scenario = scenario
        self.employees = None
        #self.solution = solution
        #self.best_solution = solution

        # skill counter. Object with dimensions
        self.skill_counter = self.create_skill_counter()

    def create_skill_counter(self):
        """
        Function to create skill counter
        :return:
        Array with dimensions num_days x num_shift_types x (sum of skill sets x skills per skill set)
        """

        dim_skills = sum([len(skill_set) for skill_set in self.scenario.skill_set_collection._collection.values()])
        return np.zeros((self.scenario.num_days_in_horizon, dim_skills, self.scenario.num_shift_types))

    def update_skill_counter(self, skill_index, skill_set_index):
        """
        Function to change skill counter upon assignment
        :return:
        skill_counter object
        """


