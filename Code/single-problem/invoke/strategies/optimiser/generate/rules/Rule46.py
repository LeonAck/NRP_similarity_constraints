from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule46:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        # minimum X minutes of break for domain.shifts with pay duration longer than Y minutes, possibly split in breaks of minimum Z minutes
        minShiftpay_duration = self.rule.parameter1
        minBreakTime = self.rule.parameter2
        minBreakLength = self.rule.parameter3
        parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2,
                      "parameter_3": self.rule.parameter3}

        shiftsOfLength = [shift for shift in sorted(domain.shifts, key=lambda x: x.start) if shift.pay_duration >= minShiftpay_duration]
        for employee in domain.employees:
            employeeShifts = [shift for shift in shiftsOfLength if employee.is_eligible(shift) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
            for shift in employeeShifts:
                if self.rule.is_applicable(shift, employee) and self.rule.is_applicable_day(shift.start):
                    # count total length of breaks longer than minBreakLength
                    totalBreakTime = 0
                    if shift.break_duration > 0:
                        totalBreakTime = shift.break_duration
                    else:
                        for shift_break in shift.breaks:
                            break_duration = (shift_break.end - shift_break.start)/60
                            if break_duration >= minBreakLength:
                                totalBreakTime += break_duration
                    # Check if total length more than minBreakTime, if not add violation
                    if totalBreakTime < minBreakTime:
                        shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                        # if shift.id in shiftsData:
                        #     shiftsData[shift.id]['violation_costs'] += shiftVar.x * self.rule.penalty * domain.settings .rule_objective
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=shiftVar.x * self.rule.penalty * domain.settings.rule_objective,
                                                shift_id=shift.id,
                                                date=shift.start,
                                                shift_start=shift.start,
                                                shift_finish=shift.end,
                                                department_id=shift.department_id,
                                                relevant_shifts=[shift.id],
                                                violation_description=generate_violation_text(minBreakLength, minBreakTime, shift.id),
                                                parameters=parameters))

def generate_violation_text(minBreakLength, minBreakTime, shift_id):
    return "The total break time of breaks with a minimum length of {} hours is less than {} hours for shift {}".format(minBreakLength/60, minBreakTime/60, shift_id)