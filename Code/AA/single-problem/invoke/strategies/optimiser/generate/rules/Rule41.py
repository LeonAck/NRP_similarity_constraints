from datetime import datetime,timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule41:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # Rule 41: Assign the weekend domain.shifts based on the maximum contract hours
        ft_minutes = int(self.rule.parameter1)
        ft_max_weekend_minutes = int(self.rule.parameter2)
        if self.rule.parameter3:
            use_input_payperiod = True
            payperiod_length = int(self.rule.parameter3)
        else:
            use_input_payperiod = False


        if self.rule.penalty != 0:
            for employee in domain.employees:
                if employee.payperiod_minutes_max > 0 and self.rule.is_applicable(None, employee):
                    if not use_input_payperiod:
                        payperiod_length = 28
                    for index, day in enumerate(domain.days):
                        if index / payperiod_length % 1 == 0:
                            shiftsInPayperiod = [shift for shift in domain.shifts if day.date <= shift.start < day.date + int(timedelta(days=payperiod_length).total_seconds()) and employee.is_eligible(shift)]
                            if len(shiftsInPayperiod) > 0:
                                discount_factor = (ft_max_weekend_minutes/ft_minutes)*(employee.payperiod_minutes_max/ft_minutes)
                                maximum_weekend_minutes = discount_factor * employee.payperiod_minutes_max
                                # c_max_weekend_hours = solver.Constraint(0, maximum_weekend_minutes, '{}-{}-{}-weekendHoursConstraint'.format(employee.id, day.date,self.rule.rule_counter))
                                slackVar = solver.add_var(lb=0, ub=self.maxValue, name='weekendHoursSlackVar_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter), var_type='C')
                                slackCoefficient = 0
                                vars = []
                                pay_durations = []
                                for shift in shiftsInPayperiod:
                                    dt_start_shift = datetime.utcfromtimestamp(shift.start)
                                    if dt_start_shift.weekday() in [5, 6]:
                                        if (not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)) and shift.in_schedule(domain.settings .start, domain.settings .end) \
                                            and self.rule.is_applicable(shift, employee):
                                            varText = VAR_DEFAULTS.assignment.id(employee, shift)

                                            shiftEmpVariable = solver.var_by_name(varText)
                                            if shiftEmpVariable:
                                                vars.append(shiftEmpVariable)
                                                pay_durations.append(int(shift.pay_duration))
                                                # c_max_weekend_hours.SetCoefficient(shiftEmpVariable, int(shift.pay_duration))

                                if not self.rule.is_mandatory:
                                    # weekendHoursSlackVar = solver.IntVar(0, self.maxValue, '{}-{}-{}-weekendHoursSlackVar'.format(employee.id, day.date,self.rule.rule_counter))
                                    # c_max_weekend_hours.SetCoefficient(weekendHoursSlackVar, -1)
                                    slackCoefficient = -1
                                    slackVar.obj = self.rule.penalty * domain.settings .rule_objective
                                solver.add_constr(xsum(vars[i]*pay_durations[i] for i in range(0, len(vars))) + slackVar*slackCoefficient <= maximum_weekend_minutes, name='{}-{}-{}-weekendHoursConstraint'.format(employee.id, day.date,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        # max contract hours
        if self.rule.parameter1:
            use_input_payperiod = True
            payperiod_length = int(self.rule.parameter2)
        else:
            use_input_payperiod = False

        if self.rule.penalty != 0:
            for employee in domain.employees:
                if employee.payperiod_minutes_max > 0 and self.rule.is_applicable(None, employee):
                    if not use_input_payperiod:
                        payperiod_length = 28
                    for index, day in enumerate(domain.days):
                        if index / payperiod_length % 1 == 0:
                            slack_var = solver.var_by_name('weekendHoursSlackVar_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))
                            if slack_var and slack_var.x != 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=day.date))
