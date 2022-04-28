from Invoke.Constraints.initialize_rules import Rule
import numpy as np


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

    def print_violations_per_employee(self, solution, scenario):
        for employee_id in scenario.employees._collection.keys():
            print(employee_id, sum([self.violations_per_employee_day_soft(solution, scenario, employee_id, d_index)
                    for d_index in range(0, scenario.day_collection.num_days_in_horizon-1)]))

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
            if not self.violations_per_employee_day_mandatory(solution, scenario, employee, d_index):
                flag = False
                # break

        return flag

    def violations_per_employee_day_mandatory(self, solution, scenario, employee, d_index):
        """
        Check violations per nurse per day
        """
        # get number of violations
        flag = True
        # check if working
        if solution.check_if_working_day(employee.id, d_index):
            # compare to day before
            # check if not the first and working the day before
            if d_index > 0 and solution.check_if_working_day(employee.id, d_index - 1):

                # if solution.shift_assignments[employee.id][d_index]['s_type'] \
                #         in scenario.forbidden_shift_type_successions[solution.shift_assignments[employee.id][d_index-1]['s_type']-1][1]:
                if solution.shift_assignments[employee.id][d_index][0] - 1 \
                        in scenario.forbidden_shift_type_successions[
                    solution.shift_assignments[employee.id][d_index - 1][0] - 1][1]:
                    flag = False

            # check if not the last day, no violation before and working the day after day d_index
            if d_index < scenario.num_days_in_horizon - 1 and flag and solution.check_if_working_day(employee.id,
                                                                                                     d_index + 1):
                # if solution.shift_assignments[employee.id][d_index]['s_type'] \
                #     in scenario.forbidden_shift_type_successions[
                #         int(solution.shift_assignments[employee.id][d_index + 1]['s_type'] - 1)][1]:
                if solution.shift_assignments[employee.id][d_index + 1][0] - 1 \
                        in scenario.forbidden_shift_type_successions[
                    solution.shift_assignments[employee.id][d_index][0] - 1][1]:
                    flag = False

        return flag

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

        # if d_index < scenario.num_days_in_horizon - 1 and \
        #         solution.shift_assignments[employee_id][d_index][0] != -1:
        #     if solution.shift_assignments[employee_id][d_index+1][0] \
        #             in scenario.forbidden_shift_type_successions[
        #             solution.shift_assignments[employee_id][d_index][0]][1]:
        #         number_of_violations += 1

        return number_of_violations

    def get_allowed_shift_types(self, solution, scenario, employee_id, d_index):
        """
        For a given day get the shift types that are not allowed given
        the assignment the day before and the day after
        """
        allowed_shift_types = scenario.shift_collection.shift_types_indices

        if d_index > 0:
            # check if working the day before
            if solution.check_if_working_day(employee_id, d_index - 1):
                # get shift type of the day before
                shift_type_day_before = solution.shift_assignments[employee_id][d_index - 1][0]

                for s_type in scenario.forbidden_shift_type_successions[shift_type_day_before][1]:
                    # delete forbidden shifts
                    allowed_shift_types = np.delete(allowed_shift_types, np.in1d(allowed_shift_types, s_type))

        # check if there is a day after
        if d_index < scenario.num_days_in_horizon - 1:
            # check if working the day after
            if solution.check_if_working_day(employee_id, d_index + 1):
                # get shift type of day after
                shift_type_day_after = solution.shift_assignments[employee_id][d_index + 1][0]

                for succession in scenario.forbidden_shift_type_successions:
                    if shift_type_day_after in succession[1]:
                        # delete forbidden shifts
                        allowed_shift_types = np.delete(allowed_shift_types,
                                                        np.in1d(allowed_shift_types, succession[0]))

        return allowed_shift_types

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

        if change_info['d_index'] < solution.day_collection.num_days_in_horizon - 1:
            if solution.shift_assignments[
                change_info['employee_id']][change_info['d_index']+1][0] \
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
            if change_info['curr_s_type']\
                    in solution.forbidden_shift_type_successions[
                        solution.shift_assignments[
                            change_info['employee_id']][
                            change_info['d_index'] - 1][0]][
                        1]:
                violation_counter -= 1

        if change_info['d_index'] < solution.day_collection.num_days_in_horizon - 1:
            if solution.shift_assignments[
                    change_info['employee_id']][change_info['d_index']+1][0] \
                    in solution.forbidden_shift_type_successions[
                            change_info['curr_s_type']][1]:
                violation_counter -= 1

        return violation_counter
