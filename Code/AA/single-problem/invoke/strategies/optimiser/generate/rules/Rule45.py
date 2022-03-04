from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule45:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # After series of length >= X of domain.shifts of type Y either Z hour break or another shift of the same type
        if self.rule.penalty > 0:
            shiftTypeForRule = int(self.rule.parameter1)
            minimumSeriesLength = int(self.rule.parameter2)
            minimumBreakTime = int(self.rule.parameter3)
            penalty = self.rule.penalty
            for employee in domain.employees:
                if not employee.is_fixed and self.rule.is_applicable(None, employee):
                    employeeShifts = [shift for shift in domain.shifts if employee.is_eligible(shift) and shift.in_schedule(domain.settings.start, domain.settings.end)]
                    employeeShiftsOfType = [shift for shift in employeeShifts if shiftTypeForRule in shift.shift_types]
                    # for each shift of type, check if there are domain.shifts of the same type in the X-1 domain.days before, and ensure that if they are assigned,
                    # there is either a shift of the same type the next day or no shift in the next Z hours
                    for shift in employeeShiftsOfType:
                        if self.rule.is_applicable_day(shift.start):
                            shifts_of_typeAfter = [shift2 for shift2 in employeeShiftsOfType if shift2.start > shift.end and shift2.start < shift.start + 36*60*60]
                            restOrNightShiftSlack = solver.add_var(lb=0, ub=1, var_type='B', name='restOrNightShiftSlack_{}_{}_{}_{}_{}'.format(employee.id, shift.id, str(shift.start), str(shift.end),self.rule.rule_counter))
                            slack_coeff = 0
                            restVar = solver.add_var(lb=0, ub=1, var_type='B', name='restOrNightShift_{}_{}_{}_{}'.format(employee.id, shift.id, shift.end + minimumBreakTime*60,self.rule.rule_counter))
                            # make sure restVar does not overlap with other shifts
                            startTime = shift.end
                            shifts_within_rest = [shift4 for shift4 in employeeShifts if
                                           shift4.end > startTime and shift4.start < startTime + minimumBreakTime * 60]
                            shift_vars_within_rest = []
                            for shift_in_rest in shifts_within_rest:
                                shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_in_rest))
                                if shiftVar:
                                    shift_vars_within_rest.append(shiftVar)
                            solver.add_constr(xsum(shift_vars_within_rest) + 1000*restVar <= 1000,
                                              name='RestOrWorkConstraint_{}_{}_{}_{}'.format(employee.id, shift.id,
                                                                                             startTime + minimumBreakTime * 60,
                                                                                             self.rule.rule_counter))

                            # add variables for the current shift, restvariable and domain.shifts of type after the current shift
                            currentShiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))

                            next_day_shiftsoftype = []
                            prevShifts = []

                            for shift3 in shifts_of_typeAfter:
                                shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift3))
                                next_day_shiftsoftype.append(shiftVar)

                            # add variables for domain.shifts of type before the current shift
                            shifts_of_typeBefore = [shift2 for shift2 in employeeShiftsOfType if shift2.start > shift.start - ((minimumSeriesLength-1)*24 + 12)*60*60 and shift2.start < shift.start]
                            for idx,prevShift in enumerate(shifts_of_typeBefore):
                                overlapping_shifts = []
                                for checkOverlapShift in list(shifts_of_typeBefore[idx+1:]):
                                    if prevShift.is_fixed and checkOverlapShift.is_fixed and prevShift.employee_id == checkOverlapShift.employee_id:
                                        if prevShift.start <= checkOverlapShift.start < prevShift.end:
                                            overlapping_shift = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, checkOverlapShift))
                                            overlapping_shifts.append(overlapping_shift)
                                            shifts_of_typeBefore.remove(checkOverlapShift)

                                if len(overlapping_shifts) > 0:
                                    overlap_var = solver.add_var(lb=0, ub=1, var_type='B',
                                                         name='overlapping_shifts_{}_{}_{}_{}'.format(employee.id,
                                                                                                    prevShift.id,
                                                                                                    overlapping_shifts[0].id,
                                                                                                    self.rule.rule_counter))
                                    solver.add_constr(xsum(overlapping_shifts) <= 10000 * overlap_var, name='define_overlap_var_{}_{}_{}_{}'.format(employee.id,
                                                                                                    prevShift.id,
                                                                                                    overlapping_shifts[0].id, self.rule.rule_counter))
                                    prevShifts.append(overlap_var)
                                else:
                                    shiftVar = solver.var_by_name(VAR_DEFAULTS.assignment.id(employee, prevShift))
                                    prevShifts.append(shiftVar)

                            if not self.rule.is_mandatory:
                                slack_coeff = 1
                                restOrNightShiftSlack.obj = int(penalty * domain.settings .rule_objective)
                            #assumption one night shift per day
                            solver.add_constr(xsum(prevShifts) + currentShiftVar <= xsum(next_day_shiftsoftype) + restVar + slack_coeff * restOrNightShiftSlack + (minimumSeriesLength - 1), name='restOrNightShift_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        shiftTypeForRule = int(self.rule.parameter1)
        minimumSeriesLength = int(self.rule.parameter2)
        minimumBreakTime = int(self.rule.parameter3)
        if self.rule.penalty > 0:
            for employee in domain.employees:
                employeeShifts = [shift for shift in domain.shifts if employee.is_eligible(shift)]
                employeeShiftsOfType = [shift for shift in employeeShifts if shiftTypeForRule in shift.shift_types]
                for shift in employeeShiftsOfType:
                    if self.rule.is_applicable_day(shift.start):
                        slack_var = solver.var_by_name('restOrNightShiftSlack_{}_{}_{}_{}_{}'.format(employee.id, shift.id, str(shift.start), str(shift.end),self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            violationShifts = []
                            shifts_of_typeBefore = [shift2 for shift2 in employeeShiftsOfType if shift2.start > shift.start - ((minimumSeriesLength - 1) * 24 + 12) * 60 * 60 and shift2.start < shift.start]
                            for prevShift in shifts_of_typeBefore:
                                shiftVar = solver.var_by_name(VAR_DEFAULTS.assignment.id(employee, prevShift))
                                if shiftVar and shiftVar.x > 0:
                                    violationShifts.append(prevShift)
                            violationShifts.append(shift)
                            shiftsAfter = [shift4 for shift4 in employeeShifts if shift4.end > shift.end and shift4.start < shift.end + minimumBreakTime * 60]
                            for shift5 in shiftsAfter:
                                shiftVar = solver.var_by_name(VAR_DEFAULTS.assignment.id(employee, shift5))
                                if shiftVar and shiftVar.x > 0:
                                    violationShifts.append(shift5)
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    shift_id=shift.id,
                                                    date=shift.start,
                                                    shift_start=shift.start,
                                                    shift_finish=shift.end,
                                                    department_id=shift.department_id,
                                                    relevant_shifts=[shift.id for shift in violationShifts],
                                                    violation_description=generate_violation_text(minimumBreakTime, shiftTypeForRule, shift.end_datetime_str)))
def generate_violation_text(minimumRest, shiftType, endSeries):
    return "Less than {} hours rest after series of shifts of type {} starting on {}".format(minimumRest/60, shiftType, endSeries)