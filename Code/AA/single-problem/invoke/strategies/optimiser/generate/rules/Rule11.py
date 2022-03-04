from config import configuration
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule11:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # Rule 11: Minimum minutes per shift
        for shift in domain.shifts.get_unfixed_shifts().get_shifts_starts_in_interval(domain.settings.start, domain.settings.end).get_rule_applicable_shifts(self.rule):
            shiftDuration = shift.pay_duration + shift.break_duration

            if shiftDuration < self.rule.parameter1:
                for employee in domain.employees.get_rule_applicable_employees(self.rule):
                    if not employee.is_fixed and employee.is_eligible(shift):
                        shiftMinDurationSlackVar = solver.add_var(lb=0, ub=1, name='shiftMinDurationSlack_{}_{}_{}'.format(
                            employee.id, shift.id,self.rule.rule_counter), var_type='B')
                        slack_coeff = 0
                        if not self.rule.is_mandatory:
                            slack_coeff = 1
                            shiftMinDurationSlackVar.obj = (self.rule.parameter1 - shiftDuration) * self.rule.penalty * domain.settings .rule_objective
                        varText = VAR_DEFAULTS.assignment.id(employee, shift)

                        shiftEmpVariable = solver.var_by_name(varText)
                        if shiftEmpVariable:
                            solver.add_constr(shiftEmpVariable*-1 + slack_coeff*shiftMinDurationSlackVar == 0, name='shiftMinDurationConstraint_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        # minimum minutes per shift
        for shift in domain.shifts.get_unfixed_shifts().get_shifts_starts_in_interval(domain.settings.start, domain.settings.end).get_rule_applicable_shifts(self.rule):
            shiftDuration = shift.pay_duration + shift.break_duration
            if shiftDuration < self.rule.parameter1:
                for employee in domain.employees.get_rule_applicable_employees(self.rule):
                    if employee.is_eligible(shift):
                        slack_var = solver.var_by_name('shiftMinDurationSlack_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))
                        if slack_var and slack_var.x > 0.0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                         user_id=employee.id,
                                                         violation_costs=slack_var.x * slack_var.obj,
                                                         shift_id=shift.id,
                                                         date=shift.start,
                                                         shift_start=shift.start,
                                                         shift_finish=shift.end,
                                                         department_id=shift.department_id))
