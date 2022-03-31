import numpy as np


class Solution:
    """
    Class to store solutions of the problem
    """

    def __init__(self, other_solution=None):

        if other_solution:
            # employee shift assignments
            self.shift_assignments = other_solution.shift_assignments

            # transfer skill request info
            self.diff_opt_request = other_solution.diff_opt_request
            self.diff_min_request = other_solution.diff_min_request

            # objective value
            self.obj_value = other_solution.obj_value

            # information to keep track of solution per nurse
            self.total_assignments = None
            self.working_days = None
            self.work_stretches = None
            self.working_weekends_set = None
            self.number_working_weekends = None
            self.shift_stretches = None  # nog bedenken of dit samenkomt in een enkel object
            # of per shift type opslaan als object
            self.day_off_stretches = None

    def replace_shift_assignment(self, employee_id, d_index, s_index, sk_index):
        """
        Replace shift assignment of employee by new shift assignment
        """
        self.shift_assignments[employee_id][d_index] = np.array([s_index, sk_index])
        # self.shift_assignments[employee_id][day_index] = {'s_type': s_type_index + 1, 'sk_type': sk_index}

    def shift_assignment_to_off(self, employee_id, d_index):
        """
        Change shift assignment of employee to day off
        """
        self.shift_assignments[employee_id][d_index] = np.array([-1, -1])

    def check_if_working_day(self, employee_id, d_index):
        """
        Check if nurse works on specific day
        :return:
        True or False
        """
        return self.shift_assignments[employee_id][d_index][0] > -1

    def update_information_removal(self, solution, employee_id, d_index, s_index, sk_index):
        """
        Function to update relevant information after removal from shift skill combination
        """
        # hard constraints
        solution.diff_min_request[(d_index, sk_index, s_index)] -= 1

        # soft constraints
        # S1
        solution.diff_opt_request[(d_index, sk_index, s_index)] -= 1

    def update_information_insertion(self, solution, employee_id, d_index, s_index, sk_index):
        """
        Function to update relevant information after insertion into new shift skill combination
        """
        # hard constraints
        solution.diff_min_request[(d_index, sk_index, s_index)] += 1

        # soft constraints
        # S1
        solution.diff_opt_request[(d_index, sk_index, s_index)] += 1

        # all other constraints

    def update_solution_change(self, change_info):
        """
        Function to implement all changes caused by the new solution
        after it has been accepted
        """
        employee_id = change_info['employee_id']
        # check if employee is working in current solution
        if change_info["current_working"]:
            self.update_information_removal(solution=self,
                                            employee_id=change_info['employee_id'],
                                            d_index=change_info['curr_ass'][0],
                                            s_index=change_info['curr_ass'][1],
                                            sk_index=change_info['curr_ass'][2])
        # check if new assignment is working
        if change_info["new_working"]:
            self.update_information_insertion(solution=self,
                                            employee_id=change_info['employee_id'],
                                            d_index=change_info['d_index'],
                                            s_index=change_info['new_s_type'],
                                            sk_index=change_info['new_sk_type'])

            # add new shift assignment
            self.replace_shift_assignment(employee_id=change_info['employee_id'],
                                          d_index=change_info['d_index'],
                                          s_index=change_info['new_s_type'],
                                          sk_index=change_info['new_sk_type'])
        else:
            # remove shift assignment if not moving to shift assignment
            self.shift_assignment_to_off(employee_id=change_info['employee_id'],
                                         d_index=change_info['d_index'])

        # change objective value
        self.obj_value += change_info['cost_increment']

    # def create_skill_counter(self):
    #     """
    #     Function to create skill counter
    #     :return:
    #     Array with dimensions num_days x num_shift_types x (sum of skill sets x skills per skill set)
    #     """
    #
    #     dim_skills = sum([len(skill_set) for skill_set in self.scenario.skill_set_collection.collection.values()])
    #     return np.zeros((self.scenario.num_days_in_horizon, self.scenario.num_shift_types, dim_skills))

    # def update_skill_counter(self, day_index, s_type_index, skill_index, skill_set_index, add=True, increment=1):
    #     """
    #     Function to change skill counter upon assignment
    #     :return:
    #     skill_counter object
    #     """
    #     # calc where to change the skill counter
    #     skill_index_to_change = self.scenario.skill_set_collection.collection[skill_set_index].start_index + \
    #                             self.scenario.skill_set_collection.collection[skill_set_index].get_index_in_set(
    #                                 skill_index)
    #     if add:
    #         self.skill_counter[day_index, s_type_index, skill_index_to_change] += increment
    #     else:
    #         self.skill_counter[day_index, s_type_index, skill_index_to_change] -= increment





