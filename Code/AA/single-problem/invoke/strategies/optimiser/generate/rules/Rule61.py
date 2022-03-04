from datetime import datetime, timedelta
from mip import xsum
import pytz
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
# Rule 61 Do not violate maximum hours in period between time_1 and time_2

class Rule61:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # Rule 61 Do not violate maximum hours in period
        maximumWorkingMinutes = self.rule.parameter1
        starting_time_on_day = self.rule.parameter3
        ending_time_on_day = self.rule.parameter4
        shifting_window_size = self.rule.parameter5
        if self.rule.penalty > 0:
            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    constraintMade = False
                    payperiod_length = 7
                    if employee.payperiod_length and not self.rule.parameter2:
                        payperiod_length = employee.payperiod_length
                    elif self.rule.parameter2:
                        payperiod_length = self.rule.parameter2
                    for index, day in enumerate(domain.days):
                        if (index / payperiod_length % 1 == 0 or (shifting_window_size > 0 and index / shifting_window_size % 1 == 0)) and self.rule.is_applicable_day(day.date):
                            constraintMade = True
                            maximumHoursSlackVar = solver.add_var(name='maximHoursBetweenTimesSlackVar_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter), lb=0, ub=self.maxValue, var_type='C')
                            slackCoefficient = 0
                            vars = []
                            pay_durations_between_times = []
                            if not self.rule.is_mandatory:
                                slackCoefficient = -1
                                maximumHoursSlackVar.obj = self.rule.penalty * domain.settings .rule_objective
                            shiftsInPayperiod = [shift for shift in domain.shifts if day.date <= shift.start < day.date + int(timedelta(days=payperiod_length).total_seconds())]

                            for shift in shiftsInPayperiod:
                                if (not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)) and shift.in_schedule(domain.settings .start, domain.settings .end) \
                                        and self.rule.is_applicable(shift, employee):
                                    if employee.is_eligible(shift):
                                        varText = VAR_DEFAULTS.assignment.id(employee, shift)

                                        shiftEmpVariable = solver.var_by_name(varText)
                                        if shiftEmpVariable:
                                            vars.append(shiftEmpVariable)
                                            time_between_hours = determine_duration_between_times(shift.start, shift.end, starting_time_on_day, ending_time_on_day, self.rule)
                                            pay_durations_between_times.append(int(time_between_hours))
                            solver.add_constr(xsum(vars[i] * pay_durations_between_times[i] for i in range(0, len(vars))) + slackCoefficient * maximumHoursSlackVar <= (maximumWorkingMinutes), name='maximumMinutesBetweenTimesConstraint_{}_{}_{}_{}_{}_{}'.format(employee.id, day.date, self.rule.penalty, self.rule.parameter1, self.rule.parameter2,self.rule.rule_counter))

                    if not constraintMade:
                        print("No Constraint for Rule 61 was made for Employee {}, please check the start of the payperiod and make sure that it's midnight".format(employee.id))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2,
                          "parameter_3": self.rule.parameter3, "parameter_4": self.rule.parameter4,
                          "parameter_5": self.rule.parameter5, "parameter_6": self.rule.parameter6}
            starting_time_on_day = self.rule.parameter3
            ending_time_on_day = self.rule.parameter4
            shifting_window_size = self.rule.parameter5

            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    payperiod_length = 7
                    if employee.payperiod_length and not self.rule.parameter2:
                        payperiod_length = employee.payperiod_length
                    elif self.rule.parameter2:
                        payperiod_length = self.rule.parameter2
                    for index, day in enumerate(domain.days):
                        if (index / payperiod_length % 1 == 0 or (shifting_window_size > 0 and index / shifting_window_size % 1 == 0)) and self.rule.is_applicable_day(day.date):
                            slack_var = solver.var_by_name('maximHoursBetweenTimesSlackVar_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))
                            if slack_var and slack_var.x != 0:
                                violationShifts = [shift for shift in domain.shifts if day.date <= shift.start < day.date + int(timedelta(days=payperiod_length).total_seconds()) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs= slack_var.x * slack_var.obj,
                                                        date=day.date,
                                                        relevant_shifts=[shift.id for shift in
                                                                         violationShifts],
                                                        violation_description=generate_violation_text(self.rule.parameter1, payperiod_length, starting_time_on_day, ending_time_on_day, day.date),
                                                        parameters=parameters))

def determine_duration_between_times(shift_start, shift_end, window_start_time, window_end_time, rule):
    start_time_local = datetime.fromtimestamp(shift_start, tz=pytz.time_zone(rule.rule_time_zone))
    window_start = start_time_local.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() + 60 * window_start_time
    window_end = start_time_local.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() + 60 * window_end_time
    overlapHours = 0

    if window_start < shift_end and window_end > shift_start:
        overlapStart = window_start
        overlapEnd = window_end

        if window_start < shift_start:
            overlapStart = shift_start
        if window_end > shift_end:
            overlapEnd = shift_end
        overlapHours = int((overlapEnd - overlapStart) / (60))
    elif window_start + 24 * 60 * 60 < shift_end and window_end + 24 * 60 * 60 > shift_start:
        overlapStart = window_start + 24 * 60 * 60
        overlapEnd = window_end + 24 * 60 * 60

        if window_start + 24 * 60 * 60 < shift_start:
            overlapStart = shift_start
        if window_end + 24 * 60 * 60 > shift_end:
            overlapEnd = shift_end
        overlapHours = int((overlapEnd - overlapStart) / (60))
    return overlapHours



def generate_violation_text(maximumHours, periodLength, starting_time_on_day, ending_time_on_day, startDate):
    return "More than {} working hours between {} and {} starting on {} on day {}".format(maximumHours/60, periodLength, starting_time_on_day, ending_time_on_day, startDate)
