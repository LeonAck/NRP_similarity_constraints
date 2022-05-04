from Invoke.Constraints.initialize_rules import Rule
import numpy as np

class RuleS3Min(Rule):
    """
        Rule that checks whether less days off than minimum per employee
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
        return sum([np.maximum(self.parameter_per_employee[employee_id] - day_off_stretch['length'], 0)
                    for day_off_stretch in solution.day_off_stretches[employee_id].values()
                    if day_off_stretch['end_index'] > -1])

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
        length_1, length_2, the_day_off_stretch = None, None, None
        # find in what work stretch the d_index is
        for start_index, day_off_stretch in solution.day_off_stretches[change_info['employee_id']].items():
            if change_info['d_index'] in range(start_index, day_off_stretch["end_index"]+1):
                # calc length of remaining stretches
                # calc length of remaining stretches
                length_1 = change_info['d_index'] - start_index if change_info[
                                                                       'd_index'] - start_index > 0 else employee_parameter
                length_2 = day_off_stretch['end_index'] - change_info['d_index'] if day_off_stretch['end_index'] - \
                                                                                 change_info[
                                                                                     'd_index'] > 0 else employee_parameter
                the_day_off_stretch = day_off_stretch
                break

            # add extra violations
        new_violations_1 = np.maximum(employee_parameter - length_1, 0) if change_info['d_index'] != 0 else 0
        # the new violations - the old violations

        return new_violations_1 \
               + np.maximum(employee_parameter - length_2, 0) \
               - np.maximum(employee_parameter - the_day_off_stretch['length'], 0)

    def incremental_violation_assigned_to_off(self, solution, change_info):
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        if solution.check_if_middle_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1) \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id, d_index - 1)

            previous_violations = np.maximum(
                employee_parameter - solution.day_off_stretches[employee_id][d_index + 1]['length'], 0) \
                                  + np.maximum(
                employee_parameter - solution.day_off_stretches[employee_id][start_index]['length'], 0)
            new_violations = np.maximum(employee_parameter
                                        - (solution.day_off_stretches[employee_id][d_index + 1]['length']
                                           + solution.day_off_stretches[employee_id][start_index][
                                               'length']
                                           + 1), 0)
            return -(previous_violations - new_violations)
        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and not solution.check_if_working_day(employee_id, d_index + 1):
            return -1 if solution.day_off_stretches[employee_id][d_index + 1][
                             'length'] < employee_parameter else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and not solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_day_off_stretch_end(solution, employee_id, d_index - 1)
            return -1 if solution.day_off_stretches[employee_id][start_index][
                             'length'] < employee_parameter else 0

        # if single day
        else:
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                return np.maximum(employee_parameter - solution.historical_work_stretch[employee_id] - 1, 0)
            else:
                return np.maximum(employee_parameter - 1, 0)


    def find_day_off_stretch_end(self, solution, employee_id, d_index):
        """
        Find key of day off stretch given that d_index is the last day
        """
        for s_index, day_off_stretch in solution.day_off_stretches[employee_id].items():
            if day_off_stretch['end_index'] == d_index:
                return s_index

    def find_day_off_stretch_middle(self, solution, employee_id, d_index):
        """
       Find key of day off stretch given that d_index is the last day
       """
        for s_index, day_off_stretch in solution.day_off_stretches[employee_id].items():
            if d_index in range(s_index + 1, day_off_stretch['end_index']):
                return s_index
