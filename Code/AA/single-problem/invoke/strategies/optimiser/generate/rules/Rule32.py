import json
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule32:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # minimum resting period in minutes per period in domain.days

        if self.rule.penalty > 0:
            period = int(self.rule.parameter1) * 24 * 60
            minimumRestingPeriod = int(self.rule.parameter2)
            penalty = self.rule.penalty

            # make rest period variables and make sure they do not overlap with assigned shifts
            for employee in domain.employees:
                employee_shifts = [shift for shift in domain.shifts if employee.is_eligible(shift)]
                day_begin = domain.days[0].date
                day_end = domain.settings .end
                end_day_end = day_end +24*60*60

                stepLength = 60 * 60
                # employee_shifts_times = [shift.start for shift in employee_shifts] + [shift.end for shift in employee_shifts]
                # for time in employee_shifts_times:
                #     if time%(60*60) == int(0.25*60*60):
                #         stepLength = int(0.25 * 60 * 60)
                #         break
                #     elif time%(60*60) == int(0.5*60*60):
                #         stepLength = int(0.5 * 60 * 60)
                hoursVars= []
                for timeBucket in range(day_begin, end_day_end - minimumRestingPeriod*60 + 1, stepLength):
                    shiftsEndInPrevBucket = [shift for shift in employee_shifts if shift.end > day_begin and timeBucket-stepLength < shift.end <= timeBucket]
                    if timeBucket == day_begin or len(shiftsEndInPrevBucket) > 0:
                        hoursVars.append(timeBucket)
                        overlappingShifts = [shift for shift in employee_shifts if shift.end > timeBucket and shift.start < timeBucket + minimumRestingPeriod * 60]
                        if len(overlappingShifts) > 0:
                            restingPeriodShiftVar = solver.add_var(lb=0, ub=1, var_type='I', name='restingPeriodShiftVar_{}_{}_{}_{}'.format(employee.id, timeBucket, minimumRestingPeriod,self.rule.rule_counter))
                            vars = []
                            for shift in overlappingShifts:
                                var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if var:
                                    vars.append(var)
                            solver.add_constr(xsum(vars) + restingPeriodShiftVar*100 <= 100, name='noOverlapRestingPeriodShiftsConstraint_{}_{}_{}_{}'.format(employee.id, timeBucket, minimumRestingPeriod,self.rule.rule_counter))
                        else:
                            restingPeriodShiftVar = solver.add_var(lb=1, ub=1, var_type='I', name='restingPeriodShiftVar_{}_{}_{}_{}'.format(employee.id, timeBucket, minimumRestingPeriod,self.rule.rule_counter))

                # make sure at least one rest period variable is 1 per period
                for start_period in range(day_begin, day_end - period*60 + minimumRestingPeriod*60 + 1, stepLength):
                    shiftsStartNextHour = [shift for shift in employee_shifts if shift.start >= start_period and shift.start < start_period + stepLength]
                    if len(shiftsStartNextHour) > 0:
                        earliestStart = start_period + stepLength
                        for shift in shiftsStartNextHour:
                            if shift.start < earliestStart:
                                earliestStart = shift.start
                        start_period_vars = start_period + stepLength
                        start_period = earliestStart

                        end_period = start_period + (period-minimumRestingPeriod)*60
                        restingPeriodSlackVar = solver.add_var(lb=0, ub=1, var_type='I', name=
                                                              'restingPeriodSlackVar_{}_{}_{}_{}'.format(employee.id,
                                                                                                         start_period,
                                                                                                         minimumRestingPeriod,
                                                                                                         self.rule.rule_counter))
                        slack_coeff = 0
                        shift_vars = []
                        resting_period_vars = []
                        for shift in shiftsStartNextHour:
                            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                            if var:
                                shift_vars.append(var)
                        for timeBucket in range(start_period_vars, end_period + 1, stepLength):
                            if timeBucket in hoursVars:
                                restingPeriodShiftVar = solver.var_by_name('restingPeriodShiftVar_{}_{}_{}_{}'.format(employee.id, timeBucket, minimumRestingPeriod,self.rule.rule_counter))
                                if restingPeriodShiftVar:
                                    resting_period_vars.append(restingPeriodShiftVar)
                        if not self.rule.is_mandatory:
                            slack_coeff = 1000
                            restingPeriodSlackVar.obj = int(penalty * domain.settings .rule_objective)
                        solver.add_constr(-xsum(shift_vars)+xsum(resting_period_vars) + slack_coeff*restingPeriodSlackVar >= 0, name='minimumRestingPeriodConstraint_{}_{}_{}_{}'.format(employee.id, minimumRestingPeriod, start_period,self.rule.rule_counter) )


    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            period = int(self.rule.parameter1) * 24 * 60
            minimumRestingPeriod = int(self.rule.parameter2)
            stepLength = int(60 * 60)

            for employee in domain.employees:
                day_begin = domain.days[0].date
                day_end = domain.days[len(domain.days) - 1].date
                for start_period in range(day_begin, day_end - period * 60 + minimumRestingPeriod * 60 + 1, stepLength):
                    if not self.rule.is_mandatory:
                        slack_var = solver.var_by_name('restingPeriodSlackVar_{}_{}_{}_{}'.format(employee.id, start_period, minimumRestingPeriod,self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=start_period))