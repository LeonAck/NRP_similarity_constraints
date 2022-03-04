from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule50:
    def __init__(self, rule):
        self.rule = rule

    # Rule 50: Penalty for working shift of type without shift of same type before or after
    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            shift_type = int(self.rule.parameter1)
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                for day_index in range(0, len(domain.days)-2):
                    var_list_1, var_list_2, var_list_3 = [], [], []
                    for shift in domain.shifts:
                        if shift_type in shift.shift_types:
                            if domain.days[day_index].date <= shift.start < domain.days[day_index + 1].date and employee.is_eligible(shift):
                                var_s1 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if var_s1:
                                    var_list_1.append(var_s1)
                            if domain.days[day_index + 1].date <= shift.start < domain.days[day_index + 2].date and employee.is_eligible(shift):
                                var_s2 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if var_s2:
                                    var_list_2.append(var_s2)
                            if day_index + 3 < len(domain.days):
                                day3_end = domain.days[day_index + 3].date
                            else:
                                day3_end = domain.settings .end
                            if domain.days[day_index + 2].date <= shift.start < day3_end and employee.is_eligible(shift):
                                var_s3 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if var_s3:
                                    var_list_3.append(var_s3)
                    slack_coeff = 0
                    slackvar = solver.add_var(name='sameTypesSlack_{}_{}_{}'.format(employee.id, day_index,self.rule.rule_counter),
                                              var_type="I", lb=0, ub=10)
                    if not self.rule.is_mandatory:
                        slack_coeff = -1
                        # set the goal function for this alert
                        slackvar.obj = int(self.rule.penalty * domain.settings .rule_objective)
                    s = solver.add_constr(-xsum(var_list_1) + xsum(var_list_2) - xsum(var_list_3) + slack_coeff * slackvar <= 0,
                                          'sameTypesConstraint_{}_{}_{}'.format(employee.id, day_index,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0 and not self.rule.is_mandatory:
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                for day_index in range(0, len(domain.days)-2):
                    slack_var = solver.var_by_name('sameTypesSlack_{}_{}_{}'.format(employee.id, day_index,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=domain.days[day_index].date))