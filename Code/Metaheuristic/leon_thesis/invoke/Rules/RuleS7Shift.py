from invoke.Domain.RuleCollection import Rule


class RuleS7Shift(Rule):
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

        return sum(solution.shift_comparison[employee_id] == 0)

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change operator
        :return:
        \delta number_of_violations
        """
        parameter_1 = solution.rule_collection.collection["S7Shift"].parameter_1
        # off to assigned
        if not change_info['current_working']:
            return self.incremental_violation_change_off_to_assigned(solution,
                                                                     change_info, parameter_1)
        # assigned to off
        elif not change_info['new_working']:
            return self.incremental_violation_change_assigned_to_off(solution,
                                                                     change_info, parameter_1)
        # if assigned to assigned
        elif change_info['new_working'] and change_info['current_working']:
            if change_info['new_s_type'] != change_info['curr_s_type']:
                return self.incremental_violation_change_off_to_assigned(solution,
                                                                         change_info, parameter_1) \
                       + self.incremental_violation_change_assigned_to_off(solution,
                                                                           change_info, parameter_1)
            else:
                return 0
        else:
            return 0

    def incremental_violation_change_off_to_assigned(self, solution,
                                                     change_info, parameter_1):
        violation_counter = 0
        # compare with day in the past
        if change_info['d_index'] - parameter_1 >= 0:
            # if one day working, then both days will be working after the change
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] - parameter_1):
                # compare new shift type with ref day
                if change_info['new_s_type'] != \
                        solution.shift_assignments[change_info['employee_id']][
                            change_info['d_index'] - parameter_1][0]:
                    violation_counter += 1

        # compare with future day
        # if one day working, then both days will be working after the change
        if self.check_future_day_in_horizon(solution.day_collection, change_info['d_index'], parameter_1):
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] + parameter_1):
                # compare new shift type with ref day
                if change_info['new_s_type'] != solution.shift_assignments[
                    change_info['employee_id']][
                        change_info['d_index'] + parameter_1][0]:
                    violation_counter += 1

        return violation_counter

    def incremental_violation_change_assigned_to_off(self, solution,
                                                     change_info, parameter_1):

        violation_counter = 0
        if change_info['d_index'] - parameter_1 >= 0:
            # if this day working, both days were working days
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] - parameter_1):
                # compare old shift type with ref day
                if solution.shift_comparison[change_info['employee_id']][
                        change_info['d_index']] == 0:
                    violation_counter -= 1

        # compare with future day
        # if one day working, then both days will be working after the change
        if self.check_future_day_in_horizon(solution.day_collection, change_info['d_index'], parameter_1):
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] + parameter_1):
                # compare old shift type with ref day
                if solution.shift_comparison[change_info['employee_id']][
                        change_info['d_index'] + parameter_1] == 0:
                    violation_counter -= 1

        return violation_counter

    def update_information_off_to_assigned(self, solution, change_info):
        parameter_1 = solution.rule_collection.collection["S7Shift"].parameter_1

        if change_info['d_index'] - parameter_1 >= 0:
            # compare with day in the past
            # if one day working, then both days will be working after the change
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] - parameter_1):
                # compare new shift type with ref day
                if change_info['new_s_type'] != \
                        solution.shift_assignments[change_info['employee_id']][
                            change_info['d_index'] - parameter_1][0]:
                    solution.shift_comparison[change_info['employee_id']][change_info['d_index']] = 0
                else:
                    solution.shift_comparison[change_info['employee_id']][change_info['d_index']] = 1

        # compare with future day
        # if one day working, then both days will be working after the change
        if self.check_future_day_in_horizon(solution.day_collection, change_info['d_index'], parameter_1):
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] + parameter_1):
                # compare new shift type with ref day
                if change_info['new_s_type'] != solution.shift_assignments[
                    change_info['employee_id']][
                        change_info['d_index'] + parameter_1][0]:
                    solution.shift_comparison[change_info['employee_id']][
                        change_info['d_index'] + parameter_1] = 0
                else:
                    solution.shift_comparison[change_info['employee_id']][
                        change_info['d_index'] + parameter_1] = 1

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        parameter_1 = solution.rule_collection.collection["S7Shift"].parameter_1

        if change_info['d_index'] - parameter_1 >= 0:
            # if this day working, both days were working days
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] - parameter_1):

                solution.shift_comparison[change_info['employee_id']][
                    change_info['d_index']] = -1

        # compare with future day
        # if one day working, then both days will be working after the change
        if self.check_future_day_in_horizon(solution.day_collection, change_info['d_index'], parameter_1):
            if solution.check_if_working_day(change_info['employee_id'],
                                             change_info['d_index'] + parameter_1):
                # compare old shift type with ref day
                solution.shift_comparison[change_info['employee_id']][
                    change_info['d_index'] + parameter_1] = -1

        return solution

    def update_information_assigned_to_assigned(self, solution, change_info):

        if change_info['new_s_type'] != change_info['curr_s_type']:
            solution = self.update_information_assigned_to_off(solution, change_info)
            solution = self.update_information_off_to_assigned(solution, change_info)
        return solution


    def check_ref_day_in_horizon(self, d_index):
        """
        Function to check whether the d_index - parameter_1 is in the horizon
        """
        return (d_index - self.parameter_1) >= 0

    def check_future_day_in_horizon(self, day_collection, d_index, parameter_1):
        return (d_index + parameter_1) <= day_collection.num_days_in_horizon - 1
