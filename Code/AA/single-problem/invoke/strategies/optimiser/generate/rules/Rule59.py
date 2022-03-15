from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule59:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # Penalty for overlap with preference not to work
        if self.rule.penalty > 0:
            for shift in domain.shifts:
                for employee in domain.employees:
                    if len(employee.employee_off_day_preferences) > 0:
                        if not shift.is_fixed and employee.is_eligible(shift) and self.rule.is_applicable(shift, employee):
                            for offDayPreference in employee.employee_off_day_preferences:
                                if offDayPreference.start < shift.end and offDayPreference.end > shift.start:
                                    overlapStart = offDayPreference.start
                                    overlapEnd = offDayPreference.end
                                    if offDayPreference.start < shift.start:
                                        overlapStart = shift.start
                                    if offDayPreference.end > shift.end:
                                        overlapEnd = shift.end
                                    overlapHours = int((overlapEnd - overlapStart) / (60 * 60))
                                    if overlapHours > 0:
                                        varText = VAR_DEFAULTS.assignment.id(employee, shift)
                                        shiftAllocVar = solver.var_by_name(varText)
                                        overlapVariable = solver.add_var(lb=0, ub=1, var_type='B', name='overlapOffDayPreferenceVariable_{}_{}_{}_{}_{}'.format(shift.id, employee.id, offDayPreference.start, offDayPreference.end,self.rule.rule_counter))
                                        overlapVariable.obj = 1 * self.rule.penalty * domain.settings .rule_objective * overlapHours
                                        solver.add_constr(shiftAllocVar - overlapVariable == 0, name='overlapOffDayPreferenceConstraint_{}_{}_{}_{}_{}'.format(shift.id, employee.id, offDayPreference.start, offDayPreference.end,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            for shift in domain.shifts:
                for employee in domain.employees:
                    for offDayPreference in employee.employee_off_day_preferences:
                        slack_var = solver.var_by_name('overlapOffDayPreferenceVariable_{}_{}_{}_{}_{}'.format(shift.id, employee.id, offDayPreference.start, offDayPreference.end,self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                         user_id=employee.id,
                                                         violation_costs=slack_var.x * slack_var.obj,
                                                         shift_id=shift.id,
                                                         date=shift.start,
                                                         shift_start=shift.start,
                                                         shift_finish=shift.end,
                                                         department_id=shift.department_id))
