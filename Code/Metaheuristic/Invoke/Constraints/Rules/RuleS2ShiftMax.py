from Invoke.Constraints.initialize_rules import Rule
import numpy as np


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
        return sum([self.count_violations_employee(solution, scenario, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, scenario, employee_id):
        """
        Function to count violations for an employee
        """
        return sum([self.count_violations_employee_shift(solution, employee_id, s_index)
                    for s_index in scenario.shift_collection.shift_types_indices])

    def count_violations_employee_shift(self, solution, employee_id, s_index):
        return sum([shift_stretch['length'] - self.parameter_per_s_type[s_index]
                    for shift_stretch in solution.shift_stretches[employee_id][s_index].values()
                    if shift_stretch['length'] > self.parameter_per_s_type[s_index]])

    def find_shift_stretch_end(self, solution, employee_id, d_index, s_index):
        """
        Find key of work stretch given that d_index is the last day
        """
        for start_index, shift_stretch in solution.shift_stretches[employee_id][s_index].items():
            if shift_stretch['end_index'] == d_index:
                return start_index

    def find_shift_stretch_middle(self, solution, employee_id, d_index, s_index):
        """
       Find key of work stretch given that d_index is the last day
       """
        for start_index, shift_stretch in solution.shift_stretches[employee_id][s_index].items():
            if d_index in range(s_index+1, shift_stretch['end_index']):
                return start_index

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update solution information after change from off to assigned
        """

        if solution.check_if_middle_day(change_info['d_index']) \
        and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] + 1, change_info['new_s_type']) \
        and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] - 1, change_info['new_s_type']):
            start_index = self.find_shift_stretch_end(solution, change_info['employee_id'], change_info['d_index']-1, change_info['new_s_type'])

            # replace end_index of new work stretch with last
            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][
                start_index][
                "end_index"] \
                = solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][
                change_info['d_index'] + 1][
                'end_index'
            ]
            # compute new length
            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][
                start_index][
                "length"] \
                += solution.shift_stretches[
                       change_info['employee_id']][change_info['new_s_type']][
                       change_info['d_index'] + 1]['length'] + 1

            # remove unnecessary stretch
            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']].pop(change_info['d_index'] + 1)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(change_info['d_index'])\
                and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index']+1, change_info['new_s_type']):

            # create change key of dictionary
            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][change_info['d_index']] = solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][change_info['d_index'] + 1]
            # adjust length
            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][change_info['d_index']]['length'] += 1

            del solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][change_info['d_index'] + 1]

        elif not solution.check_if_first_day(change_info['d_index']) \
            and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index']-1, change_info['new_s_type']):
            start_index = self.find_shift_stretch_end(solution, change_info['employee_id'], change_info['d_index']-1, change_info['new_s_type'])
            # change end index by one
            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][start_index]['end_index'] += 1

            solution.shift_stretches[
                change_info['employee_id']][change_info['new_s_type']][start_index]['length'] += 1

        # if single day
        else:
            # create index of single length
            solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][change_info['d_index']] \
                = {'end_index': change_info['d_index'],
                   'length': 1}

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update solution information after change from assigned to off
        """
        # check if not the last or first day and in a work stretch
        if solution.check_if_middle_day(change_info['d_index']) \
             and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] + 1, change_info['curr_s_type']) \
             and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] - 1, change_info['curr_s_type']):

            start_index = self.find_shift_stretch_middle(solution, change_info['employee_id'], change_info['d_index'], change_info['curr_s_type'])
            # add new key value for second new work stretch
            solution.shift_stretches[change_info['employee_id']][change_info['curr_s_type']][
                change_info['d_index'] + 1] \
                = {
                'end_index': solution.shift_stretches[
                    change_info['employee_id']][change_info['curr_s_type']][
                    start_index]['end_index'],
                'length': solution.shift_stretches[
                              change_info['employee_id']][change_info['curr_s_type']][
                              start_index]['end_index'] - change_info['d_index']
            }

            # change end index and length of first new work stretch
            solution.shift_stretches[change_info['employee_id']][change_info['curr_s_type']][start_index]['end_index'] \
                = change_info['d_index'] - 1
            solution.shift_stretches[change_info['employee_id']][change_info['curr_s_type']][start_index]['length'] \
                = change_info['d_index'] - start_index

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(change_info['d_index']) \
                and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] + 1, change_info['curr_s_type']):
            # change start index of old key
            solution.shift_stretches[
                change_info['employee_id']][change_info['curr_s_type']][change_info['d_index'] + 1] \
                = solution.shift_stretches[
                change_info['employee_id']][change_info['curr_s_type']][change_info['d_index']]
            # change the length of the stretch
            solution.shift_stretches[
                change_info['employee_id']][change_info['curr_s_type']][change_info['d_index'] + 1]['length'] -= 1
            del solution.shift_stretches[
                change_info['employee_id']][change_info['curr_s_type']][change_info['d_index']]

        # check if not the first day and the day before working
        elif not change_info['d_index'] == 0 \
                and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] - 1, change_info['curr_s_type']):
            start_index = self.find_shift_stretch_end(solution, change_info['employee_id'], change_info['d_index'], change_info['curr_s_type'])
            solution.shift_stretches[change_info['employee_id']][change_info['curr_s_type']][start_index]['end_index'] \
                -= 1
            solution.shift_stretches[change_info['employee_id']][change_info['curr_s_type']][start_index]['length'] \
                -= 1

        # if single day
        else:
            del solution.shift_stretches[
                change_info['employee_id']][change_info['curr_s_type']][change_info['d_index']]

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
        try:
            shift_parameter = self.parameter_per_s_type[change_info['new_s_type']]
        except KeyError:
            print("hi")
            a = 6

        if solution.check_if_middle_day(change_info['d_index']) \
                and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] + 1, change_info['new_s_type']) \
                and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] - 1, change_info['new_s_type']):
            start_index = self.find_shift_stretch_end(solution, change_info['employee_id'], change_info['d_index']-1, change_info['new_s_type'])
            # calc previous violations of the separate work stretches
            previous_violations = np.maximum(
                solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][
                    change_info['d_index'] + 1]['length'] - shift_parameter,
                0) \
                                  + np.maximum(
                solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][start_index]['length'] - shift_parameter,
                0)
            return np.maximum((solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][
                                   change_info['d_index'] + 1]['length']
                               + solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][start_index][
                                   'length'] + 1) - shift_parameter, 0) \
                   - previous_violations
        # check if not the last day and the day after working
        elif not solution.check_if_last_day(change_info['d_index']) \
            and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] + 1, change_info['new_s_type']):
            # check whether the length of the new work stretch is longer than allowed
            return 1 if solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][
                            change_info['d_index'] + 1]['length'] >= shift_parameter \
                else 0


        # check if not the first day and the day before working
        elif not change_info['d_index'] == 0 \
                and solution.check_if_working_s_type_on_day(change_info['employee_id'], change_info['d_index'] - 1, change_info['new_s_type']):
            start_index = self.find_shift_stretch_end(solution, change_info['employee_id'], change_info['d_index']-1, change_info['new_s_type'])
            # check if the length of the new work stretch is too long
            return 1 if solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']][start_index]['length'] >= shift_parameter \
                else 0

        # if single day
        else:
            return 0

    def incremental_violations_assigned_to_off(self, solution, change_info):
        shift_parameter = self.parameter_per_s_type[change_info['curr_s_type']]

        # find in what work stretch the d_index is
        for start_index, shift_stretch in solution.shift_stretches[change_info['employee_id']][change_info['new_s_type']].items():
            if change_info['d_index'] in range(start_index, shift_stretch["end_index"]+1):
                split_1 = change_info['d_index'] - start_index
                split_2 = shift_stretch['end_index'] - change_info['d_index']

                return -(np.maximum(shift_stretch['length'] - shift_parameter, 0)
                         - np.maximum(split_1 - shift_parameter, 0)
                         - np.maximum(split_2 - shift_parameter, 0))


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













