from datetime import timedelta
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule31:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # After shift type (night shift) either parameter2-hour break or another shift of same type (night shift)
        if self.rule.penalty > 0:
            shiftTypeForRule = int(self.rule.parameter1)
            minimumBreakTimeSmall = int(self.rule.parameter2)
            penalty = self.rule.penalty

            hours_range_to_count_shifts = 32
            if self.rule.parameter3:
                hours_range_to_count_shifts = int(self.rule.parameter3)

            for employee in domain.employees:
                if not employee.is_fixed and self.rule.is_applicable(None, employee):
                    restVarsParameter1 = []
                    shifts_of_type = [shift for shift in domain.shifts if shiftTypeForRule in shift.shift_types and (employee.is_eligible(shift) or (shift.is_fixed and shift.employee_id == employee.id)) and shift.in_schedule(domain.settings .start, domain.settings .end)]
                    for shift in shifts_of_type:
                        shifts_of_typeAfter = [shift2 for shift2 in domain.shifts if shiftTypeForRule in shift2.shift_types and shift2.start > shift.end and shift2.start < shift.start + hours_range_to_count_shifts*60*60 and (employee.is_eligible(shift2) or (shift2.is_fixed and shift2.employee_id == employee.id))]
                        restOrNightShiftSlack = solver.add_var(lb=0, ub=1, var_type='B', name='restOrNightShiftSlack_{}_{}_{}_{}_{}'.format(employee.id, shift.id, str(shift.start),str(shift.end), self.rule.rule_counter))
                        slack_coeff = 0
                        if shift.end not in restVarsParameter1:
                            restVar = solver.add_var(lb=0, ub=1, var_type='B', name='restOrNightShift_{}_{}_{}_{}'.format(employee.id, shift.end, shift.end+minimumBreakTimeSmall*60,self.rule.rule_counter))
                            restVarsParameter1.append(shift.end)
                        else:
                            restVar = solver.var_by_name('restOrNightShift_{}_{}_{}_{}'.format(employee.id, shift.end, shift.end+minimumBreakTimeSmall*60,self.rule.rule_counter))

                        currentShiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                        vars = []
                        for shift2 in shifts_of_typeAfter:
                            shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift2))
                            if shiftVar:
                                vars.append(shiftVar)

                        if not self.rule.is_mandatory:
                            slack_coeff = 1
                            restOrNightShiftSlack.obj = int(penalty * domain.settings .rule_objective)
                        solver.add_constr(-currentShiftVar + restVar + xsum(vars) + slack_coeff * restOrNightShiftSlack >= 0, name='restOrNightShiftConstraint_{}_{}_{}_{}'.format(employee.id, shift.id, minimumBreakTimeSmall,self.rule.rule_counter))

                    # make sure restVar does not overlap with other shifts
                    for startTime in restVarsParameter1:
                        restVar = solver.var_by_name('restOrNightShift_{}_{}_{}_{}'.format(employee.id, startTime, startTime+minimumBreakTimeSmall*60,self.rule.rule_counter))
                        shiftsAfter = [shift3 for shift3 in domain.shifts if shift3.end > startTime and shift3.start < startTime + minimumBreakTimeSmall * 60 and (employee.is_eligible(shift3) or (shift3.is_fixed and shift3.employee_id == employee.id))]
                        vars = []
                        for shift3 in shiftsAfter:
                            shiftVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift3))
                            if shiftVar:
                                vars.append(shiftVar)
                        solver.add_constr(100*restVar + xsum(vars) <= 100, name='RestOrWorkConstraint_{}_{}_{}_{}'.format(employee.id, startTime, startTime + minimumBreakTimeSmall * 60,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        shiftTypeForRule = int(self.rule.parameter1)
        if self.rule.penalty > 0:
            for employee in domain.employees:
                shifts_of_type = [shift for shift in domain.shifts if shiftTypeForRule in shift.shift_types and (employee.is_eligible(shift) or (shift.is_fixed and shift.employee_id == employee.id))]
                for shift in shifts_of_type:
                    slack_var = solver.var_by_name('restOrNightShiftSlack_{}_{}_{}_{}_{}'.format(employee.id, shift.id, str(shift.start), str(shift.end),self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                shift_id=shift.id,
                                                date=shift.start,
                                                shift_start=shift.start,
                                                shift_finish=shift.end,
                                                department_id=shift.department_id))