from Domain.RuleCollection import Rule
import numpy as np

class RuleS8RefShift(Rule):
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

        return sum(solution.ref_comparison_shift_level[employee_id] == 0)

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change operator
        :return:
        \delta number_of_violations
        """
        # off to assigned
        if not change_info['current_working']:
            return self.incremental_violation_change_off_to_assigned(solution,
                                                                     change_info)
        # assigned to off
        elif not change_info['new_working']:
            return self.incremental_violation_change_assigned_to_off(solution,
                                                                     change_info)
        # if assigned to assigned
        elif change_info['new_working'] and change_info['current_working']:
            if change_info['new_s_type'] != change_info['curr_s_type']:
                return self.incremental_violation_change_off_to_assigned(solution,
                                                                         change_info) \
                       + self.incremental_violation_change_assigned_to_off(solution,
                                                                           change_info)
            else:
                return 0
        else:
            return 0

    def incremental_violation_change_off_to_assigned(self, solution,
                                                     change_info):
        violation_counter = 0
        # compare with day in the past
  
        # if one day working, then both days will be working after the change
        if solution.check_if_working_day_ref(change_info['employee_id'],
                                         change_info['d_index']):
            # compare new shift type with ref day
            if change_info['new_s_type'] != \
                    solution.ref_assignments[change_info['employee_id']][
                        change_info['d_index']][0]:
                violation_counter += 1

        return violation_counter

    def incremental_violation_change_assigned_to_off(self, solution,
                                                     change_info):

        violation_counter = 0
    
        # if this day working, both days were working days
        if solution.check_if_working_day_ref(change_info['employee_id'],
                                         change_info['d_index']):
            # compare old shift type with ref day
            if solution.ref_comparison_shift_level[change_info['employee_id']][
                    change_info['d_index']] == 0:
                violation_counter -= 1

        return violation_counter

    def update_information_off_to_assigned(self, solution, change_info):


        # compare with day in the past
        # if one day working, then both days will be working after the change
        if solution.check_if_working_day_ref(change_info['employee_id'],
                                         change_info['d_index']):
            # compare new shift type with ref day
            if change_info['new_s_type'] != \
                    solution.ref_assignments[change_info['employee_id']][
                        change_info['d_index']][0]:
                solution.ref_comparison_shift_level[change_info['employee_id']][change_info['d_index']] = 0
            else:
                solution.ref_comparison_shift_level[change_info['employee_id']][change_info['d_index']] = 1
        else:
            solution.ref_comparison_shift_level[change_info['employee_id']][change_info['d_index']] = -1
        return solution

    def update_information_assigned_to_off(self, solution, change_info):

        # if this day working, both days were working days
        if solution.check_if_working_day_ref(change_info['employee_id'],
                                         change_info['d_index']):

            solution.ref_comparison_shift_level[change_info['employee_id']][
                change_info['d_index']] = -1

        return solution

    def update_information_assigned_to_assigned(self, solution, change_info):

        if change_info['new_s_type'] != change_info['curr_s_type']:
            solution = self.update_information_assigned_to_off(solution, change_info)
            solution = self.update_information_off_to_assigned(solution, change_info)
        return solution

    def incremental_violations_swap(self, solution, swap_info, rule_id):

        return np.count_nonzero(solution.ref_comparison_shift_level[swap_info['employee_id_1']][
                      swap_info['start_index']:swap_info['end_index'] + 1]) - np.count_nonzero(
            swap_info['ref_comparison_shift_level_1']) \
               + np.count_nonzero(solution.ref_comparison_shift_level[swap_info['employee_id_2']][
                        swap_info['start_index']:swap_info['end_index'] + 1]) - np.count_nonzero(
            swap_info['ref_comparison_shift_level_2'])

    def check_comparison_swap(self, solution, swap_info,
                              comparison_object_name):
        """
        Function to calculate new day comparison object
        and calculate the incremental violations
        """
        for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
            other_employee = swap_info['employee_id_{}'.format(2-i)]
            new_comparison_array_swap = np.array([self.update_comparison_array_per_day(solution, employee_id, other_employee,
                                                                              d_index) for d_index in range(swap_info['start_index'], swap_info['end_index'] + 1)])
            swap_info['{}_{}'.format(comparison_object_name, i+1)] = new_comparison_array_swap

        return swap_info
    
    def update_comparison_array_per_day(self, solution, employee_id, other_employee_id, d_index):
        if solution.check_if_working_day_ref(employee_id, d_index):
            if solution.shift_assignments[other_employee_id][d_index][0] == solution.ref_assignments[employee_id][d_index][0]:
                return 1
            elif solution.shift_assignments[other_employee_id][d_index][0] == -1:
                return -1
            else:
                return 0
        else:
            return -1

    # def compare_assignment_swap(self, solution, swap_info, compare_function):
    #
    #     return np.array([compare_function(solution, swap_info['employee_id_1'], swap_info['employee_id_2'], d_index)
    #                      for d_index in range(swap_info['start_index'], swap_info['end_index'] + 1)])
    #
    # def compare_function(self, solution, employee_id_1, employee_id_2, d_index):
    #     if solution.check_if_working_day(employee_id_1, d_index) == solution.check_if_working_day(
    #             employee_id_2, d_index):
    #         if self.compare_shift_type(solution, employee_id_1, employee_id_2, d_index):
    #             return 1
    #         else:
    #             return 0
    #     else:
    #         return -1

    def update_information_swap(self, solution, swap_info):

        solution.ref_comparison_shift_level[swap_info['employee_id_1']][
        swap_info['start_index']:swap_info['end_index'] + 1] = swap_info['ref_comparison_shift_level_1']

        solution.ref_comparison_shift_level[swap_info['employee_id_2']][
        swap_info['start_index']:swap_info['end_index'] + 1] = swap_info['ref_comparison_shift_level_2']

        return solution.ref_comparison_shift_level

    # def compare_shift_type(self, solution, employee_id_1, employee_id_2, d_index):
    #     return solution.shift_assignments[employee_id_1][d_index][0] == solution.shift_assignments[employee_id_2][d_index][0]

