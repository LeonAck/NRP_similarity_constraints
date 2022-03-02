from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule22:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # even distribution of shift type
        if self.rule.penalty > 0:
            shift_type = str(self.rule.parameter1)
            for shift in domain.shifts:
                shift_types = [str(shift_type) for shift_type in shift.shift_types]
                if shift_type in shift_types:
                    for employee in domain.employees:
                        shiftTypeCount = 0
                        for shiftCount in employee.shift_counts:
                            if str(shiftCount.id) == str(shift_type):
                                shiftTypeCount = shiftCount.quantity
                        if employee.is_eligible(shift) and self.rule.is_applicable(employee, shift) and shiftTypeCount > 0:
                            varText = VAR_DEFAULTS.assignment.id(employee, shift)
                            shiftAllocVar = solver.var_by_name(varText)
                            evenShiftTypeSlack = solver.add_var(lb=0, ub=1, var_type='B', name='evenShiftTypeSlack_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))
                            evenShiftTypeSlack.obj = shiftTypeCount * self.rule.penalty * domain.settings .rule_objective
                            solver.add_constr(shiftAllocVar - evenShiftTypeSlack == 0, name='evenShiftTypeConstraint_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        # even distribution of shift type
        if self.rule.penalty != 0:
            shift_type = str(self.rule.parameter1)
            for shift in domain.shifts:
                if shift_type in shift.shift_types:
                    for employee in domain.employees:
                        if employee.is_eligible(shift) and self.rule.is_applicable(employee, shift):
                            slack_var = solver.var_by_name('evenShiftTypeSlack_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        shift_id=shift.id,
                                                        date=shift.start,
                                                        shift_start=shift.start,
                                                        shift_finish=shift.end,
                                                        department_id=shift.department_id))