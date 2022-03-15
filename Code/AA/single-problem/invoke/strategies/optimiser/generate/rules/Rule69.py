from config import constants, configuration
from strategies.optimiser.output import Violation

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 69: Penalty for assigning less than the minimum hours per day
class Rule69:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        min_minutes_per_day = self.rule.parameter1
        for day, employee in self.get_rule_applicable_combinations(domain):
            assignment_vars = [
                (shift.pay_duration, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                for shift in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date, day.date + constants.time.seconds_per_day).get_rule_applicable_shifts(self.rule)
            ]
            objective_penalty = self.rule.penalty * domain.settings.rule_objective

            solver.create_slacked_constraint(
                id=RULES_DEFAULTS[self.rule.tag].id(day, employee, self.rule.rule_counter),
                constraint_lhs=assignment_vars,
                constraint_sense=">=",
                constraint_rhs=min_minutes_per_day,
                slack_lower_bound=0,
                slack_upper_bound=1,
                slack_constraint_coeff=10000,
                slack_objective_coeff=objective_penalty
            )

    def add_violation_to_output(self, solver, domain, output):
        # no unassigned shifts
        for day, employee in self.get_rule_applicable_combinations(domain):
            slack_var = solver.find_slack_variable_constraint(RULES_DEFAULTS[self.rule.tag].id(day, employee, self.rule.rule_counter))
            if slack_var and slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=day.date))

    def get_rule_applicable_combinations(self, domain):
        for day in domain.days.get_rule_applicable_days(self.rule):
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                yield day, employee

