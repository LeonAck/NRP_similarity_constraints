from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from domain.day import Day
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule49:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # The weekend block rule per period (weekly/monthly/quarterly/yearly)
        # A weekend off is construed as free time during the hours from Saturday at midnight (0:00 a.m.) to Monday 11:00 a.m. (59 hours of freedom in total)
        if self.rule.penalty > 0:
            minFreeWeekends = int(self.rule.parameter1)
            periodToCheck = self.rule.parameter2 # number of months/weeks
            weeksNotMonths = self.rule.parameter3  # if True, the value of parameter2 is interpreted as weeks
            # freeMinutes = self.rule.parameter4  # total number of free minutes that is required directly after monday 00:00 a.m.
            freeMinutes = 11*60  # total number of free minutes that is required directly after monday 00:00 a.m.
            shifts_sorted_on_time = sorted(domain.shifts, key=lambda x: x.start)

            # find start and end of period to check
            startPeriod = datetime.utcfromtimestamp(domain.settings .start).replace(tzinfo=pytz.utc)
            startPeriod = startPeriod.replace(hour=0, minute=0)
            if not weeksNotMonths:
                startPeriod = startPeriod.replace(month=startPeriod.month - (startPeriod.month-1)%periodToCheck, day=1)
            else:
                startPeriod = startPeriod - timedelta(days=startPeriod.weekday())
            endPeriod = startPeriod + relativedelta(months=+periodToCheck)
            if weeksNotMonths:
                endPeriod = startPeriod + relativedelta(weeks=+periodToCheck)

            # create list of domain.days in period
            domain.daysPeriod = []
            dayTimeStamp = int(startPeriod.timestamp())
            while dayTimeStamp < endPeriod.timestamp():
                d = Day(dayTimeStamp)
                domain.daysPeriod.append(d)
                dayTimeStamp += int(timedelta(days=1).total_seconds())

            for employee in domain.employees:
                employeeShifts = [shift for shift in shifts_sorted_on_time if employee.is_eligible(shift)]
                freeWeekends = 0
                if not weeksNotMonths:
                    if periodToCheck == 3:
                        freeWeekends = employee.freeWeekendsQuarter
                    if periodToCheck == 1:
                        freeWeekends = employee.freeWeekendsMonth

                # iterate over domain.days of the week/month/quarter/year
                freeWeekendVars = []
                for day in domain.daysPeriod:
                    if day.date < domain.settings .start:
                        # do nothing, weekends in this period are included in the counter
                        continue

                    dayDatetime = datetime.utcfromtimestamp(day.date)
                    if dayDatetime.weekday() in [5]:
                        if day.date >= domain.settings .end:
                            # count weekend as free weekend
                            freeWeekends += 1
                            continue
                        else:
                            # create restVar for the period from Saturday at midnight (0:00 a.m.) to Monday 11:00 a.m.
                            restVarText = 'restVar_{}_{}'.format(employee.id, str(day.date))
                            restVar = solver.var_by_name(restVarText)
                            if not restVar:
                                restVar = solver.add_var(lb=0, ub=1, name=restVarText, var_type='B')
                            freeWeekendVars.append(restVar)

                            # make sure restVar can only be 1 if no overlap with worked shifts
                            endTimeRest = day.date + timedelta(days=2, minutes=freeMinutes).total_seconds()
                            overlappingShifts = [shift for shift in employeeShifts if shift.end > day.date and shift.start < endTimeRest]
                            vars = []
                            for shift in overlappingShifts:
                                shiftText = VAR_DEFAULTS.assignment.id(employee, shift)
                                shiftVar = solver.var_by_name(shiftText)
                                if shiftVar:
                                    vars.append(shiftVar)
                            solver.add_constr(0 <= xsum(vars) + restVar*len(overlappingShifts) <= len(overlappingShifts), name='restVarConstraint_{}_{}_{}'.format(employee.id, day.date,self.rule.rule_counter))

                # make minimum free weekends per period constraint
                if minFreeWeekends > freeWeekends:
                    minFreeWeekendsSlackVar = solver.add_var(lb=0, ub=minFreeWeekends, name='minFreeWeekendsSlackVar_{}_{}_{}'.format(employee.id, startPeriod.timestamp(),self.rule.rule_counter), var_type='I')
                    slackCoefficient = 0
                    if not self.rule.is_mandatory:
                        slackCoefficient = 1
                        minFreeWeekendsSlackVar.obj = self.rule.penalty * domain.settings .rule_objective
                    solver.add_constr(minFreeWeekends - freeWeekends <= xsum(freeWeekendVars) + slackCoefficient*minFreeWeekendsSlackVar, name='minimumFreeWeekendsConstraint_{}_{}_{}'.format(employee.id, startPeriod.timestamp(),self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        periodToCheck = self.rule.parameter2  # number of months/weeks
        weeksNotMonths = self.rule.parameter3

        # find start and end of period to check
        startPeriod = datetime.utcfromtimestamp(domain.settings .start).replace(tzinfo=pytz.utc)
        if not weeksNotMonths:
            startPeriod = startPeriod.replace(month=startPeriod.month - (startPeriod.month - 1) % periodToCheck, day=1)
        else:
            startPeriod = startPeriod - timedelta(days=startPeriod.weekday())

        for employee in domain.employees:
            slack_var = solver.var_by_name('minFreeWeekendsSlackVar_{}_{}_{}'.format(employee.id, startPeriod.timestamp(),self.rule.rule_counter))
            if slack_var and slack_var.x > 0:
               output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                        user_id=employee.id,
                                        violation_costs=slack_var.x * slack_var.obj,
                                        date=startPeriod.timestamp()))