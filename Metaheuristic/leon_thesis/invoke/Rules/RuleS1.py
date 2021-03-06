from Domain.RuleCollection import Rule
import numpy as np


class RuleS1(Rule):
    """
        Rule that checks for optimal coverage per skill request
        Compares optimal skill request to number of nurses with that skill assigned to shift
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        violation_counter = 0
        num_shift_types = scenario.num_shift_types
        num_skills = scenario.skill_collection.num_skills
        optimal_coverage = scenario.optimal_coverage
        shift_assignments = solution.shift_assignments
        for d_index in range(scenario.num_days_in_horizon):
            for s_index in range(num_shift_types):
                for sk_index in range(num_skills):
                    violation_counter += self.count_violations_day_shift_skill(
                       shift_assignments, optimal_coverage,
                        d_index, s_index,
                        sk_index)
        return violation_counter

    def count_violations_day_shift_skill(self,shift_assignments, optimal_coverage, d_index, s_index, sk_index):
        """
        Function to count violations for a given day, shift type and skill
        """
        assignment_count = self.count_assignments_day_shift_skill(shift_assignments, d_index, s_index, sk_index)

        if assignment_count < optimal_coverage[(d_index, sk_index, s_index)]:
            return optimal_coverage[(d_index, sk_index, s_index)] - assignment_count
        else:
            return 0

    def count_assignments_day_shift_skill(self,shift_assignments, d_index, s_index, sk_index):
        assignment_count = 0

        for employee in shift_assignments.values():
            if np.array_equal(employee[d_index], np.array([s_index, sk_index])):
                assignment_count += 1

        return assignment_count

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        delta number_of_violations
        """
        violation = 0
        if change_info["current_working"]:
            violation += self.increment_violations_day_shift_skill(solution.diff_opt_request,
                                                                   d_index=change_info["d_index"],
                                                                   s_index=change_info["curr_s_type"],
                                                                   sk_index=change_info["curr_sk_type"],
                                                                   insertion=False)
        if change_info["new_working"]:
            violation += self.increment_violations_day_shift_skill(solution.diff_opt_request,
                                                                   d_index=change_info["d_index"],
                                                                   s_index=change_info["new_s_type"],
                                                                   sk_index=change_info["new_sk_type"],
                                                                   insertion=True)

        return violation

    def increment_violations_day_shift_skill(self, diff_opt_request, d_index, s_index,
                                             sk_index, insertion=True):
        """
        Function to count violations for a given day, shift type and skill
        """
        # check if there is a shortage compared to optimal level
        if insertion:
            return -1 if diff_opt_request[(d_index, sk_index, s_index)] < 0 else 0
        else:
            return 1 if diff_opt_request[(d_index, sk_index, s_index)] <= 0 else 0
