from Domain.RuleCollection import Rule
import numpy as np
class RuleS8RefDay(Rule):
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
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, employee_id):
        """
        Function to count violations for a given employee
        """
        return sum(solution.ref_comparison_day_level[employee_id] == 0)

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change operator
        :return:
        \delta number_of_violations
        """
        violation_counter = 0
        if not change_info['current_working'] or not change_info['new_working']:
            if solution.ref_comparison_day_level[change_info['employee_id']][change_info['d_index']] == 1:
                violation_counter += 1
            elif solution.ref_comparison_day_level[change_info['employee_id']][change_info['d_index']] == 0:
                violation_counter -= 1

        return violation_counter

    def update_information_off_to_assigned(self, solution, change_info):

        # compare to ref day
        if solution.ref_comparison_day_level[change_info['employee_id']][change_info['d_index']] == 1:
            solution.ref_comparison_day_level[change_info['employee_id']][change_info['d_index']] = 0
        elif solution.ref_comparison_day_level[change_info['employee_id']][change_info['d_index']] == 0:
            solution.ref_comparison_day_level[change_info['employee_id']][change_info['d_index']] = 1

        return solution

    def incremental_violations_swap(self, solution, swap_info, rule_id):

        return np.sum(solution.ref_comparison_day_level[swap_info['employee_id_1']][
                      swap_info['start_index']:swap_info['end_index'] + 1]) - np.sum(swap_info['ref_comparison_day_level_1']) \
               + np.sum(solution.ref_comparison_day_level[swap_info['employee_id_2']][
                        swap_info['start_index']:swap_info['end_index'] + 1]) - np.sum(
            swap_info['ref_comparison_day_level_2'])

    def check_comparison_swap(self, solution, swap_info, compare_function, comparison_object,
                              comparison_object_name):
        """
        Function to calculate new day comparison object
        and calculate the incremental violations
        """
        comparison_array = self.compare_assignment_swap(solution, swap_info, compare_function)

        swap_info['{}_1'.format(comparison_object_name)] = np.ones(swap_info['k_swap']) - np.abs(
            comparison_object[swap_info['employee_id_1']][
            swap_info['start_index']:swap_info['end_index'] + 1] - comparison_array)
        swap_info['{}_2'.format(comparison_object_name)] = np.ones(swap_info['k_swap']) - np.abs(
            comparison_object[swap_info['employee_id_2']][
            swap_info['start_index']:swap_info['end_index'] + 1] - comparison_array)

        return swap_info

    def compare_assignment_swap(self, solution, swap_info, compare_function):

        return np.array([compare_function(solution, swap_info['employee_id_1'], swap_info['employee_id_2'], d_index)
                         for d_index in range(swap_info['start_index'], swap_info['end_index'] + 1)])

    def compare_function(self, solution, employee_id_1, employee_id_2, d_index):

        return 1 if solution.check_if_working_day(employee_id_1, d_index) == solution.check_if_working_day(
            employee_id_2, d_index) else 0

    def update_information_swap(self, solution, swap_info):

        solution.ref_comparison_day_level[swap_info['employee_id_1']][
        swap_info['start_index']:swap_info['end_index'] + 1] = swap_info['ref_comparison_day_level_1']

        solution.ref_comparison_day_level[swap_info['employee_id_2']][
        swap_info['start_index']:swap_info['end_index'] + 1] = swap_info['ref_comparison_day_level_2']

        return solution.ref_comparison_day_level



