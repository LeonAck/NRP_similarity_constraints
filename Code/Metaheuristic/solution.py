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
        return np.zeros((self.scenario.num_days_in_horizon, self.scenario.num_shift_types, dim_skills))

    def update_skill_counter(self, day_index, s_type_index, skill_index, skill_set_index, add=True, increment=1):
        """
        Function to change skill counter upon assignment
        :return:
        skill_counter object
        """
        # calc where to change the skill counter
        skill_index_to_change = self.scenario.skill_set_collection._collection[skill_set_index].start_index + skill_index
        if add:
            self.skill_counter[day_index, s_type_index, skill_index_to_change] += increment
        else:
            self.skill_counter[day_index, s_type_index, skill_index_to_change] -= increment

    def sum_skill_counter_per_skill(self, skill_index):
        """
        Function to add the skill counter for a given skill
        :return:
        sum (int)
        """



