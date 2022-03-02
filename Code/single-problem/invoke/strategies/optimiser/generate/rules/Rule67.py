from config import constants, configuration
from strategies.optimiser.output import Violation

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 67: Penalty for not assigning the minimum number of shifts per shift group
class Rule67:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        min_on_groups = self.rule.parameter1
        for group_id in self.get_rule_applicable_combinations(domain):
            assignment_vars = []
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                assignment_vars.extend([
                    (1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                    for shift in employee.eligible_shifts_in_schedule.get_shifts_by_filter(lambda shift: shift.group_id == group_id)
                ])
            objective_penalty = self.rule.penalty * domain.settings.rule_objective

            solver.create_slacked_constraint(
                id=RULES_DEFAULTS[self.rule.tag].id(group_id, self.rule.rule_counter),
                constraint_lhs=assignment_vars,
                constraint_sense=">=",
                constraint_rhs=min_on_groups,
                slack_lower_bound=0,
                slack_upper_bound= 0 if self.rule.is_mandatory else min_on_groups,
                slack_constraint_coeff=1,
                slack_objective_coeff= objective_penalty if len(assignment_vars) > 0 else 0
            )

    def add_violation_to_output(self, solver, domain, output):
        for group_id in self.get_rule_applicable_combinations(domain):
            assignment_slack_var = solver.find_slack_variable_constraint(RULES_DEFAULTS[self.rule.tag].id(group_id, self.rule.rule_counter))
            if assignment_slack_var and assignment_slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id,
                                        violation_costs=assignment_slack_var.x * assignment_slack_var.obj,
                                        rule_tag= self.rule.tag,
                                        shift_group=group_id))

    def get_rule_applicable_combinations(self, domain):
        for group_id in self.rule.shift_group_ids:
            yield group_id
