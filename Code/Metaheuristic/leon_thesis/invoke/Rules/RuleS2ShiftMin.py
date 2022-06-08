from invoke.Domain.RuleCollection import Rule
from invoke.Rules.RuleS2Min import RuleS2Min
import numpy as np


class RuleS2ShiftMin(Rule):
    """
        Rule that checks for optimal coverage per skill request
        Compares optimal skill request to number of nurses with that skill assigned to shift
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_shift(solution, scenario, s_index)
                    for s_index in scenario.shift_collection.shift_types_indices])

    def count_violations_shift(self, solution, scenario, s_index):
        """
        Function to count violations for an employee
        """
        return sum(
            [self.count_violations_shift_employee(solution.shift_stretches[s_index][employee_id], s_index, employee_id)
             for employee_id in scenario.employees._collection.keys()])

    def count_violations_shift_employee(self, work_stretch_employee_shift, s_index, employee_id):
        return sum([np.maximum(self.parameter_per_s_type[s_index] - shift_stretch['length'], 0)
                    for shift_stretch in work_stretch_employee_shift.values()])

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        delta number_of_violations
        """

        # check if moving from off to assigned
        if not change_info['current_working']:
            return self.incremental_violations_off_to_assigned(solution, change_info)

        # check if moving from assigned to off
        elif not change_info['new_working']:
            return self.incremental_violations_assigned_to_off(solution, change_info)
        else:
            return self.incremental_violations_assigned_to_assigned(solution, change_info)

    def incremental_violations_off_to_assigned(self, solution, change_info):
        """
        Incremental violations off to assigned
        """
        d_index = change_info['d_index']
        employee_id = change_info['employee_id']
        new_s_type = change_info['new_s_type']
        shift_parameter = self.parameter_per_s_type[new_s_type]

        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, new_s_type) \
                and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, new_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index - 1, new_s_type)

            previous_violations = np.maximum(
                shift_parameter - solution.shift_stretches[new_s_type][employee_id][d_index + 1]['length'], 0) \
                                  + np.maximum(
                shift_parameter - solution.shift_stretches[new_s_type][employee_id][start_index]['length'], 0)
            new_violations = np.maximum(shift_parameter
                                        - (solution.shift_stretches[new_s_type][employee_id][d_index + 1]['length']
                                           + solution.shift_stretches[new_s_type][employee_id][start_index]['length']
                                           + 1), 0)
            return -(previous_violations - new_violations)
        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, new_s_type):
            # if first day and history before
            if change_info['d_index'] == 0 and solution.last_assigned_shift[employee_id] == new_s_type:
                return RuleS2Min().calc_incremental_violations_merge_stretch(
                    solution.shift_stretches[new_s_type][employee_id],
                    rule_parameter=shift_parameter,
                    start_index_1=-solution.historical_shift_stretch[
                        employee_id],
                    start_index_2=d_index + 1)
            else:
                return -1 if solution.shift_stretches[new_s_type][employee_id][d_index + 1][
                                 'length'] < shift_parameter else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, new_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index - 1, new_s_type)
            return -1 if solution.shift_stretches[new_s_type][employee_id][start_index][
                             'length'] < shift_parameter else 0

        # if single day
        else:
            if d_index == 0 and solution.last_assigned_shift[employee_id] == new_s_type:
                start_index = -solution.historical_shift_stretch[employee_id]
                return -1 if solution.shift_stretches[new_s_type][employee_id][start_index][
                                 'length'] < shift_parameter else 0
            else:
                return np.maximum(shift_parameter - 1, 0)

    def incremental_violations_assigned_to_off(self, solution, change_info):
        shift_parameter = self.parameter_per_s_type[change_info['curr_s_type']]
        length_1, length_2, the_shift_stretch = None, None, None
        # find in what work stretch the d_index is
        for start_index, shift_stretch in solution.shift_stretches[
            change_info['curr_s_type']][change_info['employee_id']].items():
            if change_info['d_index'] in range(start_index, shift_stretch["end_index"] + 1):
                # calc length of remaining stretches
                length_1 = change_info['d_index'] - start_index if change_info[
                                                                       'd_index'] - start_index > 0 else shift_parameter
                length_2 = shift_stretch['end_index'] - change_info['d_index'] if shift_stretch['end_index'] - \
                                                                                  change_info[
                                                                                      'd_index'] > 0 else shift_parameter
                the_shift_stretch = shift_stretch
                break
        # add extra violations
        new_violations_1 = np.maximum(shift_parameter - length_1, 0) if change_info[
                                                                            'd_index'] != 0 and length_1 > 0 else 0

        # add extra violations
        # the new violations - the old violations
        return new_violations_1 \
               + np.maximum(shift_parameter - length_2, 0) \
               - np.maximum(shift_parameter - the_shift_stretch['length'], 0)

    def incremental_violations_assigned_to_assigned(self, solution, change_info):
        """
                Count incremental violations assigned --> assigned
                """
        # if new shift type the same as old shift type, no change in violations
        if change_info['curr_s_type'] == change_info['new_s_type']:
            return 0
        else:
            # if different, we need to check the violations for removing the old shift type
            # and adding the new shift type
            return self.incremental_violations_off_to_assigned(solution, change_info) \
                   + self.incremental_violations_assigned_to_off(solution, change_info)

    def find_shift_stretch_end(self, solution, employee_id, d_index, s_index):
        """
        Find key of work stretch given that d_index is the last day
        """
        for start_index, shift_stretch in solution.shift_stretches[s_index][employee_id].items():
            if shift_stretch['end_index'] == d_index:
                return start_index

    def find_shift_stretch_middle(self, solution, employee_id, d_index, s_index):
        """
       Find key of work stretch given that d_index is the last day
       """
        for start_index, shift_stretch in solution.shift_stretches[s_index][employee_id].items():
            if d_index in range(start_index + 1, shift_stretch['end_index']):
                return start_index

    def incremental_violations_swap(self, solution, swap_info, rule_id):
        """
        Function to calculate the incremental violations after a swap operation
        """

        incremental_violations = 0
        for s_index in range(0, solution.num_shift_types):
            stretch_name = 'shift_stretches_{}'.format(s_index)
            stretch_object = solution.shift_stretches[s_index]
            for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
                old_violations = self.count_violations_shift_employee(stretch_object[employee_id], s_index, employee_id)
                new_violations = self.count_violations_shift_employee(swap_info['{}_new'.format(stretch_name)][employee_id],
                                                                s_index,
                                                                employee_id)
                incremental_violations += new_violations - old_violations
        return incremental_violations
