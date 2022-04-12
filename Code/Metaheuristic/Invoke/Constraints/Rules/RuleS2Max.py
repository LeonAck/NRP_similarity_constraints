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

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        delta number_of_violations
        """
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]

        # check if moving from off to assigned
        if not change_info['current_working']:

            work_stretch_before = None
            # find the word stretch of which day d_index - 1 is the last day
            for start_index, work_stretch in solution.work_stretches[
                change_info['employee_id']].items():
                if change_info['d_index'] - 1 == work_stretch["end_index"]:
                    work_stretch_before = work_stretch
                    break

            # check if both adjacent day are in a work stretch
            if change_info['d_index'] + 1 in solution.work_stretches[
                change_info['employee_id']].keys() and work_stretch_before:

                # check if the length of the new work stretch is too long
                if employee_parameter <= solution.work_stretches[change_info['employee_id']][
                    change_info['d_index'] + 1]['length'] \
                        + work_stretch_before['length']:

                    # calc previous violations of the separate work stretches
                    previous_violations = np.maximum(
                        solution.work_stretches[change_info['employee_id']][
                        change_info['d_index']+1]['length'] - employee_parameter,
                         0) \
                          + np.maximum(
                        work_stretch_before['length'] - employee_parameter,
                         0)

                    return (solution.work_stretches[change_info['employee_id']][
                    change_info['d_index'] + 1]['length']
                        + work_stretch_before['length'] + 1) - employee_parameter \
                        - previous_violations

            # check if only the day after is in a work stretch
            elif change_info['d_index'] + 1 in solution.work_stretches[
                change_info['employee_id']].keys():

                # check whether the length of the new work stretch is longer than allowed
                return 1 if solution.work_stretches[change_info['employee_id']][
                       change_info['d_index'] + 1]['length'] >= employee_parameter \
                        else 0

            # check whether only the day before is in a work stretch
            elif work_stretch_before:
                # check if the length of the new work stretch is too long
                return 1 if work_stretch_before['length'] >= employee_parameter \
                            else 0
            # if neither of the adjacent days are in a work stretch
            else:
                return 0

        # check if moving from assigned to off
        elif not change_info['new_working']:
            # find in what work stretch the d_index is
            for start_index, work_stretch in solution.work_stretches[change_info['employee_id']].items():
                if change_info['d_index'] in range(start_index, work_stretch["end_index"]):

                    split_1 = change_info['d_index'] - start_index
                    split_2 = work_stretch['end_index'] - change_info['d_index']

                    return -(np.maximum(work_stretch['length'] - employee_parameter, 0)
                             - np.maximum(split_1 - employee_parameter, 0)
                            - np.maximum(split_2 - employee_parameter, 0))

        else:
            return 0

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update solution information after change from off to assigned
        """
        work_stretch_before = None
        start_index_before = None
        # find the word stretch of which day d_index - 1 is the last day
        for start_index, work_stretch in solution.work_stretches[
            change_info['employee_id']].items():
            if change_info['d_index'] - 1 == work_stretch["end_index"]:
                work_stretch_before = work_stretch
                start_index_before = start_index
                break
        # check if both adjacent day are in a work stretch
        if change_info['d_index'] + 1 in solution.work_stretches[
            change_info['employee_id']].keys() and work_stretch_before:
            # replace end_index of new work stretch with last
            solution.work_stretches[
                change_info['employee_id']][
                start_index_before][
                "end_index"] \
                = solution.work_stretches[
                change_info['employee_id']][
                change_info['d_index'] + 1][
                'end_index'
            ]
            # compute new length
            solution.work_stretches[
                change_info['employee_id']][
                start_index_before][
                "length"] \
            += solution.work_stretches[
                change_info['employee_id']][
                change_info['d_index'] + 1][
                'length'
            ] + 1

            # remove unnecessary stretch
            solution.work_stretches[
                change_info['employee_id']].pop(change_info['d_index'] + 1)

        # check if only the day after is in a work stretch
        elif change_info['d_index'] + 1 in solution.work_stretches[
            change_info['employee_id']].keys():

            # create change key of dictionary
            solution.work_stretches[
                change_info['employee_id']][change_info['d_index']] = solution.work_stretches[
                change_info['employee_id']].pop(change_info['d_index'] + 1)

            # change length
            solution.work_stretches[
                change_info['employee_id']][change_info['d_index']]['length'] += 1

        # check whether only the day before is in a work stretch
        elif work_stretch_before:
            # change end index by one
            solution.work_stretches[
                change_info['employee_id']][start_index_before]['end_index'] += 1

            solution.work_stretches[
                change_info['employee_id']][start_index_before]['length'] += 1

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update solution information after change from assigned to off
        """
        if change_info['d_index'] in solution.work_stretches[
            change_info['employee_id']].keys():
            # change start index of old key
            solution.work_stretches[
            change_info['employee_id']][change_info['d_index']+1] \
                = solution.work_stretches[
            change_info['employee_id']].pop(change_info['d_index'])

            # reduce length of stretch by one
            solution.work_stretches[
                change_info['employee_id']][change_info['d_index'] + 1]['length'] \
            -= 1
        else:
            end = None
            middle = None
            start_index_d = None
            # find whether index is in end or middle of work stretch
            for start_index, work_stretch in solution.work_stretches[
                                            change_info['employee_id']].items():
                if change_info['d_index'] == work_stretch["end_index"]:
                    end = True
                    start_index_d = start_index
                    break
                elif change_info['d_index'] in range(start_index, work_stretch["end_index"]):
                    middle = True
                    start_index_d = start_index
                    break

            # check if removed assignment is at the end of work stretch
            if end:
                solution.work_stretches[change_info['employee_id']][start_index_d]['end_index'] \
                    -= 1
                solution.work_stretches[change_info['employee_id']][start_index_d]['length'] \
                    -= 1

            # removed assignment is in the middle of a work stretch
            # resulting in two new work stretches
            else:
                # add new key value for second new work stretch
                solution.work_stretches[change_info['employee_id']][
                    change_info['d_index'] + 1] \
                    = {
                    'end_index': solution.work_stretches[
                        change_info['employee_id']][
                        start_index_d]['end_index'],
                    'length': solution.work_stretches[
                        change_info['employee_id']][
                        start_index_d]['end_index'] - change_info['d_index']
                }

                # change end index and length of first new work stretch
                solution.work_stretches[change_info['employee_id']][start_index_d]['end_index'] \
                    = change_info['d_index'] - 1
                solution.work_stretches[change_info['employee_id']][start_index_d]['length'] \
                    = change_info['d_index'] - start_index_d

        return solution



















