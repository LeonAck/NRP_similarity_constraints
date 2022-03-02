from datetime import datetime, timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule54:
    # Rule to ensure that if one shift type is assigned (parameter 1) another shift type (parameter 2) is assigned
    # X domain.days after it to the same person (parameter 3)
    # it gives a bonus when it assigns this (parameter 4)
    # it has a minimum of cases this needs to apply for (parameter 5)
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            shift_type_1 = self.rule.parameter1
            shift_type_2 = self.rule.parameter2
            days_between = int(self.rule.parameter3)
            bonus = int(self.rule.parameter4)
            minimum = int(self.rule.parameter5)

            for day in domain.days:
                combi_vars = []
                for employee in domain.employees:
                    shifts_on_day = [shift for shift in domain.shifts if day.date <= shift.start < day.date + 24*60*60 and employee.is_eligible(shift) and shift_type_1 in shift.shift_types]
                    shifts_next_period = [shift for shift in domain.shifts if day.date + days_between*24*60*60 <= shift.start < day.date + (days_between+1)*24*60*60 and employee.is_eligible(shift) and shift_type_2 in shift.shift_types]

                    if len(shifts_on_day) > 0 and len(shifts_next_period) > 0:
                        # we need to make a constraint that ensures the same shift type is done by the same employee
                        var_text_combi = 'v-{}-{}-{}-combi-var'.format(employee.id, str(day.date),self.rule.rule_counter)
                        combi_var = solver.add_var(lb=0, ub=10, var_type='I', name=var_text_combi)
                        combi_vars.append(combi_var)

                        vars_day_1 = []
                        vars_next_day = []
                        for shift_day_1 in shifts_on_day:
                            shift_day_1_text = '{}-{}-{}-{}-{}'.format(employee.id, str(shift_day_1.start), str(shift_day_1.end),
                                                              shift_day_1.department_id, shift_day_1.id)
                            shift_day_1_var = solver.var_by_name(shift_day_1_text)
                            if shift_day_1_var:
                                vars_day_1.append(shift_day_1_var)
                        for shift_next_day in shifts_next_period:
                            shift_next_day_text = '{}-{}-{}-{}-{}'.format(employee.id, str(shift_next_day.start),
                                                                       str(shift_next_day.end),
                                                                       shift_next_day.department_id, shift_next_day.id)
                            shift_next_day_var = solver.var_by_name(shift_next_day_text)
                            if shift_next_day_var:
                                vars_next_day.append(shift_next_day_var)
                        combi_var.obj = -bonus
                        solver.add_constr(xsum(vars_day_1) + xsum(vars_next_day) - 2*combi_var >= 0,
                                          name='{}-{}-{}-combi-constraint'.format(employee.id, str(day.date),self.rule.rule_counter))


                # creation of the constraint for the entire day. Checks whether there is at least combis equal to the minimum
                slack_coefficient = 0
                slack_variable_text = 's-{}-{}-combishifts'.format(str(day.date),self.rule.rule_counter)
                slack_variable = solver.add_var(lb=0, ub=100, var_type='I', name=slack_variable_text)
                if not self.rule.is_mandatory:
                    slack_coefficient = 1
                    slack_variable.obj = self.rule.penalty * domain.settings .rule_objective
                combi_constraint_name = 'c-{}-{}-combishifts'.format(str(day.date),self.rule.rule_counter)
                solver.add_constr(xsum(combi_vars) + slack_coefficient*slack_variable >= minimum, name=combi_constraint_name)



    def add_violation_to_output(self, solver, domain, output):
        # Rule to ensure that if one shift type is assigned (parameter 1) another shift type (parameter 2) is assigned
        if self.rule.penalty > 0:
            for day in domain.days:
                slack_variable_text = 's-{}-{}-combishifts'.format(str(day.date),self.rule.rule_counter)
                slack_var = solver.var_by_name(slack_variable_text)
                if slack_var and slack_var.x > 0:
                    output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                            violation_costs=slack_var.x * slack_var.obj,
                                            date=str(day)))
