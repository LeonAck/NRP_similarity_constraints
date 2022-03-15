# Rule 70: Do not violate minimum hours in period
from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables


class Rule70:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # Rule 70: Do not violate minimum hours in period
        minimumWorkingMinutes = self.rule.parameter1
        shiftTypeForRule = self.rule.parameter4
        usePrevHours = self.rule.parameter5
        if self.rule.penalty > 0:
            for employee in domain.employees:
                previousMinutes = 0
                if usePrevHours:
                    previousMinutes = employee.previous_hours*60
                if self.rule.is_applicable(None, employee):
                    constraintMade = False
                    payperiod_length = 7
                    if employee.payperiod_length and not self.rule.parameter2:
                        payperiod_length = employee.payperiod_length
                    elif self.rule.parameter2:
                        payperiod_length = self.rule.parameter2
                    shifting_window_size = self.rule.parameter6 if self.rule.parameter6 else payperiod_length
                    for day in domain.days.get_start_days_for_steps(shifting_window_size, self.rule.period_start, self.rule.period_end).get_rule_applicable_days(self.rule):
                        if self.rule.period_end:
                            end_period = min(day.date + int(timedelta(days=payperiod_length).total_seconds()), self.rule.period_end)
                        else:
                            end_period = day.date + int(timedelta(days=payperiod_length).total_seconds())
                        constraintMade = True
                        minimumHoursSlackVar = solver.add_var(name='minimumHoursSlackVar_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter), lb=0, ub=self.maxValue, var_type='C')
                        slackCoefficient = 0
                        vars = []
                        pay_durations = []
                        vars2 = []
                        coefficients = []
                        if not self.rule.is_mandatory:
                            slackCoefficient = 1
                            minimumHoursSlackVar.obj = self.rule.penalty * domain.settings.rule_objective

                        unavailability_durations = employee.get_payduration_unavailabilities(day.date, end_period)

                        shiftsInPayperiod = [shift for shift in domain.shifts if day.date <= shift.start < end_period]

                        for shift in shiftsInPayperiod:
                            if (not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)) and shift.in_schedule(domain.settings .start, domain.settings .end) \
                                    and self.rule.is_applicable(shift, employee):
                                if employee.is_eligible(shift):
                                    varText = VAR_DEFAULTS.assignment.id(employee, shift)

                                    shiftEmpVariable = solver.var_by_name(varText)
                                    if shiftEmpVariable:
                                        vars.append(shiftEmpVariable)
                                        pay_durations.append(int(shift.pay_duration))
                                        if shiftTypeForRule and shiftTypeForRule in shift.shift_types:
                                            vars2.append(shiftEmpVariable)
                                            coefficients.append(1)
                        solver.add_constr(xsum(vars[i] * pay_durations[i] for i in range(0, len(vars))) + slackCoefficient * minimumHoursSlackVar >= (minimumWorkingMinutes - previousMinutes - unavailability_durations), name='minimumMinutesConstraint_{}_{}_{}_{}_{}_{}'.format(employee.id, day.date, self.rule.penalty, self.rule.parameter1, self.rule.parameter2,self.rule.rule_counter))

                    if not constraintMade:
                        print("No Constraint for Rule 70 was made for Employee {}, please check the start of the payperiod and make sure that it's midnight".format(employee.id))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2,
                          "parameter_3": self.rule.parameter3, "parameter_4": self.rule.parameter4,
                          "parameter_5": self.rule.parameter5, "parameter_6": self.rule.parameter6}

            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    payperiod_length = 7
                    if employee.payperiod_length and not self.rule.parameter2:
                        payperiod_length = employee.payperiod_length
                    elif self.rule.parameter2:
                        payperiod_length = self.rule.parameter2
                    shifting_window_size = self.rule.parameter6 if self.rule.parameter6 else payperiod_length
                    for day in domain.days.get_start_days_for_steps(shifting_window_size, self.rule.period_start, self.rule.period_end).get_rule_applicable_days(self.rule):
                        slack_var = solver.var_by_name('minimumHoursSlackVar_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))
                        if slack_var and slack_var.x != 0:
                            violationShifts = [shift for shift in domain.shifts if day.date <= shift.start < day.date + int(timedelta(days=payperiod_length).total_seconds()) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=day.date,
                                                    relevant_shifts=[shift.id for shift in violationShifts],
                                                    violation_description=generate_violation_text(self.rule.parameter1, payperiod_length, str(day)),
                                                    parameters=parameters))

def generate_violation_text(minimum_hours, periodLength, startDate):
    return "Less than {} working hours in the period of {} days starting on {}".format(minimum_hours/60, periodLength, startDate)
