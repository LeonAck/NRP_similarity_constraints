from config import configuration
from strategies.optimiser.output import Violation

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
class Rule20:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # overlap with preferences
        for employee, preference, shift in self.get_rule_applicable_combinations(domain):
            overlap_hours = shift.get_overlap_hours(preference.start, preference.end)
            if overlap_hours > 0:
                solver.create_slacked_constraint(
                    id=RULES_DEFAULTS[self.rule.tag].id(employee, preference, shift, self.rule.rule_counter),
                    constraint_lhs=[(1,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))],
                    constraint_sense="==",
                    constraint_rhs=0,
                    slack_lower_bound=0,
                    slack_upper_bound=int(not self.rule.is_mandatory),
                    slack_constraint_coeff=-1,
                    slack_objective_coeff=-1 * self.rule.penalty * domain.settings.rule_objective * overlap_hours
                )

    def add_violation_to_output(self, solver, domain, output):
        for employee, preference, shift in self.get_rule_applicable_combinations(domain):
            slack_var = solver.find_variable(RULES_DEFAULTS[self.rule.tag].id(employee, preference, shift, self.rule.rule_counter))
            if slack_var and slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                        user_id=employee.id,
                                        violation_costs=slack_var.x * slack_var.obj,
                                        shift_id=shift.id,
                                        date=shift.start,
                                        shift_start=shift.start,
                                        shift_finish=shift.end,
                                        department_id=shift.department_id))

    def get_rule_applicable_combinations(self, domain):
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            for preference in employee.employee_preferences:
                for shift in employee.unfixed_eligible_shifts_in_schedule.get_rule_applicable_shifts(self.rule).get_shifts_within_interval(preference.start, preference.end):
                    yield employee, preference, shift
