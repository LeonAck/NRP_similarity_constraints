from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule55:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # After shift of type y either another shift of type y or no shift of this type for the next x domain.days
        if self.rule.penalty > 0:
            shiftTypeForRule = int(self.rule.parameter1)
            daysInBetween = int(self.rule.parameter2)
            penalty = self.rule.penalty
            for employee in domain.employees:
                if not employee.is_fixed and self.rule.is_applicable(None, employee):
                    employeeShiftsOfType = [shift for shift in domain.shifts if shiftTypeForRule in shift.shift_types and (employee.is_eligible(shift) or (shift.is_fixed and shift.employee_id == employee.id))]
                    for shift in employeeShiftsOfType:
                        shifts_of_typeNextDay = [shift2 for shift2 in employeeShiftsOfType if shift2.start > shift.end and shift2.start < shift.start + 36*60*60 and (employee.is_eligible(shift2) or (shift2.is_fixed and shift2.employee_id == employee.id))]
                        shifts_of_typeNextDays = [shift3 for shift3 in employeeShiftsOfType if shift3.start > shift.end and shift3.start < shift.start + (daysInBetween*24+12)*60*60 and (employee.is_eligible(shift3) or (shift3.is_fixed and shift3.employee_id == employee.id)) and shift3 not in shifts_of_typeNextDay]
                        if len(shifts_of_typeNextDays) > 0:
                            vars = []
                            coefficients = []
                            currentShiftEmpVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                            if currentShiftEmpVar:
                                vars.append(currentShiftEmpVar)
                                coefficients.append(-1)
                            for shiftNextDay in shifts_of_typeNextDay:
                                nextDayShiftEmpVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shiftNextDay))
                                if nextDayShiftEmpVar:
                                    vars.append(nextDayShiftEmpVar)
                                    coefficients.append(1)

                            # make variable that is 0 if 1 or more of the domain.shifts from shifts_of_typeNextDays are worked and 1 otherwise
                            varsHelp = []
                            notWorksInNextDaysVar = solver.add_var(name='{}_{}_{}_notWorksInNextDaysVar'.format(employee.id, shift.id,self.rule.rule_counter), lb=0, ub=1, var_type='B')
                            for shiftNextDays in shifts_of_typeNextDays:
                                shiftNextDaysVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shiftNextDays))
                                if shiftNextDaysVar:
                                    varsHelp.append(shiftNextDaysVar)
                            workAtLeastOneConstraint = solver.add_constr(xsum(varsHelp) + len(shifts_of_typeNextDays)*notWorksInNextDaysVar <= len(shifts_of_typeNextDays), name='workAtLeastOneConstraint{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))
                            vars.append(notWorksInNextDaysVar)
                            coefficients.append(1)

                            nextOrDaysInBetweenSlackVar = solver.add_var(name='nextOrDaysInBetweenSlackVar{}_{}_{}_{}_{}'.format(employee.id, shift.id, str(shift.start), str(shift.end),self.rule.rule_counter), lb=0, ub=1, var_type='C')
                            slackCoefficient = 0
                            if not self.rule.is_mandatory:
                                slackCoefficient = 1
                                nextOrDaysInBetweenSlackVar.obj = int((self.rule.penalty * domain.settings .rule_objective))

                            nextOrDaysInBetweenConstraintLeft = solver.add_constr(0 <= xsum(vars[i] * coefficients[i] for i in range(0, len(vars))) + slackCoefficient * nextOrDaysInBetweenSlackVar,
                                                  name='nextOrDaysInBetweenConstraint{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))
                            nextOrDaysInBetweenConstraintRight = solver.add_constr(xsum(vars[i] * coefficients[i] for i in range(0, len(vars))) + slackCoefficient * nextOrDaysInBetweenSlackVar <= 2,
                                                                              name='nextOrDaysInBetweenConstraint{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        shiftTypeForRule = int(self.rule.parameter1)
        if self.rule.penalty > 0:
            for employee in domain.employees:
                shifts_of_type = [shift for shift in domain.shifts if shiftTypeForRule in shift.shift_types and (employee.is_eligible(shift) or (shift.is_fixed and shift.employee_id == employee.id))]
                for shift in shifts_of_type:
                    slack_var = solver.var_by_name('nextOrDaysInBetweenSlackVar{}_{}_{}_{}_{}'.format(employee.id, shift.id, str(shift.start), str(shift.end),self.rule.rule_counter))
                    if slack_var and slack_var.x > 0 and slack_var.obj > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                shift_id=shift.id,
                                                date=shift.start,
                                                shift_start=shift.start,
                                                shift_finish=shift.end,
                                                department_id=shift.department_id))