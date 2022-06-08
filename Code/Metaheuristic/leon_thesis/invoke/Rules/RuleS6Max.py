from invoke.Domain.RuleCollection import Rule
import numpy as np


class RuleS6Max(Rule):
    """
        Rule that compares the max number of assignments of an employee to the
        to the actual assignments
        Parameter1: max. number of assignments in the scheduling period
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
        Function to count violations for a given day, shift type and skill
        """
        return solution.num_assignments_per_nurse[employee_id] - self.parameter_per_employee[employee_id] if \
            solution.num_assignments_per_nurse[employee_id] > self.parameter_per_employee[employee_id] else 0

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        \delta number_of_violations
        """
        if not change_info['current_working'] and\
                solution.num_assignments_per_nurse[change_info['employee_id']] \
                >= self.parameter_per_employee[change_info['employee_id']]:
            return 1
        elif not change_info['new_working'] and\
                solution.num_assignments_per_nurse[change_info['employee_id']]\
                > self.parameter_per_employee[change_info['employee_id']]:
            return -1
        else:
            return 0

    def incremental_violations_swap(self, solution, swap_info, rule_id=None):
        # check the number of assignments per stretch
        assignments_stretch_1 = self.count_assignments_in_stretch(solution,
                                                                  swap_info['employee_id_1'],
                                                                  swap_info['start_index'],
                                                                  swap_info['end_index'])

        assignments_stretch_2 = self.count_assignments_in_stretch(solution,
                                                                  swap_info['employee_id_2'],
                                                                  swap_info['start_index'],
                                                                  swap_info['end_index'])

        # check if number if the same
        if assignments_stretch_1 == assignments_stretch_2:
            return 0
        else:
            return self.incremental_violation_swap_per_employee(solution,
                                                                swap_info['employee_id_1'],
                                                                assignments_in_old_stretch=assignments_stretch_1,
                                                                assignments_in_new_stretch=assignments_stretch_2) \
                + self.incremental_violation_swap_per_employee(solution,
                                                                swap_info['employee_id_2'],
                                                                assignments_in_old_stretch=assignments_stretch_2,
                                                                assignments_in_new_stretch=assignments_stretch_1)

    def count_assignments_in_stretch(self, solution, employee_id, start_index, end_index):
        """
        Function to count number of assignments in a set of days
        """
        return sum([assignment[0] != -1 for assignment in
             solution.shift_assignments[employee_id][start_index:end_index+1, ]])

    def incremental_violation_swap_per_employee(self, solution, employee_id,
                                                assignments_in_old_stretch,
                                                assignments_in_new_stretch):
        incremental_assignments = assignments_in_new_stretch - assignments_in_old_stretch

        new_violations = np.maximum(incremental_assignments
                         + solution.num_assignments_per_nurse[employee_id]
                         - self.parameter_per_employee[employee_id], 0)
        old_violations = np.maximum(
            solution.num_assignments_per_nurse[employee_id]
            -self.parameter_per_employee[employee_id], 0)

        return new_violations - old_violations

    def update_information_swap(self, solution, swap_info):
        assignments_stretch_1 = self.count_assignments_in_stretch(solution,
                                                                  swap_info['employee_id_1'],
                                                                  swap_info['start_index'],
                                                                  swap_info['end_index'])

        assignments_stretch_2 = self.count_assignments_in_stretch(solution,
                                                                  swap_info['employee_id_2'],
                                                                  swap_info['start_index'],
                                                                  swap_info['end_index'])

        # update the change of number of assignments due to swap
        if assignments_stretch_1 != assignments_stretch_2:
            solution.num_assignments_per_nurse[swap_info['employee_id_1']] += assignments_stretch_2 - assignments_stretch_1
            solution.num_assignments_per_nurse[swap_info['employee_id_2']] += assignments_stretch_1 - assignments_stretch_2

        return solution

