import numpy as np
from Invoke.Constraints.Rules.RuleS2Max import RuleS2Max
from Invoke.Constraints.Rules.RuleS3Max import RuleS3Max
from Invoke.Constraints.Rules.RuleS5Max import RuleS5Max
from Invoke.Constraints.Rules.RuleS2ShiftMax import RuleS2ShiftMax
from Invoke.Constraints.Rules.RuleS7Day import RuleS7Day
from Invoke.Constraints.Rules.RuleS7Shift import RuleS7Shift
from Invoke.Constraints.Rules.RuleS6 import RuleS6
from Invoke.Constraints.Rules.RuleS8RefDay import RuleS8RefDay

class Solution:
    """
    Class to store solutions of the problem
    """

    def __init__(self, other_solution=None):

        if other_solution:
            # get day_collection
            self.day_collection = other_solution.day_collection
            self.rule_collection = other_solution.rule_collection
            self.rules = other_solution.rules
            self.k_swap = other_solution.k_swap
            self.num_shift_types = other_solution.num_shift_types

            # employee shift assignments
            self.shift_assignments = other_solution.shift_assignments

            # H2
            self.diff_min_request = other_solution.diff_min_request

            # H3
            self.forbidden_shift_type_successions = other_solution.forbidden_shift_type_successions
            self.last_assigned_shift = other_solution.last_assigned_shift

            # S1
            if 'S1' in self.rules:
                self.diff_opt_request = other_solution.diff_opt_request

            # S2
            if 'S2Max' in self.rules:
                self.work_stretches = other_solution.work_stretches
                self.historical_work_stretch = other_solution.historical_work_stretch

            # S2Shift
            if 'S2ShiftMax' in self.rules:
                self.historical_shift_stretch = other_solution.historical_shift_stretch
                self.shift_stretches = other_solution.shift_stretches

            # S3
            if 'S3Max' in self.rules:
                self.historical_off_stretch = other_solution.historical_off_stretch
                self.day_off_stretches = other_solution.day_off_stretches

            # S5 number of assignments
            if 'S5Max' in self.rules:
                self.num_assignments_per_nurse = other_solution.num_assignments_per_nurse

            # S6 number of working weekends
            if 'S6' in self.rules:
                self.num_working_weekends = other_solution.num_working_weekends

            # S7 similarity
            if 'S7Day' in self.rules:
                self.day_comparison = other_solution.day_comparison
            if 'S7Shift' in self.rules:
                self.shift_comparison = other_solution.shift_comparison
            # S8ref
            if 'S8RefDay' in self.rules or 'S8RefShift' in self.rules or 'S8RefSkill' in self.rules:
                self.ref_assignments = other_solution.ref_assignments

            if 'S8RefDay' in self.rules:
                self.ref_comparison_day_level = other_solution.ref_comparison_day_level

            # objective value
            self.obj_value = other_solution.obj_value

            self.violation_array = other_solution.violation_array
            # information to keep track of solution per nurse
            self.working_days = other_solution.working_days

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
        solution.diff_min_request[
            (change_info['d_index'], change_info['curr_sk_type'], change_info['curr_s_type'])] -= 1

        # working days
        solution.working_days[change_info['employee_id']].remove(change_info['d_index'])
        # soft constraints
        # S1
        if 'S1' in solution.rules:
            solution.diff_opt_request[
                (change_info['d_index'], change_info['curr_sk_type'], change_info['curr_s_type'])] -= 1

        # S2Max and S2Min
        if 'S2Max' in solution.rules:
            solution = RuleS2Max().update_information_assigned_to_off(solution, change_info)

        # S2ShiftMax and S2ShiftMin
        if 'S2ShiftMax' in solution.rules:
            solution = RuleS2ShiftMax().update_information_assigned_to_off(solution, change_info)

        # S3Max and S3Min
        if 'S3Max' in solution.rules:
            solution = RuleS3Max().update_information_assigned_to_off(solution, change_info)

        # S4
        # nothing

        # S5
        if 'S5Max' in solution.rules:
            solution.num_assignments_per_nurse[change_info['employee_id']] -= 1

        # S6
        if 'S6' in solution.rules:
            if change_info['d_index'] in solution.day_collection.list_weekend_days:
                if not solution.check_if_working_day(employee_id=change_info['employee_id'],
                                                     d_index=change_info[
                                                                 'd_index']
                                                             + solution.day_collection.get_index_other_weekend_day(
                                                         solution.day_collection.weekend_day_indices[
                                                             change_info['d_index']])):
                    solution.num_working_weekends[change_info['employee_id']] -= 1

        # S7
        # can use the same function as off to assigned as the result is the same
        if 'S7Day' in solution.rules:
            solution = RuleS7Day().update_information_off_to_assigned(solution, change_info)
        if 'S7Shift' in solution.rules:
            solution = RuleS7Shift().update_information_assigned_to_off(solution, change_info)

        # S8
        if 'S8RefDay' in solution.rules:
            solution = RuleS8RefDay().update_information_off_to_assigned(solution, change_info)

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update relevant information after insertion into new shift skill combination
        """
        # hard constraints
        solution.diff_min_request[(change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1

        # working days
        solution.working_days[change_info['employee_id']].append(change_info['d_index'])

        # soft constraints
        # S1
        if 'S1' in solution.rules:
            solution.diff_opt_request[
                (change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1

        # S2Max and S2Min
        if 'S2Max' in solution.rules:
            solution = RuleS2Max().update_information_off_to_assigned(solution, change_info)

        # S2ShiftMax and S2ShiftMin
        if 'S2ShiftMax' in solution.rules:
            solution = RuleS2ShiftMax().update_information_off_to_assigned(solution, change_info)

        # S3Max
        if 'S3Max' in solution.rules or 'S3Min' in solution.rules:
            solution = RuleS3Max().update_information_off_to_assigned(solution, change_info)

        # S4
        # no changes necessary

        # S5
        if 'S5Max' in solution.rules:
            solution.num_assignments_per_nurse[change_info['employee_id']] += 1

        # S6
        if 'S6' in solution.rules:
            if change_info['d_index'] in solution.day_collection.list_weekend_days:
                if not solution.check_if_working_day(employee_id=change_info['employee_id'],
                                                     d_index=change_info[
                                                                 'd_index'] + solution.day_collection.get_index_other_weekend_day(
                                                         solution.day_collection.weekend_day_indices[
                                                             change_info['d_index']])):
                    solution.num_working_weekends[change_info['employee_id']] += 1

        # S7
        if 'S7Day' in solution.rules:
            solution = RuleS7Day().update_information_off_to_assigned(solution, change_info)
        if 'S7Shift' in solution.rules:
            solution = RuleS7Shift().update_information_off_to_assigned(solution, change_info)

        # S8
        if 'S8RefDay' in solution.rules:
            solution = RuleS8RefDay().update_information_off_to_assigned(solution, change_info)

    def update_information_assigned_to_assigned(self, solution, change_info):
        """
        Update information after moving from one assignment to the other
        """
        # hard constraints
        solution.diff_min_request[(change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1
        solution.diff_min_request[
            (change_info['d_index'], change_info['curr_sk_type'], change_info['curr_s_type'])] -= 1

        # soft constraints
        # S1
        if 'S1' in solution.rules:
            solution.diff_opt_request[
                (change_info['d_index'], change_info['new_sk_type'], change_info['new_s_type'])] += 1
            solution.diff_opt_request[
                (change_info['d_index'], change_info['curr_sk_type'], change_info['curr_s_type'])] -= 1

        # S2ShiftMax
        if 'S2ShiftMax' in solution.rules:
            RuleS2ShiftMax().update_information_assigned_to_assigned(solution, change_info)
        # S2-S6
        # no changes necessary
        # S7Shift
        if 'S7Shift' in solution.rules:
            solution = RuleS7Shift().update_information_assigned_to_assigned(solution, change_info)

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

    def update_solution_operator(self, operator_name, operator_info):
        if operator_name == "change":
            self.update_solution_change(operator_info)
        elif operator_name == "swap":
            self.update_solution_swap(operator_info)

    def update_information_swap(self, solution, swap_info):
        solution.working_days = self.update_working_days_swap(swap_info)
        if "S2Max" in solution.rules or "S2Min" in solution.rules:
            solution = RuleS2Max().update_information_swap(solution, swap_info, "work_stretches")
        if "S2ShiftMax" in solution.rules or "S2ShiftMin" in solution.rules:
            solution = RuleS2ShiftMax().update_information_swap(solution, swap_info, "shift_stretches")
        if "S3Max" in solution.rules or "S3Min" in solution.rules:
            solution = RuleS3Max().update_information_swap(solution, swap_info, "day_off_stretches")
        if "S5Max" in solution.rules:
            solution = RuleS5Max().update_information_swap(solution, swap_info)
        if "S6" in solution.rules:
            solution.num_working_weekends = RuleS6().update_information_swap(solution.num_working_weekends, swap_info)

    def update_solution_swap(self, swap_info):
        """
        Function to implement all changes after swap in the solution
        """
        self.update_information_swap(solution=self, swap_info=swap_info)

        # swap assignment of nurses in shift assignment
        self.swap_assignments(swap_info['start_index'], swap_info['end_index'],
                              swap_info['employee_id_1'], swap_info['employee_id_2'])

        # change objective value
        self.obj_value += swap_info['cost_increment']
        self.violation_array += swap_info['violation_increment']

    def swap_assignments(self, start_index, end_index, employee_id_1, employee_id_2):
        # TODO check whether swap is made
        # save stretch of employee 1
        stretch_1 = self.shift_assignments[employee_id_1][start_index:end_index + 1, ].copy()

        # replace stretch of employee 1 with the one from employee 2
        self.shift_assignments[employee_id_1][start_index:end_index + 1, ] \
            = self.shift_assignments[employee_id_2][start_index:end_index + 1, ]

        # replace stretch of employee 1 with the one from employee 2
        self.shift_assignments[employee_id_2][start_index:end_index + 1, ] \
            = stretch_1

    def update_working_days_swap(self, swap_info):
        new_working_days = {}
        for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
            other_employee_id = swap_info['employee_id_{}'.format(2 - i)]

            new_working_days[employee_id] \
                = [d_index for d_index in range(0, self.day_collection.num_days_in_horizon)
                   if d_index in self.get_working_days_in_range(other_employee_id, swap_info['start_index'],
                                                                swap_info['end_index'])
                   or (d_index in self.working_days[employee_id]
                       and d_index not in self.get_working_days_in_range(employee_id, swap_info['start_index'],
                                                                         swap_info['end_index']))]

        self.working_days[swap_info['employee_id_1']] = new_working_days[swap_info['employee_id_1']]
        self.working_days[swap_info['employee_id_2']] = new_working_days[swap_info['employee_id_2']]
        return self.working_days

    def get_working_days_in_range(self, employee_id, start_index, end_index):
        return [d_index for d_index in self.working_days[employee_id]
                if start_index <= d_index <= end_index]

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

    def check_if_same_shift_type(self, employee_id, d_index_1, d_index_2):
        return self.shift_assignments[employee_id][d_index_1][0] \
               == self.shift_assignments[employee_id][d_index_2][0]

    def create_stretch(self, stretch_object_employee, start_index, end_index):
        stretch_object_employee[start_index] = {"end_index": end_index,
                                                "length": end_index-start_index + 1}
        return stretch_object_employee

    def check_if_working_day_ref(self, employee_id, d_index):
        return self.ref_assignments[employee_id][d_index][0] > -1
