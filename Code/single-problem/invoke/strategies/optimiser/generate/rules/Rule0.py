from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 0: Ensuring that no domain.shifts overlap
class Rule0:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        create_batch_constraints = not parse_boolean(self.rule.parameter1)
        if create_batch_constraints:
            for employee, shift_i in self.get_rule_applicable_combinations_batched(domain):
                no_overlap_constraint = solver.find_constraint(RULES_DEFAULTS.no_overlapping_shifts.batch_constraint.id(employee, shift_i, self.rule.rule_counter))
                lhs_constraint = []

                for shift_j in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(shift_i.start, shift_i.end).exclude_shift(shift_i):
                    if shift_j.start > shift_i.start or (shift_i.start == shift_j.start and shift_j.id > shift_i.id):
                        if not (shift_i.is_fixed and shift_j.is_fixed):
                            lhs_constraint.append((1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_j))))
                if not no_overlap_constraint and len(lhs_constraint) > 0:
                    lhs_constraint.append((1000, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_i))))
                    solver.create_slacked_constraint(
                        id=RULES_DEFAULTS[self.rule.tag].batch_constraint.id(employee, shift_i, self.rule.rule_counter),
                        constraint_lhs=lhs_constraint,
                        constraint_sense="<=",
                        constraint_rhs=1000,
                        slack_lower_bound=0,
                        slack_upper_bound=1000,
                        slack_constraint_coeff=-int(not self.rule.is_mandatory),
                        slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
                    )
        else:
            for employee, shift_i, shift_j in self.get_rule_applicable_combinations_unbatched(domain):
                lhs_constraint = [(1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_i))), (1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_j)))]
                solver.create_slacked_constraint(
                    id=RULES_DEFAULTS[self.rule.tag].singular_constraint.id(employee, shift_i,
                                                                                   shift_j, self.rule.rule_counter),
                    constraint_lhs=lhs_constraint,
                    constraint_sense="<=",
                    constraint_rhs=1,
                    slack_lower_bound=0,
                    slack_upper_bound=1,
                    slack_constraint_coeff=-int(not self.rule.is_mandatory),
                    slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
                )

    def add_violation_to_output(self, solver, domain, output):
        create_batch_constraints = True if self.rule.parameter1 == 0 else False
        if create_batch_constraints:
            for employee, shift_i in self.get_rule_applicable_combinations_batched(domain):
                overlap_slack_var = solver.find_slack_variable_constraint(
                    RULES_DEFAULTS.no_overlapping_shifts.batch_constraint.id(employee, shift_i, self.rule.rule_counter))
                if overlap_slack_var and overlap_slack_var.x > 0:
                    violation_shifts = [shift_i]
                    for shift_j in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(shift_i.start, shift_i.end).exclude_shift(shift_i):
                        if not (shift_i.is_fixed and shift_j.is_fixed):
                            shift_j_var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_j))
                            if shift_j_var and shift_j_var.x > 0:
                                violation_shifts.append(shift_j)
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                         shift_id=shift_i.id,
                                                         violation_costs=overlap_slack_var.x * overlap_slack_var.obj,
                                                         user_id=employee.id,
                                                         date=shift_i.start,
                                                         shift_start=shift_i.start,
                                                         shift_finish=shift_i.end,
                                                         department_id=shift_i.department_id,
                                                         relevant_shifts=[shift.id for shift in violation_shifts],
                                                         violation_description=generate_violation_text(shift_i, shift_j)))
        else:
            for employee, shift_i, shift_j in self.get_rule_applicable_combinations_unbatched(domain):
                for shift_j in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(shift_i.start, shift_i.end).exclude_shift(shift_i):
                    overlap_slack_var = solver.find_slack_variable_constraint(RULES_DEFAULTS.no_overlapping_shifts.singular_constraint.id(employee, shift_i, shift_j, self.rule.rule_counter))
                    if overlap_slack_var and overlap_slack_var.x > 0:
                        violation_shifts = [shift_i]
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                     shift_id=shift_i.id,
                                                     violation_costs=overlap_slack_var.x * overlap_slack_var.obj,
                                                     user_id=employee.id,
                                                     date=shift_i.start,
                                                     shift_start=shift_i.start,
                                                     shift_finish=shift_i.end,
                                                     department_id=shift_i.department_id,
                                                     relevant_shifts=[shift.id for shift in violation_shifts],
                                                     violation_description=generate_violation_text(shift_i, shift_j)))

    def get_rule_applicable_combinations_batched(self, domain):
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            for shift_i in employee.eligible_shifts_in_schedule:
                yield employee, shift_i

    def get_rule_applicable_combinations_unbatched(self, domain):
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            for shift_i in employee.eligible_shifts_in_schedule:
                for shift_j in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(shift_i.start,
                                                                                                  shift_i.end).exclude_shift(
                        shift_i):
                    if not (shift_i.is_fixed and shift_j.is_fixed):
                        yield employee, shift_i, shift_j


def generate_violation_text(shift_i, shift_j):
    return "Shift {} and shift {} are overlapping".format(shift_i.id, shift_j.id)

