from leon_thesis.invoke.Constraints.initialize_rules import Rule
import numpy as np
from leon_thesis.invoke.Constraints.Rules.RuleS2Max import RuleS2Max


class RuleS2ShiftMax(Rule):
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
        return sum([self.count_violations_shift(solution.shift_stretches, scenario, s_index)
                    for s_index in scenario.shift_collection.shift_types_indices])

    def count_violations_shift(self, shift_stretches, scenario, s_index):
        """
        Function to count violations for an employee
        """
        return sum([self.count_violations_shift_employee(shift_stretches[s_index][employee_id], s_index, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_shift_employee(self, work_stretch_employee_shift, s_index, employee_id):
        return sum([np.maximum(shift_stretch['length'] - self.parameter_per_s_type[s_index], 0)
                    for shift_stretch in work_stretch_employee_shift.values()])

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
            if d_index in range(start_index+1, shift_stretch['end_index']):
                return start_index

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update solution information after change from off to assigned
        """
        d_index = change_info['d_index']
        employee_id = change_info['employee_id']
        new_s_type = change_info['new_s_type']

        if solution.check_if_middle_day(d_index) \
        and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, new_s_type) \
        and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, new_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index-1, new_s_type)

            solution.shift_stretches[new_s_type][employee_id] \
                = RuleS2Max().merge_stretches(solution.shift_stretches[new_s_type][employee_id],
                                               start_index_1=start_index,
                                               start_index_2=d_index+1)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index)\
                and solution.check_if_working_s_type_on_day(employee_id, d_index+1, new_s_type):

            if d_index == 0 and solution.last_assigned_shift[employee_id] == new_s_type:
                solution.shift_stretches[new_s_type][employee_id] \
                    = RuleS2Max().extend_stretch_pre(
                    stretch_object_employee=solution.shift_stretches[new_s_type][employee_id],
                    old_start=d_index + 1,
                    new_start=-solution.historical_shift_stretch[employee_id])
            else:
                solution.shift_stretches[new_s_type][employee_id] \
                    = RuleS2Max().extend_stretch_pre(
                    solution.shift_stretches[new_s_type][employee_id],
                    old_start=d_index+1,
                    new_start=d_index)

        elif not solution.check_if_first_day(d_index) \
            and solution.check_if_working_s_type_on_day(employee_id, d_index-1, new_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index-1, new_s_type)
            # change end index by one
            solution.shift_stretches[
                new_s_type][employee_id][start_index]['end_index'] += 1

            solution.shift_stretches[
                new_s_type][employee_id][start_index]['length'] += 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.last_assigned_shift[employee_id] == new_s_type:
                start_index = -solution.historical_shift_stretch[employee_id]

                # change end index by one
                solution.shift_stretches[
                    new_s_type][employee_id][start_index]['end_index'] += 1

                solution.shift_stretches[
                    new_s_type][employee_id][start_index]['length'] += 1
            else:
                # create index of single length
                solution.shift_stretches[new_s_type][employee_id][d_index] \
                    = {'end_index': d_index,
                       'length': 1}

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update solution information after change from assigned to off
        """
        d_index = change_info['d_index']
        employee_id = change_info['employee_id']
        curr_s_type = change_info['curr_s_type']

        # check if not the last or first day and in a work stretch
        if solution.check_if_middle_day(d_index) \
             and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, curr_s_type) \
             and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, curr_s_type):

            start_index = self.find_shift_stretch_middle(solution, employee_id, d_index, curr_s_type)

            solution.shift_stretches[curr_s_type][employee_id] \
                = RuleS2Max().split_stretch(
                solution.shift_stretches[curr_s_type][employee_id],
                start_index_1=start_index,
                d_index=d_index)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, curr_s_type):

            if d_index == 0 and solution.last_assigned_shift[employee_id] == curr_s_type:
                # shorten existing stretch
                solution.shift_stretches[curr_s_type][employee_id] = RuleS2Max().shorten_stretch_pre(
                    stretch_object_employee=solution.shift_stretches[curr_s_type][employee_id],
                    old_start=-solution.historical_shift_stretch[employee_id],
                    new_start=d_index + 1)

                # create new stretch for historical stretch
                solution.shift_stretches[curr_s_type][employee_id] = solution.create_stretch(
                    stretch_object_employee=solution.shift_stretches[curr_s_type][employee_id],
                    start_index=-solution.historical_shift_stretch[employee_id],
                    end_index=-1)
            else:
                solution.shift_stretches[curr_s_type][employee_id] \
                    = RuleS2Max().shorten_stretch_pre(
                    solution.shift_stretches[curr_s_type][employee_id],
                    old_start=d_index,
                    new_start=d_index+1)

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, curr_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index, curr_s_type)
            solution.shift_stretches[curr_s_type][employee_id][start_index]['end_index'] \
                -= 1
            solution.shift_stretches[curr_s_type][employee_id][start_index]['length'] \
                -= 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.last_assigned_shift[employee_id] == curr_s_type:
                start_index = -solution.historical_shift_stretch[employee_id]
                solution.shift_stretches[curr_s_type][employee_id][start_index]['end_index'] \
                    -= 1
                solution.shift_stretches[curr_s_type][employee_id][start_index]['length'] \
                    -= 1
            else:
                del solution.shift_stretches[
                    curr_s_type][employee_id][d_index]

        return solution

    def update_information_assigned_to_assigned(self, solution, change_info):
        # if new shift type the same as old shift type, no change in violations
        if change_info['curr_s_type'] == change_info['new_s_type']:
            return solution
        else:
            # if different, we need to check the violations for removing the old shift type
            # and adding the new shift type
            solution = self.update_information_assigned_to_off(solution, change_info)
            return self.update_information_off_to_assigned(solution, change_info)

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
        d_index = change_info['d_index']
        employee_id = change_info['employee_id']
        new_s_type = change_info['new_s_type']
        shift_parameter = self.parameter_per_s_type[new_s_type]

        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, new_s_type) \
                and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, new_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index-1, new_s_type)
            # calc previous violations of the separate work stretches
            previous_violations = np.maximum(
                solution.shift_stretches[new_s_type][employee_id][
                    d_index + 1]['length'] - shift_parameter, 0) \
                                  + np.maximum(
                solution.shift_stretches[new_s_type][employee_id][start_index]['length'] - shift_parameter,0)

            new_violations = np.maximum(
                (solution.shift_stretches[new_s_type][employee_id][
                                   d_index + 1]['length']
                               + solution.shift_stretches[new_s_type][employee_id][start_index][
                                   'length'] + 1)
                - shift_parameter, 0)
            return new_violations - previous_violations
        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
            and solution.check_if_working_s_type_on_day(employee_id, d_index + 1, new_s_type):
            # check whether the length of the new work stretch is longer than allowed
            return 1 if solution.shift_stretches[new_s_type][employee_id][
                            d_index + 1]['length'] >= shift_parameter \
                else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_s_type_on_day(employee_id, d_index - 1, new_s_type):
            start_index = self.find_shift_stretch_end(solution, employee_id, d_index-1, new_s_type)
            # check if the length of the new work stretch is too long
            return 1 if solution.shift_stretches[new_s_type][employee_id][start_index]['length'] >= shift_parameter \
                else 0

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.last_assigned_shift[employee_id] == new_s_type:
                start_index = -solution.historical_shift_stretch[employee_id]
                # check if the length of the new work stretch is too long
                return 1 if solution.shift_stretches[new_s_type][employee_id][start_index][
                                'length'] >= shift_parameter \
                    else 0
            else:
                return 0

    def incremental_violations_assigned_to_off(self, solution, change_info):
        shift_parameter = self.parameter_per_s_type[change_info['curr_s_type']]
        violation = False
        # find in what work stretch the d_index is
        for start_index, shift_stretch in solution.shift_stretches[change_info['curr_s_type']][change_info['employee_id']].items():
            if change_info['d_index'] in range(start_index, shift_stretch["end_index"]+1):
                split_1 = change_info['d_index'] - start_index
                split_2 = shift_stretch['end_index'] - change_info['d_index']
                violation = True

                return -(np.maximum(shift_stretch['length'] - shift_parameter, 0)
                         - np.maximum(split_1 - shift_parameter, 0)
                         - np.maximum(split_2 - shift_parameter, 0))

        if not violation:
            return 0

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

    def update_information_swap(self, solution, swap_info, stretch_name):
        """
        function to update the information collected
        """
        for s_index in range(0, solution.num_shift_types):
            shift_stretch_name = stretch_name + "_{}".format(s_index)
            solution.shift_stretches[s_index] = swap_info['{}_new'.format(shift_stretch_name)]

        return solution










