from datetime import datetime, timedelta
import pytz
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule53:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        # Do not work on both weekday 1 and weekday 2 of the same week
        weekday1 = int(self.rule.parameter1)  # number between 0 and 6, 0 = monday
        weekday2 = int(self.rule.parameter2)
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            if self.rule.is_applicable(None, employee):
                employeeShifts = [shift for shift in domain.shifts if solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                for day_index_1, day_1 in enumerate(domain.days):
                    if self.rule.is_applicable_day(day_1.date):
                        work_days = 0
                        violation_shifts = []
                        day_1_datetime = datetime.fromtimestamp(day_1.date, tz=pytz.time_zone(domain.settings .time_zone))
                        if day_1_datetime.weekday() == weekday1:
                            day_1_shifts = [shift for shift in employeeShifts if day_1.date <= shift.start < int((day_1_datetime + timedelta(days=1)).timestamp())]
                            if len(day_1_shifts) > 0:
                                violation_shifts += day_1_shifts
                                work_days += 1
                            if day_index_1 < len(domain.days) - 1:
                                day_index_2 = day_index_1 + 1
                                day_2 = domain.days[day_index_2]
                                day_2_datetime = datetime.fromtimestamp(day_2.date, tz=pytz.time_zone(domain.settings .time_zone))
                                day_2_shifts = [shift for shift in employeeShifts if day_2.date <= shift.start < int((day_2_datetime + timedelta(days=1)).timestamp())]
                                if len(day_2_shifts) > 0:
                                    violation_shifts += day_2_shifts
                                    work_days += 1
                            if work_days == 2:
                                # add violation
                                firstShift = violation_shifts[0]
                                var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, firstShift))
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                        date=firstShift.start,
                                                        relevant_shifts=[shift.id for shift in
                                                                         violation_shifts],
                                                        violation_description=generate_violation_text(weekday1, weekday2, str(day_1))))

def generate_violation_text(weekday1, weekday2, startPeriod):
    import calendar
    return "Working on {} and {} of the same week, starting on {}".format(calendar.day_name[weekday1], calendar.day_name[weekday2], startPeriod)