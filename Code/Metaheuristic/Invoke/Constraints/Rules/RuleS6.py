from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS6(Rule):
    """
        Rule that checks the number of working weekends
    """

    def __init__(self, rule_spec=None):
        super().__init__(rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, scenario.day_collection, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, day_collection, employee_id):
        """
        Function to count violations for a given day, shift type and skill
        """
        working_weekends = 0
        for weekend in day_collection.weekends.values():
            if solution.shift_assignments[employee_id][weekend[0]][0] >= 0 or \
                solution.shift_assignments[employee_id][weekend[1]][0] >= 0:
                    working_weekends += 1

        return working_weekends > self.parameter_1 if \
            working_weekends > self.parameter_1 else 0

    def incremental_violations_change(self, solution, change_info):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        \delta number_of_violations
        """
        if not change_info['current_working'] and\
                solution.num_assignments_per_nurse[change_info['employee_id']] \
                >= self.parameter_1:
            return 1
        elif not change_info['new_working'] and\
                solution.num_assignments_per_nurse[change_info['employee_id']]\
                > self.parameter_1:
            return -1
        else:
            return 0
