from config import constants, configuration
from strategies.optimiser.output import Violation

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 1: Penalty for keeping unassigned shifts
class Rule1:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        use_hours = self.rule.parameter1
        for shift in self.get_rule_applicable_combinations(domain):
            assignment_vars = [
                (1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                for employee in domain.employees.get_shift_eligible_employees(shift)
            ]
            objective_penalty = self.rule.penalty * domain.settings.rule_objective
            if use_hours == 1:
                objective_penalty *= shift.pay_duration / constants.time.minutes_per_hour
            solver.create_slacked_constraint(
                id=RULES_DEFAULTS[self.rule.tag].id(shift, self.rule.rule_counter),
                constraint_lhs=assignment_vars,
                constraint_sense="==",
                constraint_rhs=1,
                slack_lower_bound=0,
                slack_upper_bound=int(not self.rule.is_mandatory),
                slack_constraint_coeff=1,
                slack_objective_coeff=objective_penalty
            )

    def add_violation_to_output(self, solver, domain, output):
        # no unassigned shifts
        for shift in self.get_rule_applicable_combinations(domain):
            assignment_slack_var = solver.find_slack_variable_constraint(RULES_DEFAULTS[self.rule.tag].id(shift, self.rule.rule_counter))
            if assignment_slack_var and assignment_slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id,
                                        rule_tag= self.rule.tag,
                                             shift_id=shift.id,
                                             violation_costs=assignment_slack_var.x * assignment_slack_var.obj,
                                             date=shift.start,
                                             shift_start=shift.start,
                                             shift_finish=shift.end,
                                             department_id=shift.department_id,
                                             relevant_shifts=[shift.id],
                                             violation_description=generate_violation_text(shift.id)))

    def get_rule_applicable_combinations(self, domain):
        for shift in domain.shifts.get_non_fixed_shifts().get_shifts_starts_in_interval(domain.settings.start, domain.settings.end).get_rule_applicable_shifts(self.rule):
            yield shift

def generate_violation_text(shift_id):
    return "Shift with ID {} is not assigned to any employee".format(shift_id)
