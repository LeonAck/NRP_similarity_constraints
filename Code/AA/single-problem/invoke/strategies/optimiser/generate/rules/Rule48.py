from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
class Rule48:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        # Series including at least 1 shift of type X can have a length of at most Y
        # A series is defined as multiple domain.shifts ending with a restperiod of at least minimumRestTime minutes.
        if self.rule.penalty > 0:
            maxLength = self.rule.parameter1
            shiftType = self.rule.parameter2
            minimumRestTime = self.rule.parameter3
            shiftsSortedOnTime = sorted(domain.shifts, key=lambda x: x.start)
            for employee in domain.employees:
                employeeShifts = [shift for shift in shiftsSortedOnTime if solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                # iterate over domain.shifts and count the number of domain.shifts until the time between the current and next shift is >= minimumRestTime minutes
                shiftCount = 0
                shiftOfTypeCount = 0
                violationShifts = []
                for index, shift in enumerate(employeeShifts):
                    if self.rule.is_applicable_day(shift.start):
                        shiftCount += 1
                        if shiftType in shift.shift_types:
                            shiftOfTypeCount += 1
                        violationShifts.append(shift)

                        try:
                            nextShift = employeeShifts[index+1]
                            restTime = (nextShift.start - shift.end)/60
                        except:
                            restTime = minimumRestTime

                        # if restTime >= minimumRestTime this means the end of the series is reached - check the counters to see if the series violates the rule
                        if restTime >= minimumRestTime:
                            if shiftCount > maxLength and shiftOfTypeCount > 0:
                                shift = violationShifts[0]
                                var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                    date=shift.start,
                                                    relevant_shifts=[shift.id for shift in
                                                                     violationShifts],
                                                    violation_description=generate_violation_text(maxLength, shiftType, shift.start_datetime_str)))
                            shiftCount = 0
                            shiftOfTypeCount = 0
                            violationShifts = []

def generate_violation_text(maxLength, shiftType, start_series):
    return "The series starting on {} is longer than {} domain.shifts and includes a shift of type {}".format(start_series, maxLength, shiftType)