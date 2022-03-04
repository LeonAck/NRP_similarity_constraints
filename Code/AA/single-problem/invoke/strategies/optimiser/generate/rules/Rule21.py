from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
class Rule21:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # even distribution of hours
        if self.rule.penalty != 0:
            for shift in domain.shifts:
                for employee in domain.employees:
                    previous_hours = employee.previous_hours
                    if employee.is_eligible(shift) and self.rule.is_applicable(employee, shift) and previous_hours > 0:
                        varText = VAR_DEFAULTS.assignment.id(employee, shift)
                        shiftAllocVar = solver.var_by_name(varText)

                        evenHoursSlack = solver.add_var(lb=0, ub=1, var_type='B', name='evenHoursSlack_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))
                        evenHoursSlack.obj = previous_hours * self.rule.penalty * domain.settings .rule_objective
                        solver.add_constr(shiftAllocVar - evenHoursSlack == 0, name='evenHoursConstraint_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0:
            for shift in domain.shifts:
                for employee in domain.employees:
                    previous_hours = employee.previous_hours
                    if employee.is_eligible(shift) and self.rule.is_applicable(employee, shift)  and previous_hours > 0:
                        slack_var = solver.var_by_name('evenHoursSlack_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    shift_id=shift.id,
                                                    date=shift.start,
                                                    shift_start=shift.start,
                                                    shift_finish=shift.end,
                                                    department_id=shift.department_id))