from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule23:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # minimum rest periods in certain timeframe
        if self.rule.penalty != 0:
            period = int(self.rule.parameter1) * 24 * 60
            minimumRestingPeriod = int(self.rule.parameter2)
            penalty = self.rule.penalty

            for employee in domain.employees:
                day_begin = domain.days[0]
                day_end = domain.days[len(domain.days) - 1].date + 24 * 60 * 60 * 1
                current_time = day_begin.date
                finished = False
                while not finished:
                    shiftsInPeriod = [shift for shift in domain.shifts if shift.in_schedule(domain.settings .start, domain.settings .end) and shift.end > current_time and shift.start < (current_time + int(timedelta(minutes=minimumRestingPeriod).total_seconds())) and (
                            employee.is_eligible(shift) or (shift.is_fixed and shift.employee_id == employee.id))]
                    if len(shiftsInPeriod) > 0:
                        shift_vars = []
                        for shift in shiftsInPeriod:
                            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                            if var:
                                shift_vars.append(var)
                        workingVar = solver.add_var(lb=0, ub=1, var_type='B', name='WorkingVar_{}_{}_{}_{}'.format(employee.id, current_time, minimumRestingPeriod,self.rule.rule_counter))
                        solver.add_constr(-xsum(shift_vars)+5*workingVar >= 0, name='restWhenNotWorkingConstraint_{}_{}_{}_{}'.format(employee.id, current_time, minimumRestingPeriod,self.rule.rule_counter))

                        notWorkingVar = solver.add_var(lb=0, ub=1, var_type='B', name='notWorkingVar_{}_{}_{}_{}'.format(employee.id, current_time, minimumRestingPeriod,self.rule.rule_counter))
                    else:
                        notWorkingVar = solver.add_var(lb=1, ub=1, var_type='B', name='notWorkingVar_{}_{}_{}_{}'.format(employee.id, current_time, minimumRestingPeriod,self.rule.rule_counter))
                        workingVar = solver.add_var(lb=0, ub=0, var_type='B', name='WorkingVar_{}_{}_{}_{}'.format(employee.id, current_time, minimumRestingPeriod,self.rule.rule_counter))
                    solver.add_constr(notWorkingVar + workingVar == 1, name='workEqualityContraint_{}_{}_{}_{}'.format(employee.id, current_time, minimumRestingPeriod,self.rule.rule_counter))

                    # current_time = current_time + (minimumRestingPeriod) * 60
                    current_time = current_time + 12 * 60 * 60
                    if current_time > day_end - minimumRestingPeriod * 60:
                        finished = True
                # so now we have all the constraints and we iterate over each day to check whether there is a violation
                finished = False
                current_day = day_begin.date
                while not finished:
                    restVarSlack = solver.add_var(lb=0, ub=10, var_type='I', name='restVarSlack_{}_{}_{}_{}'.format(employee.id, current_day,
                                                                                          minimumRestingPeriod,
                                                                                          self.rule.rule_counter))
                    slack_coeff = 0
                    vars = []
                    for hour_begin in range(current_day, current_day + period * 60 - minimumRestingPeriod * 60, 60 * 60):
                        not_working_var = solver.var_by_name('notWorkingVar_{}_{}_{}_{}'.format(employee.id, hour_begin, minimumRestingPeriod,self.rule.rule_counter))
                        if not_working_var:
                            vars.append(not_working_var)
                    # increment per day
                    current_day = current_day + 24 * 60 * 60
                    if current_day + period * 60 > day_end:
                        finished = True
                    if not self.rule.is_mandatory:
                        slack_coeff = 1
                        restVarSlack.obj = penalty * domain.settings .rule_objective
                    solver.add_constr(xsum(vars) + slack_coeff*restVarSlack >= 1, name='minimumOneRestPeriod_{}_{}_{}_{}'.format(employee.id, current_day, minimumRestingPeriod,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        # If the input shift has an user ID, treat it like a penalty
        if self.rule.penalty > 0:
            period = int(self.rule.parameter1) * 24 * 60
            minimumRestingPeriod = int(self.rule.parameter2)
            for employee in domain.employees:
                day_begin = domain.days[0]
                day_end = domain.days[len(domain.days) - 1].date + 24 * 60 * 60 * 1
                # so now we have all the constraints and we iterate over each day to check whether there is
                finished = False
                current_day = day_begin.date
                while not finished:
                    current_day = current_day + 24 * 60 * 60
                    if current_day + period * 60 > day_end:
                        finished = True
                    if not self.rule.is_mandatory:
                        slack_var = solver.var_by_name('restVarSlack_{}_{}_{}_{}'.format(employee.id, current_day, minimumRestingPeriod,self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=current_day))
