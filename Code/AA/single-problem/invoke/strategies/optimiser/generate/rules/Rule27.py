# Rule 27: Penalty for having rest - work - rest
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule27:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            for employee in domain.employees:
                for dayIndex in range(0, len(domain.days)-2):
                    slackVar = solver.add_var(name='offWorkOffSlack_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter), lb=0, ub=10)
                    slackVarCoefficient = 0
                    # s = solver.Constraint(-1000, 0, '{}-{}-{}-offWorkOffConstraint'.format(employee.id, dayIndex,self.rule.rule_counter))
                    day = domain.days[dayIndex]
                    day2 = domain.days[dayIndex + 1]
                    day3 = domain.days[dayIndex + 2]
                    varS1s = []
                    varS2s = []
                    varS3s = []
                    for shift1 in domain.shifts:
                        if shift1.start >= day.date and shift1.start < day.date + 24*60*60 and employee.is_eligible(shift1):
                            varS1 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift1))
                            if varS1:
                                varS1s.append(varS1)
                        if shift1.start >= day2.date and shift1.start < day2.date + 24*60*60 and employee.is_eligible(shift1):
                            varS2 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift1))
                            if varS2:
                                varS2s.append(varS2)
                        if shift1.start >= day3.date and shift1.start < day3.date + 24*60*60 and employee.is_eligible(shift1):
                            varS3 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift1))
                            # s.SetCoefficient(varS2, -1)
                            if varS3:
                                varS3s.append(varS3)
                    if not self.rule.is_mandatory:
                        # s.SetCoefficient(var, -1)
                        slackVarCoefficient = -1
                        # set the goal function for this alert
                        slackVar.obj = self.rule.penalty * domain.settings .rule_objective
                    solver.add_constr(-xsum(varS1s) + xsum(varS2s) - xsum(varS3s) + slackVarCoefficient *slackVar <= 0, name='offWorkOffConstraint_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))



    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0 and not self.rule.is_mandatory:
            for employee in domain.employees:
                for dayIndex in range(0, len(domain.days)-2):
                    slack_var = solver.var_by_name('offWorkOffSlack_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=domain.days[dayIndex].date))

