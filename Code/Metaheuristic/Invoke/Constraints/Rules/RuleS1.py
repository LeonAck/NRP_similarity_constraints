from Invoke.Constraints.initialize_rules import Rule
import numpy as np

class RuleS1(Rule):
    """
        Rule that checks for optimal coverage per skill request
        Compares optimal skill request to number of nurses with that skill assigned to shift
    """

    def __init__(self, employees, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        violation_counter = 0

        for d_index in range(scenario.num_days_in_horizon):
            for s_index in range(scenario.num_shift_types):
                for sk_index in range(scenario.skill_collection.num_skills):
                    violation_counter += self.count_violations_day_shift_skill(
                                            solution, scenario,
                                            d_index, s_index,
                                            sk_index)
        return violation_counter

    def count_violations_day_shift_skill(self, solution, scenario, d_index, s_index, sk_index):
        """
        Function to count violations for a given day, shift type and skill
        """
        assignment_count = 0

        for employee in solution.shift_assignments.values():
            if np.array_equal(employee[d_index], np.array([s_index, sk_index])):
                assignment_count += 1
        if assignment_count < scenario.optimal_coverage[(d_index, sk_index, s_index)]:
            return scenario.optimal_coverage[(d_index, sk_index, s_index)] - assignment_count
        else:
            return 0

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        \delta number_of_violations
        """
        violation = 0
        if change_info["current_working"]:
            violation += self.increment_violations_day_shift_skill(solution,
                                                                   d_index=change_info["d_index"],
                                                                   s_index=change_info["curr_s_type"],
                                                                   sk_index=change_info["curr_sk_type"],
                                                                   insertion=False)
        if change_info["new_working"]:
            violation += self.increment_violations_day_shift_skill(solution,
                                                                   d_index=change_info["d_index"],
                                                                   s_index=change_info["new_s_type"],
                                                                   sk_index=change_info["new_sk_type"],
                                                                   insertion=True)

        return violation

    def increment_violations_day_shift_skill(self, solution, d_index, s_index,
                                             sk_index, insertion=True, increment=1):
        """
        Function to count violations for a given day, shift type and skill
        """
        # check if there is a shortage compared to optimal level
        # TODO adjust for higher increments if necessary
        if insertion:
            return -1 if solution.diff_opt_request[(d_index, sk_index, s_index)] < 0 else 0
        else:
            return 1 if solution.diff_opt_request[(d_index, sk_index, s_index)] <= 0 else 0

