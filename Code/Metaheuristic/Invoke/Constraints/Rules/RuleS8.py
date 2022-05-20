from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS8(Rule):
    """
        Rule that checks the number of working weekends
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, employee_id)
                    for employee_id in scenario.employees._collection.keys()
                    if employee_id in solution.employee_preferences])

    def count_violations_employee(self, solution, employee_id):
        """
        Function to count violations for a given day, shift type and skill
        """
        violations = 0
        for d_index, s_type in solution.employee_preferences[employee_id].items():
            if s_type == -1:
                if solution.check_if_working_day(employee_id, d_index):
                    violations += 1
            else:
                if solution.shift_assignments[employee_id][d_index, 0] == s_type:
                    violations += 1

        return violations

    def incremental_violations_change(self, solution, change_info, scenario=None):
        # check if moving from off to assigned
        if not change_info['current_working']:
            return self.incremental_violations_off_to_assigned(solution, change_info['employee_id'], change_info['d_index'], change_info['new_s_type'])
        # check if moving from assigned to off
        elif not change_info['new_working']:
            return self.incremental_violations_assigned_to_off(solution, change_info['employee_id'], change_info['d_index'], change_info['new_s_type'])
        else:
            return self.incremental_violations_assigned_to_assigned(solution, change_info['employee_id'], change_info['d_index'], change_info['new_s_type'], change_info['curr_s_type'])

    def check_violation(self, solution, employee_id, d_index, s_type):
        if solution.employee_preferences[employee_id][d_index] == -1:
            return 1
        else:
            if solution.employee_preferences[employee_id][d_index] == s_type:
                return 1
            else:
                return 0

    def incremental_violations_off_to_assigned(self, solution, employee_id, d_index, new_s_type):
        if d_index in solution.employee_preferences[employee_id]:
            if solution.employee_preferences[employee_id][d_index] == -1:
                return 1
            else:
                if solution.employee_preferences[employee_id][d_index] == new_s_type:
                    return 1
                else:
                    return 0
        else:
            return 0

    def incremental_violations_assigned_to_off(self, solution, employee_id, d_index, prev_s_type):
        if d_index in solution.employee_preferences[employee_id]:
            if solution.employee_preferences[employee_id][d_index] == -1:
                return -1
            else:
                if solution.employee_preferences[employee_id][d_index] == prev_s_type:
                    return -1
                else:
                    return 0
        else:
            return 0

    def incremental_violations_assigned_to_assigned(self, solution, employee_id, d_index, new_s_type, prev_s_type):
        return self.incremental_violations_off_to_assigned(solution, employee_id, d_index, new_s_type) \
                + self.incremental_violations_assigned_to_off(solution, employee_id, d_index, prev_s_type)

    def incremental_violations_swap(self, solution, swap_info):
        pass
        

