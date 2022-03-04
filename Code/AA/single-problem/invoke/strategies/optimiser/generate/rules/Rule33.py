from random import randrange
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 33: ensure that domain.shifts on next day have the same start time
def roundup(x):
    return x if x % 60 == 0 else x + 60 - x % 60


class Rule33:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            max_range_to_create_constraints_lhs = self.rule.parameter1 * 60
            max_range_to_create_constraints_rhs = self.rule.parameter2 * 60
            for employee in domain.employees:
                employeeShifts = [shift for shift in domain.shifts if employee.is_eligible(shift)]
                for shift1 in employeeShifts:
                    shift1_start_time = int((shift1.start / 60) % (24 * 60))
                    for shift2 in employeeShifts:
                        if shift1 != shift2 and not (shift1.is_fixed and shift2.is_fixed):
                            if (86_400 - max_range_to_create_constraints_lhs) <= (shift2.start - shift1.start) <= (86_400 + max_range_to_create_constraints_rhs):
                                shift2_start_time = int((shift2.start / 60) % (24 * 60))
                                start_time_difference = int(abs(shift1_start_time - shift2_start_time))
                                start_time_difference = roundup(start_time_difference)
                                if start_time_difference > 0:
                                    constraint_text = 'sameTimeConstraint_{}_{}_{}_{}'.format(employee.id, shift1.id, shift2.id,self.rule.rule_counter)
                                    slack_var_text = 'sameTimeSlack_{}_{}_{}_{}'.format(employee.id, str(shift1.id),
                                                                                        str(shift2.id),self.rule.rule_counter)
                                    same_time_slack = solver.add_var(lb=0, ub=1, var_type='B', name=slack_var_text)
                                    slack_coeff = 0

                                    shift1_var_text = VAR_DEFAULTS.assignment.id(employee, shift1)
                                    shift2_var_text = VAR_DEFAULTS.assignment.id(employee, shift2)
                                    shift1_var = solver.var_by_name(shift1_var_text)
                                    shift2_var = solver.var_by_name(shift2_var_text)

                                    if not self.rule.is_mandatory:
                                        slack_coeff = -1
                                        same_time_slack.obj = int(start_time_difference / 60) * self.rule.penalty * domain.settings .rule_objective

                                    c = solver.add_constr(shift1_var + shift2_var + slack_coeff*same_time_slack <= 1, name=constraint_text)

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            max_range_to_create_constraints_lhs = self.rule.parameter1 * 60
            max_range_to_create_constraints_rhs = self.rule.parameter2 * 60
            for employee in domain.employees:
                employeeShifts = [shift for shift in domain.shifts if employee.is_eligible(shift)]
                for shift1 in employeeShifts:
                    shift1_start_time = int((shift1.start / 60) % (24 * 60))
                    for shift2 in employeeShifts:
                        if shift1 != shift2 and not (shift1.is_fixed and shift2.is_fixed):
                            if 86_400 - max_range_to_create_constraints_lhs <= (shift2.start - shift1.start) <= 86_400 + max_range_to_create_constraints_rhs:
                                shift2_start_time = int((shift2.start / 60) % (24 * 60))
                                start_time_difference = int(abs(shift1_start_time - shift2_start_time))
                                if start_time_difference > 0:
                                    slack_var_text = 'sameTimeSlack_{}_{}_{}_{}'.format(employee.id, str(shift1.id), str(shift2.id),self.rule.rule_counter)
                                    slack_var = solver.var_by_name(slack_var_text)
                                    if slack_var and slack_var.x > 0:
                                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                                user_id=employee.id,
                                                                violation_costs=slack_var.x * slack_var.obj,
                                                                shift_id=shift1.id,
                                                                date=shift1.start,
                                                                shift_start=shift1.start,
                                                                shift_finish=shift1.end,
                                                                department_id=shift1.department_id))