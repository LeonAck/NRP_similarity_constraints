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

        # check if moving from off to assigned
        if not change_info['current_working']:
            return self.incremental_violation_off_to_assigned(solution, change_info)

        # check if moving from assigned to off
        elif not change_info['new_working']:
            return self.incremental_violation_assigned_to_off(solution, change_info)
        else:
            return 0

    def incremental_violation_off_to_assigned(self, solution, change_info):
        """
        Incremental violations off to assigned
        """
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]
        d_index = change_info['d_index']
        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_day(change_info['employee_id'], d_index + 1) \
                and solution.check_if_working_day(change_info['employee_id'], d_index - 1):
            start_index = self.find_work_stretch_end(solution, change_info['employee_id'], d_index - 1)

            previous_violations = np.maximum(employee_parameter - solution.work_stretches[change_info['employee_id']][d_index+1]['length'], 0) \
                                    + np.maximum(employee_parameter - solution.work_stretches[change_info['employee_id']][start_index]['length'], 0)
            new_violations = np.maximum(employee_parameter
                                         - (solution.work_stretches[change_info['employee_id']][d_index+1]['length']
                                            + solution.work_stretches[change_info['employee_id']][start_index]['length']
                                            + 1), 0)
            return -(previous_violations - new_violations)
        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_day(change_info['employee_id'], d_index + 1):
            return -1 if solution.work_stretches[change_info['employee_id']][d_index+1]['length'] < employee_parameter else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_day(change_info['employee_id'], d_index - 1):
            start_index = self.find_work_stretch_end(solution, change_info['employee_id'], d_index - 1)
            return -1 if solution.work_stretches[change_info['employee_id']][start_index][
                             'length'] < employee_parameter else 0

        # if single day
        else:
            return np.maximum(employee_parameter-1, 0)

    def incremental_violation_assigned_to_off(self, solution, change_info):
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]
        length_1, length_2, the_work_stretch = None, None, None
        # find in what work stretch the d_index is
        for start_index, work_stretch in solution.work_stretches[change_info['employee_id']].items():
            if change_info['d_index'] in range(start_index, work_stretch["end_index"]+1):
                # calc length of remaining stretches
                length_1 = change_info['d_index'] - start_index if change_info['d_index'] - start_index > 0 else employee_parameter
                length_2 = work_stretch['end_index'] - change_info['d_index'] if work_stretch['end_index'] - change_info['d_index']  > 0 else employee_parameter
                the_work_stretch = work_stretch
                break

        # add extra violations
        # the new violations - the old violations
        return np.maximum(employee_parameter - length_1, 0) \
               + np.maximum(employee_parameter - length_2, 0) \
               - np.maximum(employee_parameter - the_work_stretch['length'], 0)

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
            if d_index in range(s_index + 1, work_stretch['end_index']):
                return s_index
