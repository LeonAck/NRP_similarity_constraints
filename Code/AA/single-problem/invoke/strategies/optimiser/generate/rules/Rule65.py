from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
class Rule65:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # minimize difference between employee skill level and shift difficulty
        if self.rule.penalty > 0:
            for employee in domain.employees:
                employee_skill = [skill for skill in employee.skills if self.rule.skill_id == skill.id]
                if len(employee_skill) > 0:
                    for shift in domain.shifts:
                        if shift.shiftSkills and len(shift.shiftSkills) > 0:
                            shift_skill = [skill for skill in shift.shiftSkills if skill.id == self.rule.skill_id]
                            if not shift.is_fixed and employee.is_eligible(shift) and self.rule.is_applicable(shift, employee) and len(shift_skill) > 0:
                                abs_skill_difficulty_difference =  abs(shift_skill[0].difficulty - employee_skill[0].level)
                                slack_var = solver.add_var(lb=0, ub=1, var_type='B',
                                                                 name='matching_skill_difficulty{}_{}_{}_{}'.format(
                                                                     shift.id, employee.id, self.rule.skill_id,self.rule.rule_counter))
                                shiftAllocVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                if abs_skill_difficulty_difference > 0:
                                    slack_var.obj = slack_var.obj + 1 * self.rule.penalty * domain.settings.rule_objective * abs_skill_difficulty_difference
                                    solver.add_constr(shiftAllocVar - slack_var == 0,
                                                      name='matching_skill_difficulty{}_{}_{}_{}'.format(
                                                                     shift.id, employee.id, self.rule.skill_id,self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        for employee in domain.employees:
            corresponding_skill = [skill for skill in employee.skills if self.rule.skill_id == skill.id]
            if len(corresponding_skill) > 0:
                for shift in domain.shifts:
                    if shift.shiftSkills and len(shift.shiftSkills) > 0:
                        shift_skill = [skill.id == self.rule.skill_id for skill in shift.shiftSkills]
                        if not shift.is_fixed and employee.is_eligible(shift) and self.rule.is_applicable(shift, employee) and shift_skill:
                            slack_var = solver.var_by_name(name='matching_skill_difficulty{}_{}_{}_{}'.format(
                                                           shift.id, employee.id, self.rule.skill_id,self.rule.rule_counter))
                            if slack_var and slack_var.x > 0:
                                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                        user_id=employee.id,
                                                        violation_costs=slack_var.x * slack_var.obj,
                                                        shift_id=shift.id,
                                                        date=shift.start,
                                                        shift_start=shift.start,
                                                        shift_finish=shift.end,
                                                        department_id=shift.department_id))
