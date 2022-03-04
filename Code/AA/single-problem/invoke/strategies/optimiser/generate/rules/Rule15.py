from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule15:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # max domain.shifts per day

        parameter = self.rule.parameter1
        if self.rule.penalty > 0:
            for day in domain.days:
                shiftsToday = [shift for shift in domain.shifts if shift.start >= day.date and shift.start < day.date + int(timedelta(days=1).total_seconds())]
                if len(shiftsToday) > 0:
                    for employee in domain.employees.get_rule_applicable_employees(self.rule):
                        if self.rule.is_applicable(None, employee) and self.rule.is_applicable_day(day.date):
                            slackCoefficient = 0
                            vars = []
                            maxShiftsPerDaySlack = solver.add_var(lb=0, ub=self.maxValue,
                                                                  name='maxShiftsPerDaySlack_{}_{}_{}'.format(day.date,
                                                                                                              employee.id,
                                                                                                              self.rule.rule_counter), var_type='I')
                            if not self.rule.is_mandatory:
                                slackCoefficient = -1
                                maxShiftsPerDaySlack.obj = self.rule.penalty * domain.settings .rule_objective
                            for shift in shiftsToday:
                                if shift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable(shift, employee) and employee.is_eligible(shift) and (
                                        not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)):
                                    varText = VAR_DEFAULTS.assignment.id(employee, shift)
                                    shiftEmpVariable = solver.var_by_name(varText)
                                    if shiftEmpVariable:
                                        vars.append(shiftEmpVariable)

                            c = solver.add_constr(xsum(vars) + slackCoefficient * maxShiftsPerDaySlack <= parameter, name='maxShiftsPerDay_{}_{}_{}'.format(day.date, employee.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        for day in domain.days:
            for employee in domain.employees:
                if self.rule.is_applicable(None, employee) and self.rule.is_applicable_day(day.date):
                    slack_var = solver.var_by_name('maxShiftsPerDaySlack_{}_{}_{}'.format(day.date, employee.id,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=day.date))
