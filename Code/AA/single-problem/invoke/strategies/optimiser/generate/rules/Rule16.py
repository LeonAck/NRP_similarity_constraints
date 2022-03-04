from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
class Rule16:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # x number of minutes of break after every X minutes
        parameter = self.rule.parameter1
        parameter2 = self.rule.parameter2
        if self.rule.penalty > 0:
            for shift in domain.shifts.get_shifts_starts_in_interval(domain.settings.start, domain.settings.end).get_rule_applicable_shifts(self.rule):
                for employee in domain.employees.get_rule_applicable_employees(self.rule):
                    if employee.is_eligible(shift) and (not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)):
                        check_rule = False
                        start_of_working = shift.start
                        long_enough_breaks = [b for b in shift.breaks if (b.end - b.start) / 60 >= parameter2]
                        for b in long_enough_breaks:
                            if b.start > start_of_working + (parameter * 60):
                                check_rule = True
                            start_of_working = b.end
                        if len(long_enough_breaks) == 0 and (shift.end - shift.start) / 60 > parameter:
                            check_rule = True
                        if check_rule:
                            breakEmployeeSlack = solver.add_var(lb=0, ub=1, name='shiftEmployeeCorrectBreakSlack_{}_{}_{}'.format(
                                shift.id, employee.id,self.rule.rule_counter), var_type='B')
                            slack_coeff = 0
                            if not self.rule.is_mandatory:
                                slack_coeff = -1
                                breakEmployeeSlack.obj = self.rule.penalty * domain.settings.rule_objective

                            varText = VAR_DEFAULTS.assignment.id(employee, shift)
                            shiftEmpVariable = solver.var_by_name(varText)
                            if shiftEmpVariable:
                                solver.add_constr(shiftEmpVariable + slack_coeff*breakEmployeeSlack == 0, name='shiftbreak_durationEmployee_{}_{}_{}'.format(employee.id, shift.id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        for shift in domain.shifts.get_shifts_starts_in_interval(domain.settings.start,
                                                                 domain.settings.end).get_rule_applicable_shifts(
                self.rule):
            for employee in domain.employees.get_rule_applicable_employees(self.rule):
                if employee.is_eligible(shift) and (not shift.is_fixed or (shift.is_fixed and shift.employee_id == employee.id)):
                    slack_var = solver.var_by_name('shiftEmployeeCorrectBreakSlack_{}_{}_{}'.format(shift.id, employee.id,self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj,
                                                shift_id=shift.id,
                                                date=shift.start,
                                                shift_start=shift.start,
                                                shift_finish=shift.end,
                                                department_id=shift.department_id))