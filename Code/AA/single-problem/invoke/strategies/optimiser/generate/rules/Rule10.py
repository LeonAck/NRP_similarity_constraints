from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule10:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # max minutes per shift
        shiftType = self.rule.parameter2
        excludeBreak = parse_boolean(self.rule.parameter3)
        if shiftType:
            self.rule.shift_types = [str(shiftType)]
        shifts_of_type = [shift for shift in domain.shifts.get_rule_applicable_shifts(self.rule)]
        for shift in shifts_of_type:
            shiftDuration = shift.pay_duration
            if not excludeBreak:
                shiftDuration += shift.break_duration
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                if not self.rule.parameter1:
                    maximumShiftDuration = employee.maximumShiftDuration
                else:
                    maximumShiftDuration = self.rule.parameter1
                if shiftDuration > maximumShiftDuration and shift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable_day(shift.start):
                    if employee.is_eligible(shift) and self.rule.is_applicable(shift, employee):
                        shiftMaxDurationSlackVar = solver.add_var(lb=0, ub=1, name='shiftMaxDurationSlack_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter), var_type='B')
                        slack_coeff = 0
                        if not self.rule.is_mandatory:
                            slack_coeff = 1
                            shiftMaxDurationSlackVar.obj = (shiftDuration - maximumShiftDuration) * self.rule.penalty * domain.settings.rule_objective
                        varText = VAR_DEFAULTS.assignment.id(employee, shift)
                        shiftEmpVariable = solver.var_by_name(varText)
                        if shiftEmpVariable:
                            solver.add_constr(shiftEmpVariable*-1 + slack_coeff * shiftMaxDurationSlackVar==0, name='shiftMaxDurationConstraint_{}_{}_{}'.format(employee.id,
                                                                                                     shift.id,
                                                                                                     self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        shiftType = self.rule.parameter2
        parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2,
                      "parameter_3": self.rule.parameter3}
        shifts_of_type = [shift for shift in domain.shifts.get_rule_applicable_shifts(self.rule) if (shiftType and shiftType in shift.shift_types) or not shiftType]
        for shift in shifts_of_type:
            shiftDuration = shift.pay_duration + shift.break_duration
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                if not self.rule.parameter1:
                    maximumShiftDuration = employee.maximumShiftDuration
                else:
                    maximumShiftDuration = self.rule.parameter1
                if shiftDuration > maximumShiftDuration and shift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable_day(shift.start):
                    if employee.is_eligible(shift) and self.rule.is_applicable(shift, employee):
                        slack_var = solver.var_by_name('shiftMaxDurationSlack_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            violationShifts = [shift]
                            output.append(Violation(rule_id=self.rule.id,
                                                    rule_tag=self.rule.tag,
                                                         user_id=employee.id,
                                                         violation_costs=slack_var.x * slack_var.obj,
                                                         shift_id=shift.id,
                                                         date=shift.start,
                                                         shift_start=shift.start,
                                                         shift_finish=shift.end,
                                                         department_id=shift.department_id,
                                                        relevant_shifts=[shift.id for shift in violationShifts],
                                                        violation_description=generate_violation_text(shiftType, maximumShiftDuration),
                                                    parameters=parameters
                                                    ))


def generate_violation_text(shiftType, maxLength):
    if shiftType:
        return "Shift of type {} is longer than {} hours".format(shiftType, maxLength/60)
    else:
        return "Shift is longer than {} hours".format(maxLength/60)
