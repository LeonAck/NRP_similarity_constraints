from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule12:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # Rule 12: Maximum number of employees per day
        for day in domain.days:
            if self.rule.is_applicable_day(day.date):
                maxEmployeesPerDaySlackVar = solver.add_var(lb=0, ub=self.maxValue,
                                                          name= 'maxEmployeesPerDaySlack_{}_{}'.format(day.date,
                                                                                                  self.rule.rule_counter), var_type='I')
                slack_coeff = 0
                vars = []
                if not self.rule.is_mandatory:
                    slack_coeff = -1
                    maxEmployeesPerDaySlackVar.obj = self.rule.penalty
                for employee in domain.employees.get_rule_applicable_employees(self.rule):
                    if self.rule.is_applicable(None, employee):
                        worksOnVariable = solver.find_variable(VAR_DEFAULTS.works_on.id(employee, day))
                        if worksOnVariable:
                            vars.append(worksOnVariable)
                solver.add_constr(xsum(vars) + slack_coeff*maxEmployeesPerDaySlackVar <= self.rule.parameter1, name='maxEmployeesPerDayConstraint_{}_{}'.format(day.date,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        for day in domain.days:
            if self.rule.is_applicable_day(day.date):
                slack_var = solver.var_by_name('maxEmployeesPerDaySlack_{}_{}'.format(day.date,self.rule.rule_counter))
                if slack_var and slack_var.x > 0 and slack_var.obj > 0:\
                    output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                            violation_costs=slack_var.x * slack_var.obj,
                                            date=day.date))
