# Rule 26: Penalty for having domain.shifts with a short break between them if there is a rest day
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule26:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        minHours = int(self.rule.parameter1)

        for employee in domain.employees:
            for dayIndex in range(0, len(domain.days)-2):
                day = domain.days[dayIndex]
                day2 = domain.days[dayIndex + 1]
                day3 = domain.days[dayIndex + 2]
                for shift1 in domain.shifts:
                    if shift1.start >= day.date and shift1.start < day.date + 24*60*60 and employee.is_eligible(shift1):
                        varS1 = solver.var_by_name(VAR_DEFAULTS.assignment.id(employee, shift1))
                        slack_coeff = 0
                        slack_var = solver.add_var(lb=0, ub=10, name='restAfterShiftSlack_{}_{}_{}'.format(employee.id, shift1.id,self.rule.rule_counter), var_type='B' )
                        vars_day2 = []
                        vars_day3 = []
                        if varS1:
                            for shift2 in domain.shifts:
                                if shift2.start >= day2.date and shift2.start < day2.date + 24*60*60 and employee.is_eligible(shift2):
                                    varS2 = solver.var_by_name(VAR_DEFAULTS.assignment.id(employee, shift2))
                                    if varS2:
                                        vars_day2.append(varS2)
                                if shift2.start >= day3.date and shift2.start < day3.date + 24*60*60 and employee.is_eligible(shift2) and (shift2.start - shift1.end) <= minHours*60*60:
                                    varS3 = solver.var_by_name(VAR_DEFAULTS.assignment.id(employee, shift2))
                                    if varS3:
                                        vars_day3.append(varS3)
                            if not self.rule.is_mandatory:
                                slack_coeff = -1
                                # set the goal function for this alert
                                slack_var.obj = self.rule.penalty * domain.settings .rule_objective
                            solver.add_constr(varS1 - xsum(vars_day2) + xsum(vars_day3) + slack_coeff*slack_var <= 1, name='restAfterShift_{}_{}_{}'.format(employee.id, shift1.id,self.rule.rule_counter))


    def add_violation_to_output(self, solver, domain, output):
        # consec shift types rule

        if self.rule.penalty > 0 and not self.rule.is_mandatory:
            for employee in domain.employees:
                for dayIndex in range(0, len(domain.days)-2):
                    day = domain.days[dayIndex]
                    for shift1 in domain.shifts:
                        if shift1.start >= day.date and shift1.start < day.date + 24*60*60 and employee.is_eligible(shift1):
                            slack_var = solver.var_by_name('restAfterShiftSlack_{}_{}_{}'.format(employee.id, shift1.id,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=shift1.start))

