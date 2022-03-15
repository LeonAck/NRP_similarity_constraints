from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule44:
    def __init__(self, rule):
        self.rule = rule
    # Rule 44: Penalty for working shift of type without shift of same type before or after

    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            shiftType = int(self.rule.parameter1)
            for employee in domain.employees:
                for dayIndex in range(0, len(domain.days)-2):
                    slack_var = solver.add_var(lb=0, ub=10, var_type='I', name='sameTypesSlack_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))
                    slack_coeff = 0
                    varS1s = []
                    varS2s = []
                    varS3s = []

                    for shift in domain.shifts:
                        if shiftType in shift.shift_types:
                            if domain.days[dayIndex].date <= shift.start < domain.days[dayIndex + 1].date and employee.is_eligible(shift):
                                varS1 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if varS1:
                                    varS1s.append(varS1)
                            if domain.days[dayIndex + 1].date <= shift.start < domain.days[dayIndex + 2].date and employee.is_eligible(shift):
                                varS2 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if varS2:
                                    varS2s.append(varS2)
                            if dayIndex + 3 < len(domain.days):
                                day3_end = domain.days[dayIndex + 3].date
                            else:
                                day3_end = domain.settings .end
                            if domain.days[dayIndex + 2].date <= shift.start < day3_end and employee.is_eligible(shift):
                                varS3 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if varS3:
                                    varS3s.append(varS3)
                    if not self.rule.is_mandatory:
                        slack_coeff = -1
                        # set the goal function for this alert
                        slack_var.obj = int(self.rule.penalty * domain.settings .rule_objective)
                    solver.add_constr(-xsum(varS1s) + xsum(varS2s) -xsum(varS3s) + slack_coeff*slack_var >= 0, name='sameTypesConstraint_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0 and not self.rule.is_mandatory:
            for employee in domain.employees:
                for dayIndex in range(0, len(domain.days)-2):
                    slack_var = solver.var_by_name('sameTypesConstraint_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=domain.days[dayIndex].date))