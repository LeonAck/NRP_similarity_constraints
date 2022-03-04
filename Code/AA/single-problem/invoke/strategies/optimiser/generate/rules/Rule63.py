from mip import xsum
from datetime import timedelta
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule63:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # day after shift of type another shift of the same type, otherwise x days no shift of the same type.
        if self.rule.penalty > 0:
            min_free_days_after_shift_type = int(self.rule.parameter1)
            shift_type_for_rule = self.rule.parameter2
            for employee in domain.employees:
                if not employee.is_fixed and self.rule.is_applicable(None, employee):
                    employeeShiftsOfType = [shift for shift in domain.shifts if shift_type_for_rule in shift.shift_types and employee.is_eligible(shift)]
                    if len(employeeShiftsOfType) > 0:
                        for day in domain.days:
                            if self.rule.is_applicable_day(day.date):
                                shifts_today = [shift for shift in employeeShiftsOfType if day.date < shift.end <= day.date + int(timedelta(days=1).total_seconds()) and shift.in_schedule(domain.settings.start, domain.settings.end)]
                                shifts_next_day = [shift for shift in employeeShiftsOfType if day.date + int(timedelta(days=1).total_seconds()) < shift.end <= day.date + int(timedelta(days=2).total_seconds()) and shift.in_schedule(domain.settings.start,domain.settings.end)]
                                disallowed_shifts = [shift for shift in employeeShiftsOfType if day.date + int(timedelta(days=2).total_seconds()) < shift.end <= day.date + min_free_days_after_shift_type * 24 * 60 * 60 and shift.in_schedule(domain.settings.start,domain.settings.end)]
                                shift_vars_today = [solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) for shift in shifts_today]
                                shift_vars_next_day = [solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) for shift in shifts_next_day]
                                disallowed_shift_vars = [solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) for shift in disallowed_shifts]
                                if(len(shifts_today) > 0):
                                    fixed_disallowed_shifts = 0
                                    for shift in disallowed_shifts:
                                        if shift.is_fixed:
                                            fixed_disallowed_shifts += 1

                                    slack_var = solver.add_var(lb=0, ub=len(disallowed_shift_vars), var_type='I',
                                                                   name='rest_after_shift_type_{}_{}_{}_{}'.format(employee.id, shift_type_for_rule,
                                                                                                                        day.date,
                                                                                                                        self.rule.rule_counter))
                                    if not self.rule.is_mandatory:
                                        slack_coeff = 1
                                        slack_var.obj = slack_var.obj + int(self.rule.penalty * domain.settings.rule_objective)

                                    help_var = solver.add_var(var_type='B',
                                                                   name='help_var_rest_after_shift_type_{}_{}_{}_{}'.format(employee.id, shift_type_for_rule,
                                                                                                                        day.date,
                                                                                                                        self.rule.rule_counter))
                                    solver.add_constr(xsum(shift_vars_today) - xsum(shift_vars_next_day) <= 10000*help_var,
                                                      name='rest_after_shift_type_helpvar_{}_{}_{}_{}'.format(employee.id, shift_type_for_rule,
                                                                                                                        day.date,
                                                                                                                        self.rule.rule_counter))
                                    solver.add_constr(xsum(disallowed_shift_vars) - slack_coeff*slack_var<= 10000*(1-help_var),
                                                      name='rest_after_shift_type_{}_{}_{}_{}'.format(employee.id, shift_type_for_rule,
                                                                                                                        day.date,
                                                                                                                    self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            shift_type_for_rule = str(self.rule.parameter2)
            for employee in domain.employees:
                if not employee.is_fixed and self.rule.is_applicable(None, employee):
                    for day in domain.days:
                        if self.rule.is_applicable_day(day.date):
                            slack_var = solver.var_by_name(name='rest_after_shift_type_{}_{}_{}_{}'.format(employee.id, shift_type_for_rule,
                                                                                                                day.date,
                                                                                                                self.rule.rule_counter))
                            if slack_var and slack_var.x:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=day.date))

