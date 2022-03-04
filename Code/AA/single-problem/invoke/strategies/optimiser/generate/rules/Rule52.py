from datetime import datetime, timedelta
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule52:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        minFreeDays = self.rule.parameter1
        periodWeeks = self.rule.parameter2
        shifting_window_size = self.rule.parameter3
        parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2}
        shiftsSortedOnTime = sorted(domain.shifts, key=lambda x: x.start)
        for employee in domain.employees:
            if self.rule.is_applicable(None, employee):
                employeeShifts = [shift for shift in shiftsSortedOnTime if solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                freeSundayCount = 0

                for shift in employeeShifts:
                    shift.start_date = datetime.fromtimestamp(shift.start, domain.settings.time_zone)

                for index, day in enumerate(domain.days):
                    if (shifting_window_size > 0 and index / shifting_window_size % 1 == 0) and self.rule.is_applicable_day(day.date):
                        periodStart = day.date
                        periodEndTimeStamp = periodStart + periodWeeks * 7 * 24 * 60 * 60
                        periodEnd = datetime.fromtimestamp(periodEndTimeStamp, domain.settings.time_zone)
                        if self.rule.is_applicable_day(periodStart):
                            violationShifts = []

                            day_2 = datetime.fromtimestamp(periodStart, domain.settings.time_zone)
                            while day_2 <= periodEnd: # in range(periodStart, periodEnd, 86_400):
                                if day_2.weekday() == 6:
                                    day_shifts = []
                                    for shift in employeeShifts:
                                        if day_2 <= shift.start_date < day_2 + timedelta(days=1):
                                            day_shifts.append(shift)
                                    if len(day_shifts) == 0:
                                        freeSundayCount += 1
                                    else:
                                        violationShifts += day_shifts
                                day_2 += timedelta(days=1)
                            if freeSundayCount < minFreeDays and len(violationShifts) > 0:
                                # add violation
                                firstShift = violationShifts[0]
                                var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, firstShift))
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                        date=firstShift.start,
                                                        relevant_shifts=[shift.id for shift in
                                                                         violationShifts],
                                                        violation_description=generate_violation_text(minFreeDays, periodWeeks, str(day)),
                                                        parameters=parameters))
                            shiftCount = 0
                        freeSundayCount = 0

def generate_violation_text(minFreeDays, periodWeeks, startPeriod):
    return "Less than {} free sundays in the {} weeks starting on {}".format(minFreeDays, periodWeeks, startPeriod)