# Rule 43: at most W times per period the rest after a shift of type X ending after Y can be shorter than Z
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule43:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        minBreakLength = self.rule.parameter1
        maxTimeBetweenShifts = self.rule.parameter2
        if self.rule.parameter3:
            shiftTypeToCheck = self.rule.parameter3
        end_after = self.rule.parameter4
        nrExceptions = self.rule.parameter5
        period = self.rule.parameter6
        max_shift_duration = self.rule.parameter7  #minutes
        shifts_sorted_on_time = sorted(domain.shifts, key=lambda x: x.start)
        for employee in domain.employees:
            employee_shifts = [shift for shift in shifts_sorted_on_time if employee.is_eligible(shift)]
            employee_shifts_of_type = [shift for shift in employee_shifts if (self.rule.parameter3 and shiftTypeToCheck in shift.shift_types)]
            # iterate over the domain.shifts of the relevant type - the start of this shift is the start of the period over which to check the rule
            for index1, shift in enumerate(employee_shifts_of_type):
                # check if domain.shifts ends after certain time
                if shift.in_schedule(domain.settings .start, domain.settings .end) and not employee.is_fixed and (shift.end - shift.midnight_time_stamp)%(24*60*60) > end_after*60 and shift.pay_duration <= max_shift_duration and self.rule.is_applicable_day(shift.start):
                    nrViolations = 0
                    violationShifts = []
                    # iterate over domain.shifts in the period
                    for index2 in range(index1, len(employee_shifts_of_type)):
                        shift1 = employee_shifts_of_type[index2]
                        if shift1.end > shift.start + period*60:
                            break
                        shift1_text = VAR_DEFAULTS.assignment.id(employee, shift1)
                        shift1_var = solver.var_by_name(shift1_text)
                        if shift1_var and shift1_var.x > 0:
                            minBreakLengthAfterShift = minBreakLength
                            if (shift1.end - shift1.start) / 60 >= 600:
                                minBreakLengthAfterShift = max(12 * 60, minBreakLength - (shift1.pay_duration - 600))  # for domain.shifts X minutes longer than 10h the resttime may be reduced with maximum X minutes until a minimum of 12 hours
                            employee_shifts_after = [shift for shift in employee_shifts if shift1.end <= shift.start < shift1.end + minBreakLengthAfterShift * 60 and (not maxTimeBetweenShifts or shift1.end + maxTimeBetweenShifts * 60 < shift.start or maxTimeBetweenShifts == 0)]
                            # iterate over the domain.shifts within the minimum break length of the first shift
                            for shift2 in employee_shifts_after:
                                shift2_text = VAR_DEFAULTS.assignment.id(employee, shift2)
                                shift2_var = solver.var_by_name(shift2_text)
                                # if both domain.shifts are worked, add 1 to the counter of resttimes shorter than the minimum break length
                                if shift2_var and shift2_var.x > 0:
                                    if not shift1 in violationShifts:
                                        violationShifts.append(shift1)
                                    nrViolations += 1
                                    violationShifts.append(shift2)

                    # if there are more violations of minimum break length than allowed, add violation.
                    if nrViolations > nrExceptions:
                        shift_text = VAR_DEFAULTS.assignment.id(employee, shift)
                        shift_var = solver.var_by_name(shift_text)
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=shift_var.x * self.rule.penalty * domain.settings.rule_objective,
                                                shift_id=shift.id,
                                                date=shift.start,
                                                shift_start=shift.start,
                                                shift_finish=shift.end,
                                                department_id=shift.department_id,
                                                relevant_shifts=[shift.id for shift in violationShifts],
                                                violation_description=generate_violation_text(minBreakLength, end_after, nrExceptions, period, shift.start_datetime_str)))

def generate_violation_text(minimumRest, end_after, nrExceptions, period, start):
    hours = int(end_after/60)
    minutes = int(end_after - hours*60)
    return "More than {} time(s) less than {} hours rest after a shift ending after {} in the period of {} hours starting on {}".format(nrExceptions, minimumRest/(60), "%02d:%02d" % (hours, minutes), period/60, start)