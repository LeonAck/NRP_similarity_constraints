from invoke.Domain.RuleCollection import Rule
from invoke.general_functions import check_if_working_day


class RuleH3(Rule):
    """
    Rule that checks for forbidden shift types according to the scenario
    """

    # TODO incorporate history
    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
               Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, scenario, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, scenario, employee_id):
        return sum([self.violations_per_employee_day_soft(solution, scenario, employee_id, d_index)
                    for d_index in range(0, scenario.day_collection.num_days_in_horizon)])

    def violations_per_employee_day_soft(self, solution, scenario, employee_id, d_index):
        """
        Check violations per nurse per day
        """
        # get number of violations
        number_of_violations = 0
        # compare with day before
        if d_index > 0 and solution.shift_assignments[employee_id][d_index - 1][0] != -1:
            if solution.shift_assignments[employee_id][d_index][0] \
                    in \
                    scenario.forbidden_shift_type_successions[
                        solution.shift_assignments[employee_id][d_index - 1][0]][
                        1]:
                number_of_violations += 1

        # count violations through history
        elif d_index == 0 and solution.last_assigned_shift[employee_id] != -1:
            if solution.shift_assignments[employee_id][d_index][0] \
                    in \
                    scenario.forbidden_shift_type_successions[
                        solution.last_assigned_shift[employee_id]][
                        1]:
                number_of_violations += 1

        return number_of_violations

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

    def incremental_violation_change_off_to_assigned(self, solution, change_info):
        violation_counter = 0

        if change_info['d_index'] > 0 and solution.shift_assignments[
            change_info['employee_id']][
            change_info['d_index'] - 1][0] != -1:
            if change_info['new_s_type'] \
                    in \
                    solution.forbidden_shift_type_successions[
                        solution.shift_assignments[
                            change_info['employee_id']][
                            change_info['d_index'] - 1][0]][
                        1]:
                violation_counter += 1
        elif change_info['d_index'] == 0 and solution.last_assigned_shift[change_info['employee_id']] != -1:
            if change_info['new_s_type'] \
                    in \
                    solution.forbidden_shift_type_successions[
                        solution.last_assigned_shift[change_info['employee_id']]][
                        1]:
                violation_counter += 1

        if change_info['d_index'] < solution.day_collection.num_days_in_horizon - 1:
            if solution.shift_assignments[
                change_info['employee_id']][change_info['d_index'] + 1][0] \
                    in solution.forbidden_shift_type_successions[
                change_info['new_s_type']][1]:
                violation_counter += 1

        return violation_counter

    def incremental_violation_change_assigned_to_off(self, solution, change_info):
        violation_counter = 0

        if change_info['d_index'] > 0 and \
                solution.shift_assignments[
                    change_info['employee_id']][
                    change_info['d_index'] - 1][0] != -1:
            if change_info['curr_s_type'] \
                    in solution.forbidden_shift_type_successions[
                solution.shift_assignments[
                    change_info['employee_id']][
                    change_info['d_index'] - 1][0]][
                1]:
                violation_counter -= 1

        elif change_info['d_index'] == 0 and solution.last_assigned_shift[change_info['employee_id']] != -1:
            if change_info['curr_s_type'] \
                    in \
                    solution.forbidden_shift_type_successions[
                        solution.last_assigned_shift[change_info['employee_id']]][
                        1]:
                violation_counter -= 1

        if change_info['d_index'] < solution.day_collection.num_days_in_horizon - 1:
            if solution.shift_assignments[
                change_info['employee_id']][change_info['d_index'] + 1][0] \
                    in solution.forbidden_shift_type_successions[
                change_info['curr_s_type']][1]:
                violation_counter -= 1

        return violation_counter

    def print_violations_per_employee(self, solution, scenario):
        for employee_id in scenario.employees._collection.keys():
            print(employee_id, sum([self.violations_per_employee_day_soft(solution, scenario, employee_id, d_index)
                                    for d_index in range(0, scenario.day_collection.num_days_in_horizon - 1)]))

    def check_violations_mandatory(self, solution, scenario, employees):
        """
        Check violations for entire solution
        """
        flag = True
        for employee in employees._collection.values():
            # check all employees until violation is found
            if not self.violations_per_employee(solution, scenario, employee):
                flag = False
                break
        # if any violation will return flag is false
        return flag

    def violations_per_employee(self, solution, scenario, employee):
        """
        Check violations per nurse
        """
        # get number of violations
        flag = True
        for d_index, assignments in enumerate(solution.shift_assignments[employee.id]):
            if not self.violations_per_employee_day_mandatory(solution.shift_assignments, scenario, employee, d_index):
                flag = False
                # break

        return flag

    def violations_per_employee_day_mandatory(self, shift_assignments, scenario, employee, d_index):
        """
        Check violations per nurse per day
        """
        # get number of violations
        flag = True
        # check if working
        if check_if_working_day(shift_assignments, employee.id, d_index):
            # compare to day before
            # check if not the first and working the day before
            if d_index > 0 and check_if_working_day(shift_assignments, employee.id, d_index - 1):

                # if solution.shift_assignments[employee.id][d_index]['s_type'] \
                #         in scenario.forbidden_shift_type_successions[solution.shift_assignments[employee.id][d_index-1]['s_type']-1][1]:
                if shift_assignments[employee.id][d_index][0] - 1 \
                        in scenario.forbidden_shift_type_successions[
                    shift_assignments[employee.id][d_index - 1][0] - 1][1]:
                    flag = False

            # check if not the last day, no violation before and working the day after day d_index
            if d_index < scenario.num_days_in_horizon - 1 and flag and check_if_working_day(shift_assignments, employee.id,
                                                                                                     d_index + 1):
                if shift_assignments[employee.id][d_index + 1][0] - 1 \
                        in scenario.forbidden_shift_type_successions[
                    shift_assignments[employee.id][d_index][0] - 1][1]:
                    flag = False

        return flag

    # def check_one_way_swap_start_day(self, solution, employee_id_1, employee_id_2, d_index):
    #     # collect whether start index is infeasible
    #     return self.check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
    #                                            employee_id_1,
    #                                            employee_id_2,
    #                                            d_index)
    #
    # def check_one_way_swap_end_day(self, solution, k, employee_id_1, employee_id_2, d_index):
    #     return self.check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
    #                                            employee_id_2,
    #                                            employee_id_1,
    #                                            d_index + k)

    def check_removed_violations_swap(self, solution, k, employee_id_1, d_index):
        removed_violations = 0
        start_check = check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
                                                 employee_id_1,
                                                 employee_id_1,
                                                 d_index)
        end_check = check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
                                               employee_id_1,
                                               employee_id_1,
                                               d_index + k)
        if start_check:
            removed_violations += 1
        if end_check:
            removed_violations += 1
        return removed_violations

    def incremental_violations_swap(self, solution, swap_info, rule_id=None):
        incremental_violations = 0
        for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
            other_employee_id = swap_info['employee_id_{}'.format(2 - i)]
            if check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
                                          employee_id,
                                          other_employee_id, swap_info['start_index']):
                incremental_violations += 1
            if check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
                                          other_employee_id,
                                          employee_id,
                                          swap_info['start_index'] + swap_info['k_swap']):
                incremental_violations += 1

            incremental_violations -= self.check_removed_violations_swap(solution, swap_info['k_swap'], employee_id,
                                                                         swap_info['start_index'])
        return incremental_violations


def check_forbidden_given_shifts(forbidden_successions, s_index_1, s_index_2):
    """
    For two shift types, check whether they can follow each other
    """

    return s_index_2 in forbidden_successions[s_index_1][1]


def check_forbidden_before_day(solution, forbidden_successions, employee_id_1, employee_id_2,
                               d_index):
    if d_index == 0:
        # TODO functie vervangen
        return check_forbidden_given_shifts(forbidden_successions,
                                            solution.last_assigned_shift[employee_id_1],
                                            solution.shift_assignments[employee_id_2][d_index][0],
                                            ) \
            if solution.last_assigned_shift[employee_id_1] != -1 \
               and solution.shift_assignments[employee_id_2][d_index][0] != -1 \
            else False
    if d_index > 0:
            return check_forbidden_given_shifts(forbidden_successions,
                                                solution.shift_assignments[employee_id_1][d_index - 1][0],
                                                solution.shift_assignments[employee_id_2][d_index][0],
                                                ) \
                if solution.shift_assignments[employee_id_1][d_index - 1][0] != -1 \
                   and solution.shift_assignments[employee_id_2][d_index][0] != -1 \
                else False

