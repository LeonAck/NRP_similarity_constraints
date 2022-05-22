from Invoke.Constraints.initialize_rules import Rule

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


