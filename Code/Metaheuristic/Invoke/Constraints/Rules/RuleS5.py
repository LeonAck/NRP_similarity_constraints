from Invoke.Constraints.initialize_rules import Rule
from general_functions import check_if_working_day

class RuleS5(Rule):
    """
        Rule that checks whether a nurse works complete weekends
    """

    def __init__(self, employees, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution.shift_assignments, scenario, employee_id)
                    for employee_id in scenario.employees._collection.keys()
                    if self.parameter_per_employee[employee_id] == 1])

    def count_violations_employee(self, shift_assignments, scenario, employee_id):
        """
        Function to count violations for a given day, shift type and skill
        """
        incomplete_weekends = 0
        for weekend in scenario.day_collection.weekends.values():
            # check if only one day of the weekend is working
            if (check_if_working_day(shift_assignments, employee_id, weekend[0]) and
                not check_if_working_day(shift_assignments, employee_id, weekend[1])) or \
                    (check_if_working_day(shift_assignments, employee_id, weekend[1]) and
                     not check_if_working_day(shift_assignments, employee_id, weekend[0])):
                incomplete_weekends += 1
        return incomplete_weekends

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        delta number_of_violations
        """
        # check if the day is a weekend day and the employee gets penalized for
        # incomplete working weekends
        if self.parameter_per_employee[change_info["employee_id"]] == 1 \
                and change_info['d_index'] in scenario.day_collection.list_weekend_days:
            # check whether change is off to assigned
            if not change_info['current_working']:
                # check if the other day is a working day
                if solution.check_if_working_day(
                        employee_id=change_info['employee_id'],
                        d_index=change_info['d_index'] +
                                scenario.day_collection.get_index_other_weekend_day(
                                    scenario.day_collection.weekend_day_indices[
                                        change_info['d_index']])):
                    return -1
                else:
                    return 1
            # check whether change is assigned to off
            elif not change_info['new_working']:
                # check if the other day is a working day
                if solution.check_if_working_day(
                        employee_id=change_info['employee_id'],
                        d_index=change_info['d_index'] +
                                scenario.day_collection.get_index_other_weekend_day(
                                    scenario.day_collection.weekend_day_indices[
                                        change_info['d_index']])):
                    return 1
                else:
                    return -1
            else:
                return 0
        else:
            return 0

    def incremental_violations_swap(self, solution, swap_info, rule_id=None):

        employee_id_1 = swap_info['employee_id_1']
        employee_id_2 = swap_info['employee_id_2']
        if self.parameter_per_employee[employee_id_1] == 0 and self.parameter_per_employee[employee_id_2] == 0:
            return 0
        else:
            return self.count_change_incomplete_weekends_swap(solution.shift_assignments,
                                                              solution.day_collection,
                                                              employee_id_1,
                                                              employee_id_2,
                                                              start_index=swap_info['start_index'],
                                                              end_index=swap_info['end_index'])

    def count_change_incomplete_weekends_swap(self, shift_assignments, day_collection, employee_id_1, employee_id_2,
                                              start_index, end_index):
        # get incomplete weekends within the swap
        incomplete_weekends_1 = count_incomplete_weekends_in_swap(shift_assignments, day_collection, employee_id_1,
                                                                  start_index, end_index)
        incomplete_weekends_2 = count_incomplete_weekends_in_swap(shift_assignments, day_collection, employee_id_2,
                                                                  start_index, end_index)

        change_in_incomplete_weekends_1 = self.count_incremental_incomplete_weekends_employee(
            shift_assignments, day_collection, employee_id_1, employee_id_2,
            start_index, end_index, incomplete_weekends_1, incomplete_weekends_2)

        change_in_incomplete_weekends_2 = self.count_incremental_incomplete_weekends_employee(
            shift_assignments, day_collection, employee_id_2, employee_id_1,
            start_index, end_index, incomplete_weekends_2, incomplete_weekends_1)

        # sum total change in incomplete weekends as violation
        return change_in_incomplete_weekends_1 + change_in_incomplete_weekends_2

    def count_incremental_incomplete_weekends_employee(self, shift_assignments, day_collection, employee_id,
                                                       other_employee_id,
                                                       start_index, end_index, incomplete_weekends,
                                                       other_incomplete_weekends):
        if self.parameter_per_employee[employee_id]:
            # count change in incomplete weekends within swaps
            change_in_incomplete_weekends = other_incomplete_weekends - incomplete_weekends

            # add change in working weekends on the edges of the swaps
            change_in_incomplete_weekends += get_change_incomplete_weekends_start(shift_assignments, day_collection,
                                                                                  employee_id,
                                                                                  other_employee_id,
                                                                                  start_index) \
                                             + get_change_incomplete_weekends_end(shift_assignments, day_collection,
                                                                                  employee_id,
                                                                                  other_employee_id, end_index)
        else:
            change_in_incomplete_weekends = 0

        return change_in_incomplete_weekends


def get_change_incomplete_weekends_start(shift_assignments, day_collection, employee_id,
                                         other_employee_id,
                                         start_index):
    if not day_collection.if_week_day[start_index - 1] and \
            not day_collection.if_week_day[start_index]:
        # check if going from incomplete to complete
        if check_if_working_day(shift_assignments, employee_id, start_index - 1) \
                != check_if_working_day(shift_assignments, employee_id, start_index) \
                and check_if_working_day(shift_assignments, employee_id, start_index - 1) \
                == check_if_working_day(shift_assignments, other_employee_id, start_index):
            return -1
        # check if going form complete to incomplete
        elif check_if_working_day(shift_assignments, employee_id, start_index - 1) \
                == check_if_working_day(shift_assignments, employee_id, start_index) \
                and check_if_working_day(shift_assignments, employee_id, start_index - 1) \
                != check_if_working_day(shift_assignments, other_employee_id, start_index):
            return 1
        else:
            return 0
    else:
        return 0


def get_change_incomplete_weekends_end(shift_assignments, day_collection, employee_id,
                                       other_employee_id, end_index):
    if not day_collection.if_week_day[end_index] and \
            not day_collection.if_week_day[end_index + 1]:
        # check if going from incomplete to complete
        if check_if_working_day(shift_assignments, employee_id, end_index) \
                != check_if_working_day(shift_assignments, employee_id, end_index + 1) \
                and check_if_working_day(shift_assignments, employee_id, end_index + 1) \
                == check_if_working_day(shift_assignments, other_employee_id, end_index):
            return -1
        # check if going form complete to incomplete
        if check_if_working_day(shift_assignments, employee_id, end_index) \
                == check_if_working_day(shift_assignments, employee_id, end_index + 1) \
                and check_if_working_day(shift_assignments, employee_id, end_index + 1) \
                != check_if_working_day(shift_assignments, other_employee_id, end_index):
            return +1
        else:
            return 0
    else:
        return 0


def count_incomplete_weekends_in_swap(shift_assignments, day_collection, employee_id, start_index, end_index):
    incomplete_weekends = 0
    for weekend in day_collection.weekends.values():
        if weekend[0] in range(start_index, end_index + 1) and weekend[1] in range(start_index, end_index + 1) \
                and check_if_working_day(shift_assignments, employee_id, weekend[0]) != check_if_working_day(
            shift_assignments,
            employee_id, weekend[1]):
            incomplete_weekends += 1

    return incomplete_weekends


