from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule24:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # number of domain.days consecutive off per Y domain.days
        numberOfDays = int(self.rule.parameter1)
        period = int(self.rule.parameter2)
        penalty = self.rule.penalty
        if penalty > 0:
            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    for dayIndex in range(0, len(domain.days) - numberOfDays):
                        workVar = solver.add_var(lb=0, ub=1, var_type='B', name='hasShiftsInPeriod_{}_{}_{}'.format(employee.id, domain.days[dayIndex].date,self.rule.rule_counter))
                        vars = []
                        for dayIndex2 in range(dayIndex, dayIndex + numberOfDays):
                            shiftsToday = [shift for shift in domain.shifts if shift.start >= domain.days[dayIndex2].date and shift.start < domain.days[dayIndex2].date + int(timedelta(days=1).total_seconds())]
                            for shift in shiftsToday:
                                if employee.is_eligible(shift) and shift.in_schedule(domain.settings .start, domain.settings .end):
                                    shiftText = VAR_DEFAULTS.assignment.id(employee, shift)
                                    shiftEmployeeVariable = solver.var_by_name(shiftText)
                                    if shiftEmployeeVariable:
                                        vars.append(shiftEmployeeVariable)

                        solver.add_constr(xsum(vars) -1000 * workVar <= 0, name='worksInPeriod_{}_{}_{}'.format(employee.id, domain.days[dayIndex].date,self.rule.rule_counter))

                    for dayIndex in range(0, len(domain.days)):
                        if dayIndex + period < len(domain.days):
                            slackVar = solver.add_var(lb=0, ub=1, var_type='B', name='restPeriodSlackVar_{}_{}_{}'.format(employee.id,
                                                                                                domain.days[dayIndex].date,
                                                                                                self.rule.rule_counter))
                            vars = []
                            slack_coeff = 0
                            for dayIndex2 in range(dayIndex, min(dayIndex + period - 1, len(domain.days))):
                                workVar = solver.var_by_name('hasShiftsInPeriod_{}_{}_{}'.format(employee.id, domain.days[dayIndex2].date,self.rule.rule_counter))
                                if workVar:
                                    vars.append(workVar)
                            if not self.rule.is_mandatory:
                                slack_coeff = -1
                                slackVar.obj = penalty * domain.settings .rule_objective
                            solver.add_constr(xsum(vars) + slack_coeff * slackVar <= period - 2, name='hasRestPeriod_{}_{}_{}'.format(employee.id, domain.days[dayIndex].date,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        # number of domain.days of consecutive per X hours per Y domain.days
        period = int(self.rule.parameter2)
        numberOfDays = int(self.rule.parameter1)

        for employee in domain.employees:
            if self.rule.is_applicable(None, employee):
                for dayIndex in range(0, len(domain.days)):
                    if dayIndex + numberOfDays < len(domain.days):
                        if not self.rule.is_mandatory:

                            slack_var = solver.var_by_name('restPeriodSlackVar_{}_{}_{}'.format(employee.id, domain.days[dayIndex].date,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=domain.days[dayIndex].date))
