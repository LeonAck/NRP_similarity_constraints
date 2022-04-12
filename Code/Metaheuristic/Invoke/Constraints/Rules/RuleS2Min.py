from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS2Min(Rule):
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
        return sum([np.maximum(self.parameter_per_employee[employee_id] - work_stretch['length'], 0)
                    for work_stretch in solution.work_stretches[employee_id].values()])

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

                # return difference between new violations and previous violations
                return - (
                        np.maximum(
                            employee_parameter
                            - solution.work_stretches[change_info['employee_id']][
                                change_info['d_index'] + 1]['length'], 0
                        )
                        + np.maximum(
                        employee_parameter
                        - work_stretch_before['length'], 0
                        )
                        - np.maximum(
                        employee_parameter
                        - (solution.work_stretches[change_info['employee_id']][
                           change_info['d_index'] + 1]['length']
                        + work_stretch_before['length'] + 1), 0
                        )
                        )

            # check if only the day after is in a work stretch
            elif change_info['d_index'] + 1 in solution.work_stretches[
                change_info['employee_id']].keys():

                # check whether the length of the new work stretch is longer than allowed
                return -1 if solution.work_stretches[change_info['employee_id']][
                                 change_info['d_index'] + 1]['length'] <= employee_parameter \
                    else 0

            # check whether only the day before is in a work stretch
            elif work_stretch_before:
                # check if the length of the new work stretch is too long
                return -1 if work_stretch_before['length'] <= employee_parameter \
                    else 0
            # if neither of the adjacent days are in a work stretch
            else:
                return 0

        # check if moving from assigned to off
        elif not change_info['new_working']:
            # find in what work stretch the d_index is
            for start_index, work_stretch in solution.work_stretches[change_info['employee_id']].items():
                if change_info['d_index'] in range(start_index, work_stretch["end_index"]):
                    # calc length of remaining stretches
                    length_1 = change_info['d_index'] - start_index
                    length_2 = work_stretch['end_index'] - change_info['d_index']

                    # add extra violations
                    # the new violations - the old violations
                    return np.maximum(employee_parameter - length_1, 0) \
                           + np.maximum(employee_parameter - length_2, 0) \
                           - np.maximum(employee_parameter - work_stretch['length'], 0)

        else:
            return 0
