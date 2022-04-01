from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS4(Rule):
    """
        Rule that checks whether a nurse works complete weekends
    """

    def __init__(self, rule_spec=None):
        super().__init__(rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, employee_id):
        """
        Function to count violations for a given day, shift type and skill
        """
        return solution.num_assignments_per_nurse[employee_id] > self.parameter_1

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