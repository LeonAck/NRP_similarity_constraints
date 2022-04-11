from Invoke.Constraints.initialize_rules import Rule
import numpy as np


class RuleS2Max(Rule):
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
        return 0

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
        delta number_of_violations
        """
        violation = 0
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]

        if not change_info['current_working']:
            pass
        elif not change_info['new_working']:
            # find in what work stretch the d_index is
            for start_index, work_stretch in solution.work_stretches[change_info['employee_id']].items():
                if change_info['d_index'] in range(start_index, work_stretch["end_index"]):
                    if work_stretch['length'] > employee_parameter:

                        split_1 = change_info['d_index'] - start_index
                        split_2 = work_stretch['end_index'] - change_info['d_index']
                        if split_1 > employee_parameter and \
                                split_2 > employee_parameter:
                            return - ((work_stretch['length'] - employee_parameter)
                                      - (split_1 - employee_parameter)
                                      - (split_2 - employee_parameter))
                        elif split_1 > employee_parameter:
                            return - ((work_stretch['length'] - employee_parameter)
                                      - (split_1 - employee_parameter))
                        elif split_2 > employee_parameter:
                            return - ((work_stretch['length'] - employee_parameter)
                                      - (split_2 - employee_parameter))
                        else:
                            return - (work_stretch['length'] - employee_parameter)
                    else:
                        return 0

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
