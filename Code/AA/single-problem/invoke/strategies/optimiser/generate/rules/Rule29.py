# Rule 29: Penalty breaking the maximum number of domain.shifts of a particular shift type
from datetime import timedelta
from mip import xsum
from config import configuration, constants
from strategies.optimiser.output import Violation
from lib.dt import parse_timestamp

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule29:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty != 0:
            shiftType = self.rule.parameter1
            maximumNumber = self.rule.parameter2
            period = self.rule.parameter3
            end_after = self.rule.parameter4
            checkFrequency = 1
            if self.rule.parameter5:
                checkFrequency = self.rule.parameter5

            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    for dayIndex, day in enumerate(domain.days):
                        if dayIndex / checkFrequency % 1 == 0 and self.rule.is_applicable_day(day.date):
                            slackVar = solver.add_var(lb=0, ub=100, name='maxShiftsOfTypeInPeriodSlack_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))
                            slackCoefficient = 0
                            vars = []
                            shiftsInPeriod = [shift for shift in domain.shifts if domain.days[dayIndex].date <= shift.start < domain.days[dayIndex].date + int(timedelta(days=period).total_seconds())]
                            for shift in shiftsInPeriod:
                                if shiftType in shift.shift_types and employee.is_eligible(shift) and (not end_after or (shift.end - shift.midnight_time_stamp)%(24*60*60) > end_after*60):
                                    varText = VAR_DEFAULTS.assignment.id(employee, shift)
                                    var = solver.var_by_name(varText)
                                    if var:
                                        vars.append(var)
                            if not self.rule.is_mandatory:
                                slackCoefficient = -1
                                # set the goal function for this alert
                                slackVar.obj = self.rule.penalty * domain.settings .rule_objective
                            solver.add_constr(xsum(vars) + slackCoefficient * slackVar <= maximumNumber, name='maxShiftsOfTypeInPeriod_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))


    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty != 0 and not self.rule.is_mandatory:
            shiftType = self.rule.parameter1
            maximumNumber = self.rule.parameter2
            period = self.rule.parameter3
            end_after = self.rule.parameter4
            checkFrequency = 1
            if self.rule.parameter5:
                checkFrequency = self.rule.parameter5

            parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2, "parameter_3": self.rule.parameter3}

            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    for dayIndex, day in enumerate(domain.days):
                        if dayIndex / checkFrequency % 1 == 0 and self.rule.is_applicable_day(day.date):
                            slack_var = solver.var_by_name('maxShiftsOfTypeInPeriodSlack_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                violationShifts = []
                                shiftsInPeriod = [shift for shift in domain.shifts if domain.days[dayIndex].date <= shift.start < domain.days[dayIndex].date + int(timedelta(days=period).total_seconds()) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                                for shift in shiftsInPeriod:
                                    if shiftType in shift.shift_types and employee.is_eligible(shift) and (shift.end - shift.midnight_time_stamp) % (24 * 60 * 60) > end_after * 60:
                                        violationShifts.append(shift)
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=domain.days[dayIndex].date,
                                                        relevant_shifts=[shift.id for shift in violationShifts],
                                                        violation_description=generate_violation_text(maximumNumber, shiftType, end_after, period, domain.days[dayIndex].date, domain.settings.end, domain.settings.time_zone),
                                                        parameters=parameters))

def generate_violation_text(maxNumber, shiftType, end_after, period, startPeriod, endPeriod, tz):
    startPeriod = min(endPeriod, startPeriod + timedelta(days=period).total_seconds()) - timedelta(days=period).total_seconds()
    if end_after:
        minutes = int(end_after % 60)
        hours = int(end_after / 60)
        return "More than {} shifts of type {} ending after {} in the period of {} weeks starting on {}".format(maxNumber, shiftType, f"{hours:02d}" + ":" + f"{minutes:02d}", int(period/7), int(startPeriod))
    else:
        return "More than {} shifts of type {} in the period of {} weeks starting on {}".format(maxNumber, shiftType, int(period / 7), parse_timestamp(startPeriod, tz).strftime(constants.time.date_format))