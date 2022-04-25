from Invoke.Constraints.initialize_rules import Rule

class RuleS7Day(Rule):
    """
        Rule that checks the number of working weekends
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)


    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution, scenario, employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, solution, scenario, employee_id):
        """
        Function to count violations for a given employee
        """
        return sum(solution.day_comparison[employee_id] == 0)

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change operator
        :return:
        \delta number_of_violations
        """
        violation_counter = 0
        parameter_1 = solution.rule_collection.collection["S7Day"].parameter_1
        if not change_info['current_working'] or not change_info['new_working']:
            if solution.day_comparison[change_info['employee_id']][change_info['d_index']] == 1:
                violation_counter += 1
            elif solution.day_comparison[change_info['employee_id']][change_info['d_index']] == 0:
                violation_counter -= 1

            # compare to future day
            if self.check_future_day_in_horizon(solution.day_collection, change_info['d_index'], parameter_1):
                if solution.day_comparison[change_info['employee_id']][change_info['d_index'] + parameter_1] == 1:
                    violation_counter += 1
                elif solution.day_comparison[change_info['employee_id']][change_info['d_index'] + parameter_1] == 0:
                    violation_counter -= 1

        return violation_counter

    def update_information_off_to_assigned(self, solution, change_info):
        parameter_1 = solution.rule_collection.collection["S7Day"].parameter_1
        if not change_info['current_working'] or not change_info['new_working']:
            # compare to ref day
            if solution.day_comparison[change_info['employee_id']][change_info['d_index']] == 1:
                print("was the same")
                solution.day_comparison[change_info['employee_id']][change_info['d_index']] = 0
                print("after change", solution.day_comparison[change_info['employee_id']][change_info['d_index']])
            elif solution.day_comparison[change_info['employee_id']][change_info['d_index']] == 0:
                print("was different")
                solution.day_comparison[change_info['employee_id']][change_info['d_index']] = 1
                print("after change", solution.day_comparison[change_info['employee_id']][change_info['d_index']])
            # compare to future day
            if self.check_future_day_in_horizon(solution.day_collection, change_info['d_index'], parameter_1):
                if solution.day_comparison[change_info['employee_id']][change_info['d_index']+parameter_1] == 1:
                    solution.day_comparison[change_info['employee_id']][change_info['d_index']+parameter_1] = 0
                elif solution.day_comparison[change_info['employee_id']][change_info['d_index']+parameter_1] == 0:
                    solution.day_comparison[change_info['employee_id']][change_info['d_index']+parameter_1] = 1

        return solution

    def check_ref_day_in_horizon(self, d_index):
        """
        Function to check whether the d_index - parameter_1 is in the horizon
        """
        return (d_index - self.parameter_1) >= 0

    def check_future_day_in_horizon(self, day_collection, d_index, parameter_1):
        return (d_index + parameter_1) <= day_collection.num_days_in_horizon-1