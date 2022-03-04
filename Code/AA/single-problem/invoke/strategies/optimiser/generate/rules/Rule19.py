from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule19:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):

        # If the input shift has a user ID, treat it like a penalty
        if self.rule.penalty > 0:
            for shift in domain.shifts:
                if shift.employee_id and not shift.is_fixed:
                    for employee in domain.employees:
                        if employee.id == shift.employee_id and self.rule.is_applicable(shift, employee) and self.rule.is_applicable_day(shift.start):
                            allocatedPreferenceSlack = solver.add_var(lb=0, ub=1, name='allocatedPreferenceSlack_{}_{}_{}'.format(
                                shift.id, employee.id,self.rule.rule_counter), var_type='B')
                            slack_coeff = 0
                            varText = VAR_DEFAULTS.assignment.id(employee, shift)
                            shiftAllocVar = solver.var_by_name(varText)
                            if not self.rule.is_mandatory:
                                slack_coeff = -1
                                allocatedPreferenceSlack.obj =-1 * self.rule.penalty * domain.settings .rule_objective
                            if shiftAllocVar:
                                solver.add_constr(shiftAllocVar + slack_coeff*allocatedPreferenceSlack == 0, name='allocatedPreference_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        # If the input shift has a user ID, treat it like a penalty
        if self.rule.penalty > 0:
            for shift in domain.shifts:
                if shift.employee_id and not shift.is_fixed:
                    for employee in domain.employees:
                        if employee.id == shift.employee_id and self.rule.is_applicable(shift, employee) and self.rule.is_applicable_day(shift.start):
                            slack_var = solver.var_by_name('allocatedPreferenceSlack_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        shift_id=shift.id,
                                                        date=shift.start,
                                                        shift_start=shift.start,
                                                        shift_finish=shift.end,
                                                        department_id=shift.department_id))
