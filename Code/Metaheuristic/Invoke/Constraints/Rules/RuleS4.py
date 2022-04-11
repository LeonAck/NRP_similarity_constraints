from Invoke.Constraints.initialize_rules import Rule

class RuleS4(Rule):
    """
        Rule that checks whether a nurse works complete weekends
    """

    def __init__(self, employees, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, scenario, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, scenario, employee_id):
        """
        Function to count violations for a given day, shift type and skill
        """
        incomplete_weekends = 0
        for weekend in scenario.day_collection.weekends.values():
            # check if only one day of the weekend is working
            if (solution.check_if_working_day(employee_id, weekend[0]) and
                not solution.check_if_working_day(employee_id, weekend[1])) or \
                    (solution.check_if_working_day(employee_id, weekend[1]) and
                        not solution.check_if_working_day(employee_id, weekend[0])):
                incomplete_weekends += 1
        return incomplete_weekends

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        \delta number_of_violations
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

