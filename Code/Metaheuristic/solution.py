import numpy as np

class Solution:
    """
    Class to store solutions of the problem
    """

    def __init__(self, scenario):
        self.scenario = scenario

        # skill counter. Object with dimensions
        self.skill_counter = self.create_skill_counter()

        # employee shift assignments
        self.shift_assignments = self.create_shift_assignments()

        # information to keep track of solution per nurse
        self.total_assignments = None
        self.working_days = None
        self.work_stretches = None
        self.working_weekends_set = None
        self.number_working_weekends = None
        self.shift_stretches = None  # nog bedenken of dit samenkomt in een enkel object
        # of per shift type opslaan als object
        self.day_off_stretches = None

    def create_shift_assignments(self):
        """
        Create dict to store employee shift assignments
        Each array has as length the number of days
        Each element in the array store the assignment of the nurse on that day
        0 --> off
        1 --> s_type_1
        2 --> s_type_2
        etc.
        :return:
        dict with key: employee_id, value: array of zeros
        """
        shift_assignments = {}
        for id in self.scenario.employees._collection.keys():
            shift_assignments[id] = np.zeros(self.scenario.num_days_in_horizon)
        return shift_assignments

    def create_skill_counter(self):
        """
        Function to create skill counter
        :return:
        Array with dimensions num_days x num_shift_types x (sum of skill sets x skills per skill set)
        """

        dim_skills = sum([len(skill_set) for skill_set in self.scenario.skill_set_collection.collection.values()])
        return np.zeros((self.scenario.num_days_in_horizon, self.scenario.num_shift_types, dim_skills))

    def replace_shift_assignment(self, employee_id, day_index, s_type_index):
        """
        Replace shift assignment of employee by new shift assignment
        """
        self.shift_assignments[employee_id][day_index] = s_type_index + 1

    def remove_shift_assignment(self, employee_id, d_index):
        """
        Change shift assignment of employee to day off
        """
        self.shift_assignments[employee_id][d_index] = 0

    def update_skill_counter(self, day_index, s_type_index, skill_index, skill_set_index, add=True, increment=1):
        """
        Function to change skill counter upon assignment
        :return:
        skill_counter object
        """
        # calc where to change the skill counter
        skill_index_to_change = self.scenario.skill_set_collection.collection[skill_set_index].start_index +\
                    self.scenario.skill_set_collection.collection[skill_set_index].get_index_in_set(skill_index)
        if add:
            self.skill_counter[day_index, s_type_index, skill_index_to_change] += increment
        else:
            self.skill_counter[day_index, s_type_index, skill_index_to_change] -= increment

    def check_if_working_day(self, employee_id, d_index):
        """
        Check if nurse works on specific day
        :return:
        True or False
        """
        return self.shift_assignments[employee_id][d_index] > 0


