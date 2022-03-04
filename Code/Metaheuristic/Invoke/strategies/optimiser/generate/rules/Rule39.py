from datetime import datetime,timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 39: Set desired shift type after a day-off
class Rule39:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty != 0:
            desired_shiftType = self.rule.parameter1
            for employee in domain.employees:
                for day in domain.days[:-1]:
                    for shift1 in domain.shifts:
                        if day.date + int(timedelta(days=1).total_seconds()) <= shift1.start < day.date + int(timedelta(days=2).total_seconds()) and employee.is_eligible(shift1) and not desired_shiftType in shift1.shift_types:
                            shifts_on_day = [shift for shift in domain.shifts if day.date <= shift.start < day.date + int(timedelta(days=1).total_seconds()) and employee.is_eligible(shift)]
                            slackVar = solver.add_var(lb=0, ub=1, name='desiredShiftTypeAfterSlack_{}_{}_{}_{}'.format(employee.id, shift1.id, desired_shiftType, self.rule.rule_counter), var_type='B')
                            slackCoefficient = 0
                            varS2s = []

                            varText = VAR_DEFAULTS.assignment.id(employee, shift1)
                            varS1 = solver.var_by_name(varText)

                            for shift2 in shifts_on_day:
                                varText = VAR_DEFAULTS.assignment.id(employee, shift2)
                                varS2 = solver.var_by_name(varText)
                                if varS2:
                                    varS2s.append(varS2)

                            if not self.rule.is_mandatory:
                                slackCoefficient = 1
                            # set the goal function for this alert
                                slackVar.obj = self.rule.penalty * domain.settings .rule_objective
                            solver.add_constr(-varS1 + xsum(varS2s) + slackCoefficient*slackVar >= 0, name='desiredShiftTypeAfter_{}_{}_{}_{}'.format(employee.id, shift1.id, desired_shiftType, self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty != 0 and not self.rule.is_mandatory:
            desired_shiftType = self.rule.parameter1
            for employee in domain.employees:
                for day in domain.days[:-1]:
                    for shift1 in domain.shifts:
                        if day.date + int(timedelta(days=1).total_seconds()) <= shift1.start < day.date + int(timedelta(days=2).total_seconds()) and employee.is_eligible(shift1) and not desired_shiftType in shift1.shift_types:
                            slack_var = solver.var_by_name('desiredShiftTypeAfterSlack_{}_{}_{}_{}'.format(employee.id, shift1.id, desired_shiftType, self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=day.date))

