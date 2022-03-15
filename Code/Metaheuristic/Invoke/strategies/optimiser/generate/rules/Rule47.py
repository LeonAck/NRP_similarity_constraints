from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule47:
    # only for rule checking
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        # minimum X minutes rest in every period of Y*24 hours, which can be split up in periods of minimum Z minutes
        if self.rule.penalty > 0:
            period = int(self.rule.parameter1) * 24 * 60
            minimumTotalRest = int(self.rule.parameter2)
            minimumLengthRest = int(self.rule.parameter3)
            parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2, "parameter_3": self.rule.parameter3}

            shiftsSortedOnTime = sorted(domain.shifts, key=lambda x: x.start)
            for employee in domain.employees:
                employeeShifts = [shift for shift in shiftsSortedOnTime if solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
                # iterate over sorted domain.shifts - the start of every shift is the start of a period in which the minimum rest must be satisfied
                for start_shift in employeeShifts:
                    if self.rule.is_applicable_day(start_shift.start):
                        employeeShiftsInPeriod = [shift for shift in employeeShifts if start_shift.start <= shift.start < start_shift.start + period*60]
                        violationShifts = [shift for shift in employeeShiftsInPeriod]
                        totalRest = 0
                        # iterate over the domain.shifts in the period to determine the resttime after this shift (either the time until the next shift, which can be outside of the period, or the minimumTotalRest time if there is next shift).
                        for index, shift1 in enumerate(employeeShiftsInPeriod):
                            try:
                                shift2 = employeeShiftsInPeriod[index+1]
                                endRest = shift2.start
                            except:
                                endRest = start_shift.start + period*60
                                # shiftsAfter = [shift for shift in employeeShifts if shift1.start < shift.start < shift1.start + minimumTotalRest*60]
                                # endRest = shift1.end + minimumTotalRest*60
                                # if len(shiftsAfter) > 0:
                                #     endRest = shiftsAfter[0].start
                                #     violationShifts.append(shiftsAfter[0])
                            restTime = endRest-shift1.end
                            # if the resttime after the shift is longer than the minimum length of a restperiod, add to the total rest.
                            if restTime >= minimumLengthRest*60:
                                totalRest += restTime
                        # if the total rest in the period is not sufficient, add rule violation
                        if totalRest < minimumTotalRest*60:
                            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, start_shift))
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=var.x * self.rule.penalty * domain.settings.rule_objective,
                                                    date=start_shift.start,
                                                    relevant_shifts=[shift.id for shift in
                                                                     violationShifts],
                                                    violation_description=generate_violation_text(minimumTotalRest, minimumLengthRest, period, start_shift.start_datetime_str),
                                                    parameters=parameters))
def generate_violation_text(minimumTotalRest, minimumLengthRest, periodLength, periodStart):
    return "Less than {} hours rest in restperiods of at least {} hours in the period of {} x 24 hours starting on {}".format(round(minimumTotalRest/60), round(minimumLengthRest/60), round(periodLength/(60*24)), periodStart)