from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
# Rule 64: Penalty breaking the minimum number of shifts of a particular shift type
class Rule64:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty != 0:
            shiftType = self.rule.parameter1
            minimumNumber = self.rule.parameter2
            period = self.rule.parameter3
            endAfter = self.rule.parameter4
            checkFrequency = 1
            if self.rule.parameter5:
                checkFrequency = self.rule.parameter5
            use_binary_penalty = True if self.rule.parameter6 == 1 else False


            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    for dayIndex, day in enumerate(domain.days):
                        if dayIndex / checkFrequency % 1 == 0 and self.rule.is_applicable_day(day.date):
                            if use_binary_penalty:
                                slackVar = solver.add_var(lb=0, ub=1, var_type='B', name='minShiftsOfTypeInPeriodSlack_{}_{}_{}'.format(employee.id, dayIndex, self.rule.rule_counter))
                            else:
                                slackVar = solver.add_var(lb=0, ub=minimumNumber, name='minShiftsOfTypeInPeriodSlack_{}_{}_{}'.format(employee.id, dayIndex, self.rule.rule_counter))

                            slackCoefficient = 0
                            vars = []
                            shiftsInPeriod = [shift for shift in domain.shifts if domain.days[dayIndex].date <= shift.start < domain.days[dayIndex].date + int(timedelta(days=period).total_seconds())]
                            for shift in shiftsInPeriod:
                                if shiftType in shift.shift_types and employee.is_eligible(shift) and (not endAfter or (shift.end - shift.midnightTimeStamp)%(24*60*60) > endAfter*60):
                                    var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                    if var:
                                        vars.append(var)
                            if not self.rule.is_mandatory:
                                slackCoefficient = minimumNumber if use_binary_penalty else 1
                                # set the goal function for this alert
                                slackVar.obj = self.rule.penalty * domain.settings.rule_objective
                            solver.add_constr(xsum(vars) + slackCoefficient * slackVar >= minimumNumber, name='minShiftsOfTypeInPeriod_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))


    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty != 0 and not self.rule.is_mandatory:
            shiftType = self.rule.parameter1
            minimumNumber = self.rule.parameter2
            period = self.rule.parameter3
            endAfter = self.rule.parameter4
            checkFrequency = 1
            if self.rule.parameter5:
                checkFrequency = self.rule.parameter5

            parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2, "parameter_3": self.rule.parameter3}

            for employee in domain.employees:
                if self.rule.is_applicable(None, employee):
                    for dayIndex, day in enumerate(domain.days):
                        if dayIndex / checkFrequency % 1 == 0 and self.rule.is_applicable_day(day.date):
                            slack_var = solver.var_by_name('minShiftsOfTypeInPeriodSlack_{}_{}_{}'.format(employee.id, dayIndex,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        date=day.date,
                                                        violation_description=generate_violation_text(minimumNumber, shiftType, endAfter, period, day.date, domain.settings.end),
                                                        parameters = parameters))

def generate_violation_text(minimum_number, shiftType, endAfter, period, startPeriod, endPeriod):
    startPeriod = min(endPeriod, startPeriod + timedelta(days=period).total_seconds()) - timedelta(days=period).total_seconds()
    if endAfter:
        minutes = int(endAfter % 60)
        hours = int(endAfter / 60)
        return "Less than {} shifts of type {} ending after {} in the period of {} weeks starting on {}".format(minimum_number, shiftType, f"{hours:02d}" + ":" + f"{minutes:02d}", int(period/7), int(startPeriod))
    else:
        return "Less than {} shifts of type {} in the period of {} weeks starting on {}".format(minimum_number, shiftType, int(period / 7), int(startPeriod))