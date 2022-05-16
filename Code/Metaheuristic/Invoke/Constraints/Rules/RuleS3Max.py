from Invoke.Constraints.initialize_rules import Rule
from Invoke.Constraints.Rules.RuleS2Max import RuleS2Max
import numpy as np


class RuleS3Max(Rule):
    """
        Rule that check for the maximum number of consecutive days off
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, employee_id):
        """
        Function to count violations for an employee
        """
        return sum([day_off_stretch['length'] - self.parameter_per_employee[employee_id]
                    for day_off_stretch in solution.day_off_stretches[employee_id].values()
                    if day_off_stretch['length'] > self.parameter_per_employee[employee_id]
                    and day_off_stretch['end_index'] > -1])

    def find_day_off_stretch_end(self, solution, employee_id, d_index):
        """
        Find key of work stretch given that d_index is the last day
        """
        for s_index, day_off_stretch in solution.day_off_stretches[employee_id].items():
            if day_off_stretch['end_index'] == d_index:
                return s_index

    def find_day_off_stretch_middle(self, solution, employee_id, d_index):
        """
       Find key of work stretch given that d_index is the last day
       """
        for s_index, day_off_stretch in solution.day_off_stretches[employee_id].items():
            if d_index in range(s_index + 1, day_off_stretch['end_index']):
                return s_index

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update solution information after change from off to assigned
        """
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        # check if not the last or first day and in a work stretch
        if solution.check_if_middle_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1) \
                and not solution.check_if_working_day(employee_id, d_index - 1):

            start_index = self.find_day_off_stretch_middle(solution, employee_id, d_index)
            # # add new key value for second new work stretch
            # solution.day_off_stretches[employee_id][
            #     d_index + 1] \
            #     = {
            #     'end_index': solution.day_off_stretches[
            #         employee_id][
            #         start_index]['end_index'],
            #     'length': solution.day_off_stretches[
            #                   employee_id][
            #                   start_index]['end_index'] - d_index
            # }
            #
            # # change end index and length of first new work stretch
            # solution.day_off_stretches[employee_id][start_index]['end_index'] \
            #     = d_index - 1
            # solution.day_off_stretches[employee_id][start_index]['length'] \
            #     = d_index - start_index

            solution.day_off_stretches[employee_id] \
                = RuleS2Max().split_stretch(solution.day_off_stretches[employee_id],
                                            start_index_1=start_index,
                                            d_index=d_index)

        # check if not the last day and the day after off
        elif not solution.check_if_last_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_off_stretch[employee_id] > 0:
                # shorten existing stretch
                solution.day_off_stretches[employee_id] = RuleS2Max().shorten_stretch_pre(
                    stretch_object_employee=solution.day_off_stretches[employee_id],
                    old_start=-solution.historical_off_stretch[employee_id],
                    new_start=d_index + 1)

                # create new stretch for historical stretch
                solution.day_off_stretches[employee_id] = solution.create_work_stretch(
                    stretch_object_employee=solution.day_off_stretches[employee_id],
                    start_index=-solution.historical_off_stretch[employee_id],
                    end_index=-1)
            else:
                solution.day_off_stretches[employee_id] = RuleS2Max().shorten_stretch_pre(
                    stretch_object_employee=solution.day_off_stretches[employee_id],
                    old_start=d_index,
                    new_start=d_index + 1)

        # check if not the first day and the day before off
        elif not d_index == 0 \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id, d_index)
            solution.day_off_stretches[employee_id][start_index]['end_index'] \
                -= 1
            solution.day_off_stretches[employee_id][start_index]['length'] \
                -= 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_off_stretch[employee_id] > 0:
                start_index = -solution.historical_off_stretch[employee_id]
                solution.day_off_stretches[employee_id][start_index]['end_index'] \
                    -= 1
                solution.day_off_stretches[employee_id][start_index]['length'] \
                    -= 1
            else:
                del solution.day_off_stretches[
                    employee_id][d_index]

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update solution information after change from assigned to off
        """
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        if solution.check_if_middle_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1) \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id, d_index - 1)

            # # replace end_index of new work stretch with last
            # solution.day_off_stretches[
            #     employee_id][
            #     start_index][
            #     "end_index"] \
            #     = solution.day_off_stretches[
            #     employee_id][
            #     d_index + 1][
            #     'end_index'
            # ]
            # # compute new length
            # solution.day_off_stretches[
            #     employee_id][
            #     start_index][
            #     "length"] \
            #     += solution.day_off_stretches[
            #            employee_id][
            #            d_index + 1]['length'] + 1
            #
            # # remove unnecessary stretch
            # solution.day_off_stretches[
            #     employee_id].pop(d_index + 1)

            solution.day_off_stretches[employee_id] = \
                RuleS2Max().merge_stretches(solution.day_off_stretches[employee_id],
                                            start_index_1=start_index,
                                            start_index_2=d_index + 1)

            # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_off_stretch[employee_id] > 0:
                solution.day_off_stretches[employee_id] \
                    = RuleS2Max().extend_stretch_pre(
                    stretch_object_employee=solution.day_off_stretches[employee_id],
                    old_start=d_index + 1,
                    new_start=-solution.historical_off_stretch[employee_id])
            else:
                solution.day_off_stretches[employee_id] \
                    = RuleS2Max().extend_stretch_pre(
                    stretch_object_employee=solution.day_off_stretches[employee_id],
                    old_start=d_index + 1,
                    new_start=d_index)

        elif not solution.check_if_first_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id, d_index - 1)
            # change end index by one
            solution.day_off_stretches[
                employee_id][start_index]['end_index'] += 1

            solution.day_off_stretches[
                employee_id][start_index]['length'] += 1

            # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_off_stretch[employee_id] > 0:
                start_index = -solution.historical_off_stretch[employee_id]

                # change end index by one
                solution.day_off_stretches[
                    employee_id][start_index]['end_index'] += 1

                solution.day_off_stretches[
                    employee_id][start_index]['length'] += 1
            else:
                # create index of single length
                solution.day_off_stretches[employee_id][d_index] \
                    = {'end_index': d_index,
                       'length': 1}

        return solution

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
            return 0

    def incremental_violations_off_to_assigned(self, solution, change_info):
        d_index = change_info['d_index']
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]

        # find in what day off stretch the d_index is
        for start_index, day_off_stretch in solution.day_off_stretches[change_info['employee_id']].items():
            if d_index in range(start_index, day_off_stretch["end_index"] + 1):
                split_1 = d_index - start_index
                split_2 = day_off_stretch['end_index'] - d_index

                return -(np.maximum(day_off_stretch['length'] - employee_parameter, 0)
                         - np.maximum(split_1 - employee_parameter, 0)
                         - np.maximum(split_2 - employee_parameter, 0))

    def incremental_violations_assigned_to_off(self, solution, change_info):
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']

        employee_parameter = self.parameter_per_employee[employee_id]
        if solution.check_if_middle_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1) \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id,
                                                        d_index - 1)

            # # calc previous violations of the separate work stretches
            # previous_violations = np.maximum(
            #     solution.day_off_stretches[employee_id][
            #         d_index + 1]['length'] - employee_parameter,
            #     0) \
            #                       + np.maximum(
            #     solution.day_off_stretches[employee_id][start_index]['length'] - employee_parameter,
            #     0)
            # return np.maximum((solution.day_off_stretches[employee_id][
            #                        d_index + 1]['length']
            #                    + solution.day_off_stretches[employee_id][start_index][
            #                        'length'] + 1) - employee_parameter, 0) \
            #        - previous_violations
            return RuleS2Max().calc_incremental_violations_merge_stretch(solution.day_off_stretches[employee_id],
                                                                         rule_parameter=employee_parameter,
                                                                         start_index_1=start_index,
                                                                         start_index_2=d_index + 1)

        # check if not the last day and the day after off
        elif not solution.check_if_last_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_off_stretch[employee_id] > 0:
                previous_violations = np.maximum(
                    solution.day_off_stretches[employee_id][
                        d_index + 1]['length'] - employee_parameter,
                    0)
                # adapt violations compared to whether there is history before
                new_violations = np.maximum(solution.day_off_stretches[employee_id][
                                                d_index + 1]['length']
                                            + solution.historical_off_stretch[
                                                employee_id] + 1 - employee_parameter, 0)

                return new_violations - previous_violations
            else:
                # check whether the length of the new work stretch is longer than allowed
                return 1 if solution.day_off_stretches[employee_id][
                                d_index + 1]['length'] >= employee_parameter \
                    else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id,
                                                        d_index - 1)
            # check if the length of the new work stretch is too long
            return 1 if solution.day_off_stretches[employee_id][start_index][
                            'length'] >= employee_parameter \
                else 0

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_off_stretch[employee_id] > 0:
                start_index = -solution.historical_off_stretch[employee_id]
                # check if the length of the new work stretch is too long
                return 1 if solution.day_off_stretches[employee_id][start_index][
                                'length'] >= employee_parameter \
                    else 0
            else:
                return 0
