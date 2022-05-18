from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS6(Rule):
    """
        Rule that checks the number of working weekends
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        num_working_weekends = self.count_working_weekends_employee(solution, scenario)
        return sum([self.count_violations_employee(num_working_weekends, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, num_working_weekends, employee_id):
        """
        Function to count violations for a given day, shift type and skill
        """
        return num_working_weekends[employee_id] - self.parameter_per_employee[employee_id] if \
            num_working_weekends[employee_id] > self.parameter_per_employee[employee_id] else 0

    def count_working_weekends_employee(self, solution, scenario):
        """
        Function to create dictionary with the number of employees per weekend
        """
        num_working_weekends = {}

        for employee_id in scenario.employees._collection.keys():
            working_weekends = 0
            for weekend in scenario.day_collection.weekends.values():
                # a weekend is a working weekend if one of the two days is assigned
                if solution.check_if_working_day(employee_id, weekend[0]) or \
                        solution.check_if_working_day(employee_id, weekend[1]):
                    working_weekends += 1
            # save num working weekends with key employee id
            num_working_weekends[employee_id] = working_weekends

        return num_working_weekends

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change operator
        :return:
        \delta number_of_violations
        """

        if change_info['d_index'] in scenario.day_collection.list_weekend_days:
            # we have an additional total working weekend violation the following all hold:
            # a) we go from an off day to a working day
            # b) the other day in the weekend is not a working day --> extra working weekend
            # c) the number of working weekends is at or above the maximum
            if not change_info['current_working'] \
                    and not solution.check_if_working_day(employee_id=change_info['employee_id'],
                                                          d_index=change_info[
                                                                      'd_index'] + scenario.day_collection.get_index_other_weekend_day(
                                                              scenario.day_collection.weekend_day_indices[
                                                                  change_info['d_index']])) \
                    and solution.num_working_weekends[change_info['employee_id']] \
                    >= self.parameter_per_employee[change_info['employee_id']]:
                return 1
            elif not change_info['new_working'] \
                    and not solution.check_if_working_day(employee_id=change_info['employee_id'],
                                                          d_index=change_info[
                                                                      'd_index'] + scenario.day_collection.get_index_other_weekend_day(
                                                              scenario.day_collection.weekend_day_indices[
                                                                  change_info['d_index']])) \
                    and solution.num_working_weekends[change_info['employee_id']] \
                    > self.parameter_per_employee[change_info['employee_id']]:
                return -1
            else:
                return 0
        else:
            return 0

    def get_working_weekends_in_swap(self, solution, employee_id, start_index, end_index):
        """
        Get working weekends in swap without the weekends going over the edge
        """
        working_weekends = 0
        for weekend in solution.day_collection.weekends.values():
            if weekend[0] in range(start_index, end_index + 1) and weekend[1] in range(start_index, end_index + 1) \
                    and (
                    solution.check_if_working_day(employee_id, weekend[0]) or solution.check_if_working_day(employee_id,
                                                                                                            weekend[
                                                                                                                1])):
                working_weekends += 1

        return working_weekends

    def get_change_weekends_start_swap(self, solution, employee_id_1, employee_id_2, start_index):
        if not solution.day_collection.if_week_day[start_index - 1] and \
                not solution.day_collection.if_week_day[start_index]:
            if not solution.check_if_working_day(employee_id_1, start_index - 1) and \
                    solution.check_if_working_day(employee_id_1, start_index) \
                    and not solution.check_if_working_day(employee_id_2, start_index):
                return -1

            elif not solution.check_if_working_day(employee_id_1, start_index - 1) and \
                    not solution.check_if_working_day(employee_id_1, start_index) \
                    and solution.check_if_working_day(employee_id_2, start_index):
                return +1
            else:
                return 0
        else:
            return 0

    def get_change_weekends_end_swap(self, solution, employee_id_1, employee_id_2, end_index):
        if not solution.day_collection.if_week_day[end_index] and \
                not solution.day_collection.if_week_day[end_index + 1]:
            if solution.check_if_working_day(employee_id_1, end_index) and \
                    not solution.check_if_working_day(employee_id_1, end_index + 1) \
                    and not solution.check_if_working_day(employee_id_2, end_index):
                return -1

            elif not solution.check_if_working_day(employee_id_1, end_index) and \
                    not solution.check_if_working_day(employee_id_1, end_index + 1) \
                    and solution.check_if_working_day(employee_id_2, end_index):
                return +1
            else:
                return 0
        else:
            return 0

    def incremental_violations_swap_employee(self, solution, employee_id, change_in_working_weekends):
        return np.maximum(
            change_in_working_weekends + solution.num_working_weekends[employee_id] - self.parameter_per_employee[
                employee_id], 0) \
               - np.maximum(solution.num_working_weekends[employee_id] - self.parameter_per_employee[employee_id], 0)

    def incremental_working_weekends_swap(self, solution, swap_info):
        employee_id_1 = swap_info['employee_id_1']
        employee_id_2 = swap_info['employee_id_2']
        change_in_working_weekends = {employee_id_1: 0, employee_id_2: 0}
        working_weekends_1 = self.get_working_weekends_in_swap(solution, employee_id_1, swap_info['start_index'],
                                                               swap_info['end_index'])
        working_weekends_2 = self.get_working_weekends_in_swap(solution, employee_id_2,
                                                               swap_info['start_index'], swap_info['end_index'])
        # count weekends in swap
        if working_weekends_1 != working_weekends_2:
            change_in_working_weekends[employee_id_1] += working_weekends_2 - working_weekends_1
            change_in_working_weekends[employee_id_2] += working_weekends_1 - working_weekends_2

        change_in_working_weekends[employee_id_1] += self.get_change_weekends_start_swap(solution, employee_id_1,
                                                                                         employee_id_2,
                                                                                         swap_info['start_index']) \
                                                     + self.get_change_weekends_end_swap(solution, employee_id_1,
                                                                                         employee_id_2,
                                                                                         swap_info['end_index'])
        change_in_working_weekends[employee_id_2] += self.get_change_weekends_start_swap(solution, employee_id_2,
                                                                                         employee_id_1,
                                                                                         swap_info['start_index']) \
                                                     + self.get_change_weekends_end_swap(solution, employee_id_2,
                                                                                         employee_id_1,
                                                                                         swap_info['end_index'])

        swap_info['change_working_weekends'] = change_in_working_weekends
        return swap_info

    def incremental_violations_swap(self, solution, swap_info, rule_id=None):
        """
        Calc incremental violations after a swap move
        """

        return self.incremental_violations_swap_employee(solution, swap_info['employee_id_1'],
                                                         swap_info['change_working_weekends'][
                                                             swap_info['employee_id_1']]) \
               + self.incremental_violations_swap_employee(solution, swap_info['employee_id_2'],
                                                           swap_info['change_working_weekends'][
                                                               swap_info['employee_id_2']])

    def update_information_swap(self, num_working_weekends, swap_info):
        num_working_weekends[swap_info['employee_id_1']] += swap_info['change_working_weekends'][
            swap_info['employee_id_1']]
        num_working_weekends[swap_info['employee_id_2']] += swap_info['change_working_weekends'][
            swap_info['employee_id_2']]

        return num_working_weekends
