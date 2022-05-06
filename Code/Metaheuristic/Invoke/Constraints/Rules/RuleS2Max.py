from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS2Max(Rule):
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
        return sum([self.count_violations_employee(solution, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, employee_id):
        """
        Function to count violations for an employee
        """
        return sum([work_stretch['length'] - self.parameter_per_employee[employee_id]
                    for work_stretch in solution.work_stretches[employee_id].values()
                    if work_stretch['length'] > self.parameter_per_employee[employee_id]])

    def find_work_stretch_end(self, solution, employee_id, d_index):
        """
        Find key of work stretch given that d_index is the last day
        """
        for s_index, work_stretch in solution.work_stretches[employee_id].items():
            if work_stretch['end_index'] == d_index:
                return s_index

    def find_work_stretch_middle(self, solution, employee_id, d_index):
        """
       Find key of work stretch given that d_index is the last day
       """
        for s_index, work_stretch in solution.work_stretches[employee_id].items():
            if d_index in range(s_index+1, work_stretch['end_index']):
                return s_index

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update solution information after change from off to assigned
        """
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        if solution.check_if_middle_day(d_index) \
        and solution.check_if_working_day(employee_id, d_index + 1) \
        and solution.check_if_working_day(employee_id, d_index - 1):
            start_index_1 = self.find_work_stretch_end(solution, employee_id, d_index-1)

            solution.work_stretches[employee_id] = \
                self.merge_stretches(solution.work_stretches[employee_id],
                                 start_index_1=start_index_1,
                                 start_index_2=d_index + 1)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index)\
                and solution.check_if_working_day(employee_id, d_index+1):
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                solution.work_stretches[employee_id] \
                    = self.extend_stretch_pre(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    old_start=d_index + 1,
                    new_start=-solution.historical_work_stretch[employee_id])

            else:
                solution.work_stretches[employee_id] \
                    = self.extend_stretch_pre(stretch_object_employee=solution.work_stretches[employee_id],
                                              old_start=d_index+1,
                                              new_start=d_index)


        elif not solution.check_if_first_day(d_index) \
            and solution.check_if_working_day(employee_id, d_index-1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index-1)
            # change end index by one
            solution.work_stretches[
                employee_id][start_index]['end_index'] += 1

            solution.work_stretches[
                employee_id][start_index]['length'] += 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                start_index = -solution.historical_work_stretch[employee_id]

                # change end index by one
                solution.work_stretches[
                    employee_id][start_index]['end_index'] += 1

                solution.work_stretches[
                    employee_id][start_index]['length'] += 1
            else:
                # create index of single length
                solution.work_stretches[employee_id][d_index] \
                    = {'end_index': d_index,
                       'length': 1}

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update solution information after change from assigned to off
        """
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        # check if not the last or first day and in a work stretch
        if solution.check_if_middle_day(d_index) \
             and solution.check_if_working_day(employee_id, d_index + 1) \
             and solution.check_if_working_day(employee_id, d_index - 1):

            start_index = self.find_work_stretch_middle(solution, employee_id, d_index)
            # # add new key value for second new work stretch
            # solution.work_stretches[employee_id][
            #     d_index + 1] \
            #     = {
            #     'end_index': solution.work_stretches[
            #         employee_id][
            #         start_index]['end_index'],
            #     'length': solution.work_stretches[
            #                   employee_id][
            #                   start_index]['end_index'] - d_index
            # }
            #
            # # change end index and length of first new work stretch
            # solution.work_stretches[employee_id][start_index]['end_index'] \
            #     = d_index - 1
            # solution.work_stretches[employee_id][start_index]['length'] \
            #     = d_index - start_index

            solution.work_stretches[employee_id] \
                = RuleS2Max().split_stretch(
                solution.work_stretches[employee_id],
                    start_index_1=start_index,
                    d_index=d_index)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                # shorten existing stretch
                solution.work_stretches[employee_id] = self.shorten_stretch_pre(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    old_start=-solution.historical_work_stretch[employee_id],
                    new_start=d_index + 1)

                # create new stretch for historical stretch
                solution.work_stretches[employee_id] = solution.create_work_stretch(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    start_index=-solution.historical_work_stretch[employee_id],
                    end_index=-1)
            else:
                solution.work_stretches[employee_id] = self.shorten_stretch_pre(
                    stretch_object_employee=solution.work_stretches[employee_id],
                old_start=d_index,
                new_start=d_index+1)

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index)
            solution.work_stretches[employee_id][start_index]['end_index'] \
                -= 1
            solution.work_stretches[employee_id][start_index]['length'] \
                -= 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                start_index = -solution.historical_work_stretch[employee_id]
                solution.work_stretches[employee_id][start_index]['end_index'] \
                    -= 1
                solution.work_stretches[employee_id][start_index]['length'] \
                    -= 1
            else:
                try:
                    del solution.work_stretches[
                         employee_id][d_index]
                except KeyError:
                    print("hi")

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
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        employee_parameter = self.parameter_per_employee[employee_id]

        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1) \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index-1)
            # # calc previous violations of the separate work stretches
            # previous_violations = np.maximum(
            #     solution.work_stretches[employee_id][
            #         d_index + 1]['length'] - employee_parameter, 0) \
            #                       + np.maximum(
            #     solution.work_stretches[employee_id][start_index]['length'] - employee_parameter, 0)
            #
            # new_violations = np.maximum((solution.work_stretches[employee_id][
            #                        d_index + 1]['length']
            #                    + solution.work_stretches[employee_id][start_index][
            #                        'length'] + 1) - employee_parameter, 0)
            return self.calc_incremental_violations_merge_stretch(solution.work_stretches[employee_id], rule_parameter=employee_parameter,
                                                           start_index_1=start_index, start_index_2=d_index+1)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                # previous_violations = np.maximum(
                #     solution.work_stretches[employee_id][
                #         d_index + 1]['length'] - employee_parameter,
                #     0)
                # # adapt violations compared to whether there is history before
                # new_violations = np.maximum(solution.work_stretches[employee_id][
                #                                 d_index + 1]['length']
                #                             + solution.historical_work_stretch[
                #                                 employee_id] + 1 - employee_parameter, 0)

                # return new_violations - previous_violations
                return self.calc_incremental_violations_merge_stretch(solution.work_stretches[employee_id], rule_parameter=employee_parameter,
                                                           start_index_1=-solution.historical_work_stretch[
                                                employee_id], start_index_2=d_index+1, history=True)
            else:
                return 1 if solution.work_stretches[employee_id][
                                d_index + 1]['length'] >= employee_parameter \
                    else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index-1)
            # check if the length of the new work stretch is too long
            return 1 if solution.work_stretches[employee_id][start_index]['length'] >= employee_parameter \
                else 0

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                start_index = -solution.historical_work_stretch[employee_id]
                # check if the length of the new work stretch is too long
                return 1 if solution.work_stretches[employee_id][start_index][
                                'length'] >= employee_parameter \
                    else 0
            else:
                return 0

    def incremental_violations_assigned_to_off(self, solution, change_info):
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]

        # find in what work stretch the d_index is
        for start_index, work_stretch in solution.work_stretches[change_info['employee_id']].items():
            if change_info['d_index'] in range(start_index, work_stretch["end_index"]+1):
                split_1 = change_info['d_index'] - start_index
                split_2 = work_stretch['end_index'] - change_info['d_index']

                # calculate new violations based on history
                new_violations_1 = np.maximum(split_1 - employee_parameter, 0)

                return -(np.maximum(work_stretch['length'] - employee_parameter, 0)
                         - new_violations_1
                         - np.maximum(split_2 - employee_parameter, 0))

    def extend_stretch_pre(self, stretch_object_employee, old_start, new_start):
        # create change key of dictionary
        try:
            stretch_object_employee[new_start] = stretch_object_employee[old_start]
        except KeyError:
            a = 1
            print("hi")
        # adjust length
        stretch_object_employee[new_start]['length'] += old_start - new_start

        del stretch_object_employee[old_start]

        return stretch_object_employee

    def shorten_stretch_pre(self, stretch_object_employee, old_start, new_start):
        """
        Function to create key pair for new stretch and remove old stretch
        """
        # change start index of old key
        stretch_object_employee[new_start] \
            = stretch_object_employee[old_start]
        # change the length of the stretch
        stretch_object_employee[new_start]['length'] -= new_start - old_start
        del stretch_object_employee[old_start]

        return stretch_object_employee

    def merge_stretches(self, stretch_object_employee, start_index_1, start_index_2):
        """
        Function to update solution after merge of two stretches
        """
        # replace end_index of new work stretch with last
        stretch_object_employee[
            start_index_1][
            "end_index"] \
            = stretch_object_employee[
            start_index_2][
            'end_index'
        ]
        # compute new length
        stretch_object_employee[
            start_index_1][
            "length"] \
            += stretch_object_employee[
                   start_index_2]['length'] + 1

        # remove unnecessary stretch
        stretch_object_employee.pop(start_index_2)

        return stretch_object_employee

    def split_stretch(self, stretch_object_employee, start_index_1, d_index):
        """
        Function to split stretch in two different stretches
        """
        # add new key value for second new work stretch
        stretch_object_employee[d_index+1] \
            = {
                'end_index': stretch_object_employee[
                    start_index_1]['end_index'],
                'length': stretch_object_employee[
                    start_index_1]['end_index'] - d_index
                }

        # change end index and length of first new work stretch
        stretch_object_employee[start_index_1]['end_index'] \
            = d_index - 1
        stretch_object_employee[start_index_1]['length'] \
            = d_index - start_index_1

        return stretch_object_employee

    def calc_incremental_violations_merge_stretch(self, stretch_object_employee, rule_parameter, start_index_1, start_index_2, history=False):

        # calc previous violations of the separate work stretches
        # if history:
        #     previous_violations = np.maximum(
        #         stretch_object_employee[
        #             start_index_2]['length'] - rule_parameter, 0)
        # else:

        previous_violations = np.maximum(
            stretch_object_employee[
                start_index_2]['length'] - rule_parameter, 0) \
                              + np.maximum(
            stretch_object_employee[start_index_1]['length'] - rule_parameter, 0)

        new_violations = np.maximum((stretch_object_employee[
                                         start_index_2]['length']
                                     + stretch_object_employee[start_index_1][
                                         'length'] + 1) - rule_parameter, 0)
        return new_violations - previous_violations





















