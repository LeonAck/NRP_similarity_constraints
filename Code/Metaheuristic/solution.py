import numpy as np
from Invoke.Constraints.Rules.RuleS2Max import RuleS2Max
from Invoke.Constraints.Rules.RuleS3Max import RuleS3Max
from Invoke.Constraints.Rules.RuleS2ShiftMax import RuleS2ShiftMax

class Solution:
    """
    Class to store solutions of the problem
    """

    def __init__(self, other_solution=None):

        if other_solution:
            # get day_collection
            self.day_collection = other_solution.day_collection

            # employee shift assignments
            self.shift_assignments = other_solution.shift_assignments

            # H2
            self.diff_min_request = other_solution.diff_min_request

            # S1
            self.diff_opt_request = other_solution.diff_opt_request

            # S2
            self.work_stretches = other_solution.work_stretches

            # S2Shift
            self.shift_stretches = other_solution.shift_stretches

            # S3
            self.day_off_stretches = other_solution.day_off_stretches

            # S5 number of assignments
            self.num_assignments_per_nurse = other_solution.num_assignments_per_nurse

            # S6 number of working weekends
            self.num_working_weekends = other_solution.num_working_weekends

            # objective value
            self.obj_value = other_solution.obj_value

            self.violation_array = other_solution.violation_array
            # information to keep track of solution per nurse
            self.working_days = None
            self.working_weekends_set = None

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

    def check_if_working_s_type_on_day(self, employee_id, d_index, s_index):
        """
        Check if nurse works specific shift type on specific day
        """
        return self.shift_assignments[employee_id][d_index][0] == s_index

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update relevant information after removal from shift skill combination
        """
        # hard constraints
        solution.diff_min_request[(change_info['curr_ass'][0], change_info['curr_ass'][2], change_info['curr_ass'][1])] -= 1

        # soft constraints
        # S1
        solution.diff_opt_request[(change_info['curr_ass'][0], change_info['curr_ass'][2], change_info['curr_ass'][1])] -= 1

        # S2Max and S2Min
        solution = RuleS2Max().update_information_assigned_to_off(solution, change_info)

        # S2ShiftMax and S2ShiftMin
        solution = RuleS2ShiftMax().update_information_assigned_to_off(solution, change_info)

        # S3Max and S3Min
        solution = RuleS3Max().update_information_assigned_to_off(solution, change_info)

        # S4
        # nothing

        # S5
        solution.num_assignments_per_nurse[change_info['employee_id']] -= 1

        # S6
        if change_info['d_index'] in solution.day_collection.list_weekend_days:
            if not solution.check_if_working_day(employee_id=change_info['employee_id'],
                                                            d_index=change_info['d_index'] + solution.day_collection.get_index_other_weekend_day(
                                                          solution.day_collection.weekend_day_indices[change_info['d_index']])):
                solution.num_working_weekends[change_info['employee_id']] -= 1

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update relevant information after insertion into new shift skill combination
        """
        # hard constraints
        solution.diff_min_request[(change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1

        # soft constraints
        # S1
        solution.diff_opt_request[(change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1

        # S2Max and S2Min
        solution = RuleS2Max().update_information_off_to_assigned(solution, change_info)

        # S2ShiftMax and S2ShiftMin
        solution = RuleS2ShiftMax().update_information_off_to_assigned(solution, change_info)

        #S3Max
        solution = RuleS3Max().update_information_off_to_assigned(solution, change_info)

        # S4
        # no changes necessary

        # S5
        solution.num_assignments_per_nurse[change_info['employee_id']] += 1

        # S6
        if change_info['d_index'] in solution.day_collection.list_weekend_days:
           if not solution.check_if_working_day(employee_id=change_info['employee_id'],
                                                    d_index=change_info['d_index'] + solution.day_collection.get_index_other_weekend_day(
                                                  solution.day_collection.weekend_day_indices[change_info['d_index']])):
            solution.num_working_weekends[change_info['employee_id']] += 1

    def update_information_assigned_to_assigned(self, solution, change_info):
        """
        Update information after moving from one assignment to the other
        """

        # hard constraints
        solution.diff_min_request[(change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1
        solution.diff_min_request[(change_info['curr_ass'][0], change_info['curr_ass'][2], change_info['curr_ass'][1])] -= 1

        # soft constraints
        # S1
        solution.diff_opt_request[(change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1
        solution.diff_opt_request[(change_info['curr_ass'][0], change_info['curr_ass'][2], change_info['curr_ass'][1])] -= 1

        # S2ShiftMax
        # S2-S6
        # no changes necessary

    def update_solution_change(self, change_info):
        """
        Function to implement all changes caused by the new solution
        after it has been accepted
        """
        # check what change has been made
        if change_info["current_working"] and change_info['new_working']:
            self.update_information_assigned_to_assigned(solution=self,
                                                        change_info=change_info)
        elif change_info['current_working']:
            self.update_information_assigned_to_off(solution=self,
                                                    change_info=change_info)
        else:
            self.update_information_off_to_assigned(solution=self,
                                                    change_info=change_info)

        # check if new assignment is working
        if change_info["new_working"]:
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
        self.violation_array += change_info['violation_increment']

    def calc_objective_value(self, scenario, rule_collection):
        """
        Function to calculate the objective value of a solution based on the
        applied soft constraints
        """
        return np.matmul(self.get_violations(scenario, rule_collection), rule_collection.penalty_array)

    def calc_objective_value_violations(self, violation_array, rule_collection):
        """
        Function to calculate the objective value of a solution based on the
        applied soft constraints
        """
        return np.matmul(violation_array, rule_collection.penalty_array)

    def get_violations(self, scenario, rule_collection):
        violation_array = np.zeros(len(rule_collection.soft_rule_collection.collection))
        for i, rule in enumerate(rule_collection.soft_rule_collection.collection.values()):
            violation_array[i] = rule.count_violations(solution=self, scenario=scenario)
        return violation_array

    def get_violations_per_employee(self, scenario, rule_collection):
        pass

    def check_if_first_day(self, d_index):
        return d_index == 0

    def check_if_last_day(self, d_index):
        return d_index == self.day_collection.num_days_in_horizon - 1

    def check_if_middle_day(self, d_index):
        return not self.check_if_last_day(d_index) and not self.check_if_first_day(d_index)


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





