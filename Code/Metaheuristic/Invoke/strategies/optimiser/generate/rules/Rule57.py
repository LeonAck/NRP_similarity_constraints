from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule57:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # Penalty for not having X times Y consecutive domain.days off per period.
        if self.rule.penalty > 0:
            period = self.rule.parameter1
            restPeriod = self.rule.parameter2
            numberOfTimes = self.rule.parameter3
            for employee in domain.employees:
                # make consecDaysRestVar for each day
                for dayIndex in range(0, len(domain.days) - restPeriod):
                    twoDaysRestVars = []
                    nightShifts = [shift for shift in domain.shifts if employee.is_eligible(shift) and 3 in shift.shift_types and domain.days[dayIndex].date < shift.end < domain.days[dayIndex + 1].date]
                    for nightShift in nightShifts:
                        varText = VAR_DEFAULTS.assignment.id(employee, nightShift)
                        shiftEmpVariableShift = solver.var_by_name(varText)
                        if shiftEmpVariableShift:
                            twoDaysRestVars.append(shiftEmpVariableShift)
                    for dayNr in range(0, restPeriod):
                        day1 = domain.days[dayIndex + dayNr]
                        worksOn1 = solver.find_variable(VAR_DEFAULTS.works_on.id(employee, day1))
                        twoDaysRestVars.append(worksOn1)

                    consecDaysRestVar = solver.add_var(lb=0, ub=1, name='{}_{}_2daysRestVar'.format(employee.id, domain.days[dayIndex].date), var_type='B')
                    twoDaysRestConstraint = solver.add_constr(xsum(twoDaysRestVars) + 100 * consecDaysRestVar <= 100, name='{}_{}_{}_2daysRestConstraint'.format(employee.id, dayIndex,self.rule.rule_counter))

                    # Make sure rest variables do not overlap and have at least 1 day in between
                    prevRestVars = []
                    if dayIndex > 0:
                        prevRestVar = solver.var_by_name('{}_{}_2daysRestVar'.format(employee.id, domain.days[dayIndex - 1].date))
                        if prevRestVar:
                            prevRestVars.append(prevRestVar)
                    noOverlapConstraint = solver.add_constr(xsum(prevRestVars) + consecDaysRestVar <= 1, name='{}_{}_noOverlapConstraint57'.format(employee.id, domain.days[dayIndex].date))

                # make constraint for each period
                for index in range(0, len(domain.days), period):
                    twoDaysRestVars = []
                    for index2 in range(index, len(domain.days), 1):
                        twoDaysRestVar = solver.var_by_name('{}_{}_2daysRestVar'.format(employee.id, domain.days[index2].date))
                        if twoDaysRestVar:
                            twoDaysRestVars.append(twoDaysRestVar)

                    restSlackVar = solver.add_var(lb=0, ub=2, name='{}_{}_{}_restSlackVar'.format(employee.id, domain.days[index].date,self.rule.rule_counter), var_type='I')
                    slackCoefficient = 0
                    if not self.rule.is_mandatory:
                        slackCoefficient = 1
                        restSlackVar.obj = int((self.rule.penalty * domain.settings .rule_objective))

                    restConstraint = solver.add_constr(numberOfTimes <= xsum(twoDaysRestVars) + slackCoefficient*restSlackVar, name='{}_{}_{}_restConstraint'.format(employee.id, domain.days[index].date,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            restPeriod = self.rule.parameter2
            for employee in domain.employees:
                for dayIndex in range(0, len(domain.days) - restPeriod):
                    slack_var = solver.var_by_name('{}_{}_{}_restSlackVar'.format(employee.id, domain.days[dayIndex].date,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                date=domain.days[dayIndex].date))