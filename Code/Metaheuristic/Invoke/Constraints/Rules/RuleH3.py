from Invoke.Constraints.initialize_rules import Rule

class RuleH3(Rule):
    """
    Rule that checks for understaffing.
    Compares skill request to number of nurses with that skill assigned to shift
    """
    def __init__(self, rules_spec):
        super().__init__(rules_spec)

    def check_violations_mandatory(self, solution, employees):
        """
        Check violations for entire solution
        """
        flag = True
        for employee in employees:
            # check all employees until violation is found
            while flag:
                flag = self.violations_per_employee(solution, employee)
        # if any violation will return flag is false
        return flag

    def violations_per_employee(self, solution, employee):
        """
        Check violations per nurse
        """
        # get number of violations
        number_of_violations = 1

        if self.is_mandatory == True:
            return number_of_violations > 0
        else:
            return number_of_violations