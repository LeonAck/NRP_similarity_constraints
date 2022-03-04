from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule4:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # Rule 4: Minimum consecutive rest domain.days
        # create min rest domain.days
        minRest = self.rule.parameter1
        #not currently used (assume shift starts on day)
        startsOnDay = True

        # create the constraints for this rule
        # the sum of all the domain.days worked before - slack needs to be smaller than the consec shifts
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            if not employee.is_fixed:
                for dayIndex in range(0, len(domain.days) - 2):
                    #domain.shifts on work day
                    shifts1 = self.getShiftsToday(domain.shifts, domain.days[dayIndex], startsOnDay, employee, domain.settings )
                    #domain.shifts in rest period
                    shifts2 = []
                    lastDayIndex = dayIndex + minRest + 1
                    if lastDayIndex > len(domain.days):
                        lastDayIndex = len(domain.days)
                    for dayIndex2 in range(dayIndex+2, lastDayIndex):
                        shiftsOnDay = self.getShiftsToday(domain.shifts, domain.days[dayIndex2], startsOnDay, employee, domain.settings )
                        shifts2 += shiftsOnDay
                    #domain.shifts on first rest day
                    shifts3 = self.getShiftsToday(domain.shifts, domain.days[dayIndex+1], startsOnDay, employee, domain.settings )

                    for shift1 in shifts1:
                        if self.rule.is_applicable_shift(shift1) and employee.is_eligible(shift1):
                            slackVar = solver.add_var(lb=0, ub=1000,
                                                     name='minRestSlack_{}_{}_{}_{}'.format(employee.id, shift1.id,
                                                                                       domain.days[dayIndex + 1].date,
                                                                                            self.rule.rule_counter), var_type='I')
                            slackCoefficient = 0
                            varS2s = []
                            varS3s = []
                            var1 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift1))
                            for shift2 in shifts2:
                                if self.rule.is_applicable(shift2, employee) and employee.is_eligible(shift2):
                                    var2 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift2))
                                    if var2:
                                        varS2s.append(var2)
                            for shift3 in shifts3:
                                if self.rule.is_applicable(shift3, employee) and employee.is_eligible(shift3):
                                    var3 = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift3))
                                    if var3:
                                        varS3s.append(var3)

                            if not self.rule.is_mandatory:
                                slackCoefficient = -1000
                                slackVar.obj = self.rule.penalty * domain.settings .rule_objective
                            solver.add_constr(var1*100 + xsum(varS2s) + xsum(varS3s[i] * -1000 for i in range(0, len(varS3s))) + slackCoefficient*slackVar <= 100, name='minRestConstraint_{}_{}_{}_{}'.format(employee.id, shift1.id, domain.days[dayIndex+1].date,self.rule.rule_counter))


    def add_violation_to_output(self, solver, domain, output):
        # minimum consecutive rest domain.days
        if int(self.rule.parameter2) != 1:
            startsOnDay = True
        else:
            startsOnDay = False
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            if not employee.is_fixed:
                for dayIndex in range(0, len(domain.days) - 2):
                    shifts1 = self.getShiftsToday(domain.shifts, domain.days[dayIndex], startsOnDay, employee, domain.settings)
                    for shift1 in shifts1:
                        if self.rule.is_applicable(shift1, employee) and employee.is_eligible(shift1):
                            slack_var = solver.var_by_name('minRestSlack_{}_{}-{}-{}'.format(employee.id, shift1.id, domain.days[dayIndex+1].date, self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(vars(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                             user_id= employee.id,
                                                             shift_id=shift1.id,
                                                             violation_costs=slack_var.x * slack_var.obj,
                                                             date=domain.days[dayIndex+1].date)))
                #edge case slack
                var1 = solver.var_by_name('startMinRestSlack_{}_{}_{}'.format(employee.id, domain.days[0].date, self.rule.rule_counter))
                if var1 and var1.x > 0:
                    output.append(vars(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                 user_id=employee.id,
                                                 shift_id=shift1.id,
                                                 violation_costs=var1.x * var1.obj,
                                                 date=domain.days[0].date)))


    def getShiftsToday(self, shifts, day, startsOnDay, employee, settings):
        shiftsToday = []
        for shift in shifts:
            # Shifts starts on day
            if startsOnDay:
                shift_time_reference = shift.start
            # Shifts finish on day
            else:
                shift_time_reference = shift.end
            if day.date <= shift_time_reference < day.date + int(timedelta(days=1).total_seconds()) and shift.in_schedule(settings.start, settings.end) and (not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)):
                shiftsToday.append(shift)
        return shiftsToday
