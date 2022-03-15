from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule8:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # Rule 8: Shifts must start X minutes after midnight
        if self.rule.penalty > 0:
            for shift in domain.shifts:
                if shift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable_day(shift.start):
                    midnight_time_stamp = shift.midnight_time_stamp
                    shiftStartMinutesAfterMidnight = (shift.start - midnight_time_stamp) / 60
                    limit = self.rule.parameter1
                    if limit > 24*60:
                        limit = int(limit / 60)
                    if shiftStartMinutesAfterMidnight < limit:
                        for employee in domain.employees:
                            if employee.is_eligible(shift) and self.rule.is_applicable(shift, employee):
                                constraintText = 'shiftStartMinutesAfterMidnightConstraint_{}_{}_{}_{}_{}'.format(employee.id, str(shift.start), str(shift.end), shift.id,self.rule.rule_counter)
                                shiftStartMinutesAfterMidnightSlackVar = solver.add_var(lb=0, ub=1,
                                                                                       name='shiftStartMinutesAfterMidnightSlack_{}_{}_{}'.format(
                                                                                           employee.id, shift.id,
                                                                                           self.rule.rule_counter), var_type='B')
                                slack_coeff = 0
                                if not self.rule.is_mandatory:
                                    slack_coeff = 1
                                    shiftStartMinutesAfterMidnightSlackVar.obj = (self.rule.parameter1 - shiftStartMinutesAfterMidnight) * self.rule.penalty * domain.settings .rule_objective
                                shiftEmpVariable = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if shiftEmpVariable:
                                    solver.add_constr(-1*shiftEmpVariable + shiftStartMinutesAfterMidnightSlackVar*slack_coeff == 0, name=constraintText)

    def add_violation_to_output(self, solver, domain, output):
        limit = self.rule.parameter1
        parameters = {"parameter_1": self.rule.parameter1}
        for shift in domain.shifts:
            if shift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable_day(shift.start):
                for employee in domain.employees:
                    if employee.is_eligible(shift) and self.rule.is_applicable(shift, employee):
                        slack_var = solver.var_by_name('shiftStartMinutesAfterMidnightSlack_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))
                        shiftEmpVariable = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                        if shiftEmpVariable and shiftEmpVariable.x > 0 and slack_var and slack_var.x > 0 and slack_var.obj > 0:
                            violationShifts = [shift]
                            # if shift.id in shiftsData:
                            #     shiftsData[shift.id]['violation_costs'] += shiftStartMinutesAfterMidnightSlackVar.x * shiftStartMinutesAfterMidnightSlackVar.obj
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                         user_id=employee.id,
                                                         violation_costs=slack_var.x * slack_var.obj,
                                                         shift_id=shift.id,
                                                         date=shift.start,
                                                         shift_start=shift.start,
                                                         shift_finish=shift.end,
                                                         department_id=shift.department_id,
                                                         relevant_shifts=[shift.id for shift in violationShifts],
                                                         violation_description=generate_violation_text(shift.start, limit),
                                                         parameters=parameters))
def generate_violation_text(startTime, limit):
    hours = int(limit/60)
    minutes = int(limit % 60)
    return "The shift starting on {} starts before {}".format(startTime, f"{hours:02d}" + ":" + f"{minutes:02d}")