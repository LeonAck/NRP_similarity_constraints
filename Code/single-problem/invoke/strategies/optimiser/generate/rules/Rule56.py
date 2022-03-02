from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule56:
    def __init__(self, rule):
        self.rule = rule

    # ensures a minimum of x free domain.days per period accounting for the free day definition after a shift of a certain type
    def set_rule(self, solver, domain):
        if self.rule.penalty >= 0:
            period = int(self.rule.parameter1)
            period_seconds = period * 24 * 60 * 60
            minimumFreeDays = int(self.rule.parameter2)
            lengthFreeDayAfterType = int(self.rule.parameter3) * 60 # the minimum rest time after a shift of the type for the rest period to count as a free day
            shiftTypeForRule = int(self.rule.parameter4)
            lengthFreeDay = 24 * 60 * 60
            restTimesAfterShiftType = [lengthFreeDayAfterType, lengthFreeDayAfterType + lengthFreeDay, lengthFreeDayAfterType + 2 * lengthFreeDay, lengthFreeDayAfterType + 3 * lengthFreeDay]
            penalty = self.rule.penalty
            for index in range(0, len(domain.days), period):
                period_start = domain.days[index].date
                period_end = domain.days[index+period-1].date + 24*60*60
                period_shifts = [shift for shift in domain.shifts if period_start <= shift.start < period_end]
                for employee in domain.employees:
                    employee_shifts = [shift for shift in period_shifts if employee.is_eligible(shift) or (shift.is_fixed and shift.employee_id == employee.id)]

                    # make rest period variables per shift of type and make sure that they do not overlap with assigned shifts
                    employeeShiftsOfType = [shift for shift in employee_shifts if shiftTypeForRule in shift.shift_types]
                    restVarsAfterShiftsOfType = {}
                    restVarsAfterShiftsOfTypeStartTimes = {}
                    for restTime in restTimesAfterShiftType:
                        restVarsAfterShiftsOfType[restTime] = []
                        restVarsAfterShiftsOfTypeStartTimes[restTime] = []
                        for shiftOfType in employeeShiftsOfType:
                            if not shiftOfType.end in restVarsAfterShiftsOfTypeStartTimes[restTime] and shiftOfType.end + restTime <= period_end:
                                shiftsAfterNightShift = [shift for shift in employee_shifts if shiftOfType.end <= shift.start < shiftOfType.end + restTime]
                                freeDayAfterType = solver.var_by_name('{}_{}_{}_{}_freeDayAfterType'.format(employee.id, str(shiftOfType.end), str(restTime),self.rule.rule_counter))
                                if not freeDayAfterType:
                                    freeDayAfterType = solver.add_var(lb=0, ub=1, name='{}_{}_{}_{}_freeDayAfterType'.format(employee.id, str(shiftOfType.end), str(restTime),self.rule.rule_counter), var_type='B')
                                shiftVars = []
                                for shift in shiftsAfterNightShift:
                                    shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                    if shiftVar:
                                        shiftVars.append(shiftVar)
                                freeDayAfterTypeConstraint = solver.add_constr(xsum(shiftVars) + 100*freeDayAfterType <= 100, name='{}_{}_{}_{}_{}_freeDayAfterTypeConstraint'.format(employee.id, str(shiftOfType.id), str(shiftOfType.end), str(restTime),self.rule.rule_counter))
                                restVarsAfterShiftsOfType[restTime].append(freeDayAfterType)
                                restVarsAfterShiftsOfTypeStartTimes[restTime].append(shiftOfType.end)

                    # make sure that only one of the freeDayAfterType variables can be chosen per shift of type
                    for shiftOfType in employeeShiftsOfType:
                        restVars = []
                        for restTime in restTimesAfterShiftType:
                            freeDayAfterType = solver.var_by_name('{}_{}_{}_{}_freeDayAfterType'.format(employee.id, str(shiftOfType.end), str(restTime),self.rule.rule_counter))
                            if freeDayAfterType:
                                restVars.append(freeDayAfterType)
                        chooseOneConstraint = solver.add_constr(xsum(restVars) <= 1, name='{}_{}_{}_{}_{}_chooseOne'.format(employee.id, str(shiftOfType.id), restTime, str(index),self.rule.rule_counter))

                    # make rest period variables per day and make sure they do not overlap with assigned shifts
                    restVars24h = []
                    for index2 in range(index, index + period):
                        day_start = domain.days[index2].date
                        day_end = day_start + 24 * 60 * 60
                        dayShifts = [shift for shift in employee_shifts if shift.start < day_end and shift.end > day_start + 1 * 60 * 60]
                        freeDay24h = solver.var_by_name('{}_{}_{}_freeDay24h'.format(employee.id, day_start,self.rule.rule_counter))
                        if not freeDay24h:
                            freeDay24h = solver.add_var(lb=0, ub=1, name='{}_{}_{}_freeDay24h'.format(employee.id, day_start,self.rule.rule_counter), var_type='B')
                        shiftVars = []
                        for shift in dayShifts:
                            shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                            if shiftVar:
                                shiftVars.append(shiftVar)
                        freeDay24hConstraint = solver.add_constr(xsum(shiftVars) + 100*freeDay24h <= 100, name='{}_{}_{}_freeDay24hConstraint'.format(employee.id, str(day_start),self.rule.rule_counter))
                        restVars24h.append(freeDay24h)

                        # make sure that the rest variables do not overlap with the rest after night shift variables
                        noOverlapVars = []
                        for restTime in restVarsAfterShiftsOfTypeStartTimes:
                            for startTime in restVarsAfterShiftsOfTypeStartTimes[restTime]:
                                if startTime < day_end and startTime+restTime > day_start:
                                    freeDayAfterType = solver.var_by_name('{}_{}_{}_{}_freeDayAfterType'.format(employee.id, str(startTime), str(restTime),self.rule.rule_counter))
                                    if freeDayAfterType:
                                        noOverlapVars.append(freeDayAfterType)
                        solver.add_constr(xsum(noOverlapVars)+freeDay24h <= 1, name='{}_{}_{}noOverlapConstraint56'.format(employee.id, day_start,self.rule.rule_counter))

                    # Create minimum rest domain.days constraint
                    vars = []
                    coefficients = []
                    for var in restVars24h:
                        vars.append(var)
                        coefficients.append(1)
                    freeDays = 0
                    for restTime in restVarsAfterShiftsOfType:
                        freeDays += 1
                        for var in restVarsAfterShiftsOfType[restTime]:
                            if var:
                                vars.append(var)
                                coefficients.append(freeDays)

                    # Add slack variable
                    minimumFreeDaysSlackVar = solver.add_var(name='{}_{}_{}_minimumFreeDaysSlackVar'.format(employee.id, str(period_start),self.rule.rule_counter), lb=0, ub=8, var_type='I')
                    slackCoefficient = 0
                    if not self.rule.is_mandatory:
                        slackCoefficient = 1
                        # set the goal function for this alert
                        minimumFreeDaysSlackVar.obj = self.rule.penalty * domain.settings .rule_objective

                    minimumFreeDaysConstraint = solver.add_constr(minimumFreeDays <= xsum(vars[i] * coefficients[i] for i in range(0, len(vars))) + slackCoefficient * minimumFreeDaysSlackVar, name='{}_{}_{}_minimumFreeDaysConstraint'.format(employee.id, str(period_start),self.rule.rule_counter))


    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty >= 0:
            period = int(self.rule.parameter1)
            minimumFreeDays = int(self.rule.parameter2)
            lengthFreeDayAfterType = int(self.rule.parameter3) * 60
            shiftTypeForRule = int(self.rule.parameter4)
            lengthFreeDay = 24 * 60 * 60
            restTimesAfterShiftType = [lengthFreeDayAfterType, lengthFreeDayAfterType + lengthFreeDay, lengthFreeDayAfterType + 2 * lengthFreeDay, lengthFreeDayAfterType + 3 * lengthFreeDay]

            for index in range(0, len(domain.days), period):
                period_start = domain.days[index].date
                period_end = domain.days[index + period - 1].date + 24 * 60 * 60
                for employee in domain.employees:
                    if not self.rule.is_mandatory:
                        slack_var = solver.var_by_name('{}_{}_{}_minimumFreeDaysSlackVar'.format(employee.id, str(period_start),self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                           output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=period_start))