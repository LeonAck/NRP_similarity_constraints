from datetime import datetime, timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule36:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # the weekend block rule per payperiod with lenght payperiod as parameter 3
        if self.rule.penalty > 0:
            if self.rule.parameter1:
                check_shift_types = True
                parameter = str(self.rule.parameter1)
            else:
                check_shift_types = False
            
                

            parameter2 = int(self.rule.parameter2)
            pay_period_length = int(self.rule.parameter3)

            # create variables for the entire pay period to see if there are domain.shifts of the specified shift type in the roster

            if self.rule.weekdays:
                weekdays_combination = self.rule.weekdays
            else:
                weekdays_combination = [5, 6]

            for employee in domain.employees:
                if employee.max_weekends:
                    parameter2 = employee.max_weekends

                if employee.payperiod_start:
                    pay_period_start = employee.payperiod_start
                    applicable_days = [day for day in domain.days if day.date >= pay_period_start]
                if self.rule.start_payperiod:
                    pay_period_start = self.rule.start_payperiod
                    applicable_days = [day for day in domain.days if day.date >= pay_period_start]
                if self.rule.is_applicable(None, employee):
                    firstWeekendDay = -1
                    for index, day in enumerate(applicable_days):
                        if index / pay_period_length % 1 == 0 and self.rule.is_applicable_day(day.date):
                            weekendVariables = []
                            for index2, day2 in enumerate(applicable_days):
                                if index <= index2 <= index + pay_period_length:
                                    if day2.weekday in weekdays_combination and (firstWeekendDay == -1 or firstWeekendDay != weekdays_combination[0]):
                                        firstWeekendDay = day2.weekday
                                        duration = 1
                                        if day2.weekday == weekdays_combination[0]:
                                            duration = 2
                                        
                                        chosenShifts = [shift for shift in domain.shifts if day2.date <= shift.start < day2.date + int(timedelta(days=duration).total_seconds()) and employee.is_eligible(shift)]
                    
                                        blockWorksVariable = solver.add_var(lb=0, ub=1, var_type='B', name='worksShiftTypeInBlock2_{}_{}_{}_{}'.format(employee.id, day.date, day2.date,self.rule.rule_counter))
                                        vars = []
                                        weekendVariables.append(blockWorksVariable)
                                        for chosenShift in chosenShifts:
                                            applyShift = False
                                            if chosenShift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable(chosenShift, employee) and not employee.is_fixed:

                                                if check_shift_types:
                                                    for st in chosenShift.shift_types:
                                                        if st == parameter:
                                                            applyShift = True
                                                else:
                                                    applyShift = True
                                                if applyShift:
                                                    varText = VAR_DEFAULTS.assignment.id(employee, chosenShift)
                                                    shift_emp_variable = solver.var_by_name(varText)
                                                    if shift_emp_variable:
                                                        vars.append(shift_emp_variable)
                                        solver.add_constr(-xsum(vars) + 1000*blockWorksVariable >= 0, name='worksShiftTypeInBlockConstraint2_{}_{}_{}_{}'.format(employee.id, day.date, day2.date,self.rule.rule_counter))
                                    else:
                                        firstWeekendDay = -1
                            if len(weekendVariables) > 0:
                                # this is where we create the constraint. We add the variables of the previous block + slack <= maximum number of items in the payperiod
                                maximumWeekendsSlackVariable = solver.add_var(lb=0, ub=self.maxValue, var_type='C',
                                                                             name='maximumNumberOfWeekendsSlack2_{}_{}_{}'.format(
                                                                                 employee.id, day.date,self.rule.rule_counter))
                                slack_coeff = 0
                                if not self.rule.is_mandatory:
                                    slack_coeff = -1
                                    maximumWeekendsSlackVariable.obj = 1 * self.rule.penalty * domain.settings .rule_objective
                                solver.add_constr(xsum(weekendVariables) + slack_coeff*maximumWeekendsSlackVariable <= parameter2, name='maximumNumberOfWeekends2_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        pay_period_length = int(self.rule.parameter3)
        for employee in domain.employees:
            applicable_days = domain.days
            if employee.payperiod_start:
                payperiod_start = employee.payperiod_start
                applicable_days = [day for day in domain.days if day.date >= payperiod_start]
            if self.rule.start_payperiod:
                payperiod_start = self.rule.start_payperiod
                applicable_days = [day for day in domain.days if day.date >= payperiod_start]
            for index, day in enumerate(applicable_days):
                if index / pay_period_length % 1 == 0 and self.rule.is_applicable_day(day.date):
                    slack_var = solver.var_by_name('maximumNumberOfWeekendsSlack2_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=day.date))
