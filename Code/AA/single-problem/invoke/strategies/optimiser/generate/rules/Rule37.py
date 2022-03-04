from datetime import timedelta
from mip import xsum
from config import configuration
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 37: Maximum number of special domain.days
class Rule37:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        maxDays = int(self.rule.parameter1)

        if self.rule.parameter2:
            payperiod_length = self.rule.parameter2
        else:
            payperiod_length = len(domain.days)

        if self.rule.penalty > 0:

            for employee in domain.employees:
                if not employee.is_fixed and self.rule.is_applicable(None, employee):
                    for index, day in enumerate(domain.days):
                        if index / payperiod_length % 1 == 0:
                            slack_coeff = 0
                            maxDaysSlack = solver.add_var(lb=0, ub=1000, var_type='I', name='max_special_days_slack_{}_{}'.format(employee.id, maxDays, day.date, self.rule.rule_counter))
                            vars = []

                            for special_day in self.rule.special_days:
                                if day.date <= special_day.date <= day.date + int(timedelta(days=payperiod_length).total_seconds()):
                                    worksOnVariable = solver.find_variable(VAR_DEFAULTS.works_on.id(employee, special_day))
                                    if worksOnVariable:
                                        vars.append(worksOnVariable)

                            if not self.rule.is_mandatory:
                                maxDaysSlack.obj = self.rule.penalty * domain.settings .rule_objective
                            solver.add_constr(xsum(vars) + slack_coeff * maxDaysSlack <= maxDays, name='max_special_days_{}_{}'.format(employee.id, maxDays, day.date,self.rule.rule_counter))

    
    def add_violation_to_output(self, solver, domain, output):
        maxDays = int(self.rule.parameter1)
        for employee in domain.employees:
            if self.rule.penalty > 0 and not employee.is_fixed and self.rule.is_applicable(None, employee):
                if not self.rule.is_mandatory:
                    for index, day in enumerate(domain.days):
                        slack_var = solver.var_by_name(name='max_special_days_slack_{}_{}'.format(employee.id, maxDays, day.date, self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=day.date))
