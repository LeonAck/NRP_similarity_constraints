from config import configuration, constants
from strategies.optimiser.output import Violation
from lib.dt import parse_timestamp

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule42:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        # minimum parameter1 minutes rest per period of parameter2 minutes, but parameter3 times per period of parameter4 minutes the minimum minutes rest can be decreased to a minimum of parameter5 minutes
        if self.rule.penalty > 0:
            minimumRest = int(self.rule.parameter1)*60
            periodToIncludeRest = int(self.rule.parameter2)*60
            maxNrExceptions = int(self.rule.parameter3)
            minimumRestException = int(self.rule.parameter4)*60
            periodToCountExceptions = int(self.rule.parameter5)*60
            shiftsSortedOnTime = sorted(domain.shifts, key=lambda x: x.start)
            shift_type_to_exclude = self.rule.parameter6
            parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2, "parameter_3": self.rule.parameter3}

            for employee in domain.employees:
                employeeShifts = [shift for shift in shiftsSortedOnTime if solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0
                                  and shift_type_to_exclude not in shift.shift_types]

                for (shift_1_index, employee_shift_1) in enumerate(employeeShifts):
                    if self.rule.is_applicable_day(employee_shift_1.start):
                        shift_start_time = employee_shift_1.start
                        end_time_of_24_period = shift_start_time + periodToIncludeRest
                        largest_rest_time = 0
                        shifts_within_24_hours = [shift for shift in employeeShifts if shift_start_time <= shift.start < end_time_of_24_period]
                        for (shift_1_in_small_period_index, shift_1_in_small_period) in enumerate(shifts_within_24_hours):
                            shift_2_index = shift_1_in_small_period_index + 1
                            if len(shifts_within_24_hours) > shift_2_index:
                                shift_2 = shifts_within_24_hours[shift_2_index]
                                resting_period = shift_2.start - shift_1_in_small_period.end
                            else:
                                resting_period = end_time_of_24_period - shift_1_in_small_period.end
                            if resting_period > largest_rest_time:
                                largest_rest_time = resting_period

                        if len(shifts_within_24_hours) > 0 and largest_rest_time < minimumRestException:
                            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, employee_shift_1))
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                    date=employee_shift_1.midnight_time_stamp,
                                                    relevant_shifts=[shift.id for shift in shifts_within_24_hours],
                                                    violation_description=generate_violation_text(minimumRestException, periodToIncludeRest, employee_shift_1.start, end_time_of_24_period),
                                                    parameters=parameters))
                        elif len(shifts_within_24_hours) > 0 and maxNrExceptions == 0 and largest_rest_time < minimumRest:
                            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, employee_shift_1))
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                    date=employee_shift_1.midnight_time_stamp,
                                                    relevant_shifts=[shift.id for shift in shifts_within_24_hours],
                                                    violation_description=generate_violation_text(minimumRestException, periodToIncludeRest, employee_shift_1.start, end_time_of_24_period),
                                                    parameters=parameters))
                        elif largest_rest_time < minimumRest and maxNrExceptions > 0:
                            # Now check if it only happen once per 7 domain.days
                            number_of_exceptions = 0
                            minimum_rest_violation_shifts = []
                            for i in range(0, 7):
                                largest_rest_time = 0
                                shifts_within_24_hours = [shift for shift in employeeShifts if shift_start_time + (i * 86_400) <= shift.start < end_time_of_24_period + (i * 86_400)]
                                for (shift_1_in_small_period_index, shift_1_in_small_period) in enumerate(shifts_within_24_hours):
                                    if shift_1_in_small_period_index == 0:
                                        resting_period = shift_1_in_small_period.start - (shift_start_time + (i * 86_400))
                                    if resting_period > largest_rest_time:
                                        largest_rest_time = resting_period
                                    shift_2_index = shift_1_in_small_period_index + 1
                                    if len(shifts_within_24_hours) > shift_2_index:
                                        shift_2 = shifts_within_24_hours[shift_2_index]
                                        resting_period = shift_2.start - shift_1_in_small_period.end
                                    else:
                                        resting_period = end_time_of_24_period + (i * 86_400) - shift_1_in_small_period.end
                                    if resting_period > largest_rest_time:
                                        largest_rest_time = resting_period
                                if len(shifts_within_24_hours) > 0 and minimumRestException <= largest_rest_time < minimumRest:
                                    number_of_exceptions += 1
                                    minimum_rest_violation_shifts += shifts_within_24_hours

                            if number_of_exceptions > maxNrExceptions:
                                var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, employee_shift_1))
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                        date=employee_shift_1.midnight_time_stamp,
                                                        relevant_shifts=[shift.id for shift in minimum_rest_violation_shifts],
                                                        violation_description=generate_violation_text(minimumRest, periodToCountExceptions, employee_shift_1.start_datetime_str, parse_timestamp(end_time_of_24_period + (i * 86_400), domain.settings.time_zone).strftime(constants.time.date_format)),
                                                        parameters=parameters))

def generate_violation_text(minimumRest, periodLength, periodStart, periodEnd, nrExceptions = None):
    if nrExceptions:
        return "More than {} times less than {} hours rest in the period of {} hours starting on {} and ending on {}".format(nrExceptions, minimumRest/(60*60), periodLength/(60*60), periodStart, periodEnd)
    else:
        return "Less than {} hours rest in the period of {} hours starting on {} and ending on {}".format(minimumRest/(60*60), periodLength/(60*60), periodStart, periodEnd)