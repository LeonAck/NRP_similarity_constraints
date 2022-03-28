from Invoke.Constraints.initialize_rules import Rule

class RuleS1(Rule):
    """
        Rule that checks for optimal coverage per skill request
        Compares optimal skill request to number of nurses with that skill assigned to shift
    """

    def __init__(self, rule_spec=None):
        super().__init__(rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        violation_counter = 0
        for d_index in range(scenario.num_days_in_horizon):
            for s_index in range(scenario.num_shift_types):
                for sk_index in range(scenario.skill_collection.num_skills):
                    violation_counter += self.count_violations_day_shift_skill(solution, scenario,
                                                          d_index, s_index,
                                                          sk_index)
        return violation_counter

    def count_violations_day_shift_skill(self, solution, scenario, d_index, s_index, sk_index):
        """
        Function to count violations for a given day, shift type and skill
        """
        violation_counter = 0

        return violation_counter

    def increment_violations_day_shift_skill(self, solution, d_index, s_index,
                                             sk_index, insertion=True, increment=1):
        """
        Function to count violations for a given day, shift type and skill
        """
        # check if there is a shortage compared to optimal level
        # TODO adjust for higher increments if necessary
        if insertion:
            return -1 if solution.diff_opt_request[(d_index, s_index, sk_index)] < 0 else 0
        else:
            return 1 if solution.diff_opt_request[(d_index, s_index, sk_index)] <= 0 else 0

