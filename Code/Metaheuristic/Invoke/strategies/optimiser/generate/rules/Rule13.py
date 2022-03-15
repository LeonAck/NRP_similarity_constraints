from mip import xsum
from datetime import timedelta
from config import configuration
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule13:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # Rule 13: Maximum number of minutes per day
        if self.rule.penalty > 0:
            for day in domain.days:
                shiftsToday = [shift for shift in domain.shifts if shift.start >= day.date and shift.start < day.date + int(timedelta(days=1).total_seconds())]
                if len(shiftsToday) > 0:
                    for employee in domain.employees.get_rule_applicable_employees(self.rule):
                        if self.rule.is_applicable(None, employee) and self.rule.is_applicable_day(day.date):
                            maxHoursPerEmployeeDaySlackVar = solver.add_var(lb=0, ub=self.rule.parameter1 * 100,
                                                                           name='maxHoursPerEmployeeDaySlack_{}_{}_{}'.format(
                                                                               employee.id, day.date,self.rule.rule_counter))
                            slack_coeff = 0
                            vars = []
                            pay_durations = []
                            if not self.rule.is_mandatory:
                                slack_coeff = -1
                                maxHoursPerEmployeeDaySlackVar.obj = self.rule.penalty * domain.settings .rule_objective
                            for shift in shiftsToday:
                                if employee.is_eligible(shift) and shift.in_schedule(domain.settings .start, domain.settings .end):
                                    varText = VAR_DEFAULTS.assignment.id(employee, shift)
                                    shiftEmpVariable = solver.var_by_name(varText)
                                    if shiftEmpVariable:
                                        vars.append(shiftEmpVariable)
                                        pay_durations.append(int(shift.pay_duration))
                            solver.add_constr(xsum(vars[i] * pay_durations[i] for i in range(0, len(vars))) + slack_coeff*maxHoursPerEmployeeDaySlackVar <= int(self.rule.parameter1), name='maxHoursPerEmployeeDay_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        for day in domain.days:
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                if not self.rule.is_mandatory and self.rule.is_applicable(None, employee) and self.rule.is_applicable_day(day.date):
                    slack_var = solver.var_by_name('maxHoursPerEmployeeDaySlack_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=day.date))