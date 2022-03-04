from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule17:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # shift type preference rules
        if self.rule.penalty > 0:
            # if the employee has a preference, check whether a potential shift will generate an overlap. For every overlap minute give a bonus
            for employee in domain.employees:
                if len(employee.shiftTypePreferences) > 0:
                    for shift in domain.shifts:
                        for shiftTypePreferenceObject in employee.shiftTypePreferences:
                            for shiftTypePreference in shiftTypePreferenceObject.shift_types:
                                shift_type_list = [str(shift_type) for shift_type in shift.shift_types]
                                if str(shiftTypePreference) in shift_type_list:
                                    if shift.in_schedule(domain.settings .start, domain.settings .end) and self.rule.is_applicable(shift, employee) and self.rule.is_applicable_day(shift.start) and employee.is_eligible(shift) and not shift.is_fixed and not employee.is_fixed:

                                        shiftTypePreferenceAssignment = solver.add_var(lb=0, ub=1, name='shiftEmployeePreferenceVariable_{}_{}_{}_{}'.format(shift.id, employee.id, shiftTypePreference,self.rule.rule_counter))
                                        objective_factor = domain.settings .fairness_objective if domain.settings .fairness_objective != 0 else domain.settings .rule_objective
                                        shiftTypePreferenceAssignment.obj = -1 * self.rule.penalty * objective_factor * shiftTypePreferenceObject.weight
                                        varText = VAR_DEFAULTS.assignment.id(employee, shift)
                                        shiftEmpVariable = solver.var_by_name(varText)
                                        if shiftEmpVariable:
                                            solver.add_constr(shiftEmpVariable - shiftTypePreferenceAssignment == 0, name='shiftEmployeePreferenceConstraint_{}_{}_{}_{}'.format(
                                                                      shift.id, employee.id, shiftTypePreference,
                                                                      self.rule.rule_counter))



    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            for employee in domain.employees:
                if len(employee.shiftTypePreferences) > 0:
                    for shift in domain.shifts:
                        if self.rule.is_applicable(shift, employee) and self.rule.is_applicable_day(shift.start):
                            for shiftTypePreferenceObject in employee.shiftTypePreferences:
                                for shiftTypePreference in shiftTypePreferenceObject.shift_types:
                                    shift_type_list = [str(shift_type) for shift_type in shift.shift_types]
                                    if str(shiftTypePreference) in shift_type_list:
                                        slack_var = solver.var_by_name('shiftEmployeePreferenceVariable_{}_{}_{}_{}'.format(shift.id, employee.id, shiftTypePreference,self.rule.rule_counter))

                                        if slack_var and slack_var.x > 0:
                                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                                    user_id=employee.id,
                                                                    violation_costs=slack_var.x * slack_var.obj,
                                                                    shift_id=shift.id,
                                                                    date=shift.start,
                                                                    shift_start=shift.start,
                                                                    shift_finish=shift.end,
                                                                    department_id=shift.department_id))