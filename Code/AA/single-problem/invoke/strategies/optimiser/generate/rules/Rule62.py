from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
# Rule 62: Minimum of skill/department/license
class Rule62:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        minimum_of_skill_1 = int(self.rule.parameter1)
        minimum_of_skill_2 = int(self.rule.parameter2)
        minimum_employees = int(self.rule.parameter3)

        no_type = True  #if want to set overal minimum
        type_id ="no_type"
        if self.rule.department_id:
            type_id = "department_id" + self.rule.department_id
            no_type = False
        if self.rule.skill_id:
            type_id = "skill_id" + self.rule.skill_id
            no_type = False
        if self.rule.license_id:
            type_id = "license_id" + self.rule.license_id
            no_type = False

        type_id_2 = None
        if minimum_of_skill_2 > 0:
            if self.rule.department_id_2:
                type_id_2 = "department_id" + self.rule.department_id_2
            if self.rule.skill_id_2:
                type_id_2 = "skill_id" + self.rule.skill_id_2
            if self.rule.license_id_2:
                type_id_2 = "license_id" + self.rule.license_id_2

        if self.rule.penalty > 0:
            for shift_group_id in self.rule.shift_group_ids:
                assignment_vars_skill_1 = []
                assignment_vars_skill_2 = []
                all_assignment_vars = []
                for shift in domain.shifts:
                    if shift.group_id and shift.in_schedule(domain.settings.start, domain.settings.end) and self.rule.is_applicable_day(shift.start):
                        if str(shift.group_id) == str(shift_group_id):
                            for employee in domain.employees:
                                if not employee.is_eligible(shift):
                                    continue

                                department_ids = employee.department_ids
                                license_ids = [str(license.id) for license in employee.licenses]
                                skill_ids = [str(skill.id) for skill in employee.skills]
                                if no_type or self.rule.department_id in department_ids or self.rule.license_id in license_ids or self.rule.skill_id in skill_ids:
                                    var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                    assignment_vars_skill_1.append(var)
                                if minimum_of_skill_2 > 0:
                                    if self.rule.department_id_2 in department_ids or self.rule.license_id_2 in license_ids or self.rule.skill_id_2 in skill_ids:
                                        var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                        assignment_vars_skill_2.append(var)
                                if minimum_employees > 0:
                                    var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                    all_assignment_vars.append(var)


                positive_slack = solver.add_var(lb=0, ub=minimum_of_skill_1+1, var_type='I',
                                          name='positive_slack_minimum_skill_{}_{}_{}_{}'.format(type_id, minimum_of_skill_1, shift_group_id,
                                                                                 self.rule.rule_counter))
                negative_slack = solver.add_var(lb=0, ub=minimum_of_skill_2+1, var_type='I',
                                          name='negative_slack_minimum_skill_{}_{}_{}_{}'.format(type_id, minimum_of_skill_1, shift_group_id,
                                                                                 self.rule.rule_counter))
                if not self.rule.is_mandatory:
                    positive_slack.obj = positive_slack.obj + int(self.rule.penalty * domain.settings.rule_objective)
                    negative_slack.obj = negative_slack.obj + int(self.rule.penalty * domain.settings.rule_objective)

                skill_1_present_var = solver.add_var(var_type='B',
                                          name='help_var_skill_1_{}_{}_{}_{}'.format(type_id, minimum_of_skill_1, shift_group_id,
                                                                                 self.rule.rule_counter))
                solver.add_constr(minimum_of_skill_1 - xsum(assignment_vars_skill_1) <= 1000*(1-skill_1_present_var),
                                  name='minimum_of_skill_1_per_group_{}_{}_{}_{}'.format(type_id, minimum_of_skill_1,
                                                                                       shift_group_id,
                                                                                       self.rule.rule_counter))
                var_list = []
                if type_id_2:
                    skill_2_present_var = solver.add_var(var_type='B',
                                                         name='help_var_skill_2_{}_{}_{}_{}'.format(type_id_2,
                                                                                                    minimum_of_skill_2,
                                                                                                    shift_group_id,
                                                                                                    self.rule.rule_counter))
                    solver.add_constr(minimum_of_skill_2 - xsum(assignment_vars_skill_2) <= 1000*(1-skill_2_present_var),
                                      name='minimum_of_skill_2_per_group_{}_{}_{}_{}'.format(type_id_2, minimum_of_skill_2,
                                                                                           shift_group_id,
                                                                                           self.rule.rule_counter))
                    both_skills_present_var = solver.add_var(var_type='B',
                                                         name='help_var_both_skills_{}_{}_{}_{}'.format(type_id,
                                                                                                    minimum_of_skill_1,
                                                                                                    shift_group_id,
                                                                                                    self.rule.rule_counter))
                    solver.add_constr(skill_1_present_var + skill_2_present_var - 1 <= both_skills_present_var,
                                      name='both_skills_present_lb_{}_{}_{}_{}'.format(type_id,
                                                                                     minimum_of_skill_1,
                                                                                     shift_group_id,
                                                                                     self.rule.rule_counter))
                    solver.add_constr(both_skills_present_var <= skill_1_present_var,
                                      name='both_skills_present_ub1_{}_{}_{}_{}'.format(type_id,
                                                                                     minimum_of_skill_1,
                                                                                     shift_group_id,
                                                                                     self.rule.rule_counter))
                    solver.add_constr(both_skills_present_var <= skill_2_present_var,
                                      name='both_skills_present_ub2_{}_{}_{}_{}'.format(type_id,
                                                                                     minimum_of_skill_1,
                                                                                     shift_group_id,
                                                                                     self.rule.rule_counter))
                    var_list.append((minimum_employees,both_skills_present_var))
                else:
                    var_list.append((1,skill_1_present_var))

                if minimum_employees > 0:
                    # minimum_employees_var = solver.add_var(var_type='B',
                    #                                      name='minimum_employees_{}_{}_{}'.format(type_id,
                    #                                                                                 shift_group_id,
                    #                                                                                 ruleCounter))
                    # solver.add_constr(xsum(all_assignment_vars) - minimum_employees + 1 <= 10000 * minimum_employees_var,
                    #                   name='minimum_employee_{}_{}_{}_{}'.format(type_id,
                    #                                                                  minimum_of_skill_1,
                    #                                                                  shift_group_id,
                    #                                                                  ruleCounter))

                    var_list.extend([(-1, var) for var in all_assignment_vars])
                    ##(both) skill(s) present - minimum number of employees present == 0
                    solver.add_constr(xsum(coeff * var for coeff, var in var_list) + positive_slack - negative_slack == 0,name = 'minimum_of_skill_per_group_{}_{}_{}_{}'.format(type_id, minimum_of_skill_1, shift_group_id,
                                                                                 self.rule.rule_counter))
                else:
                    # both  skills present >= 1
                    solver.add_constr(xsum(coeff * var for coeff, var in var_list) + positive_slack >= 1,name = 'minimum_of_skill_per_group_{}_{}_{}_{}'.format(type_id, minimum_of_skill_1, shift_group_id,
                                                                                 self.rule.rule_counter))




    def add_violation_to_output(self, solver, domain, output):
        minimum_of_skill = int(self.rule.parameter1)

        type_id = "no_type"
        if self.rule.department_id:
            type_id = "department_id" + self.rule.department_id
        if self.rule.skill_id:
            type_id = "skill_id" + self.rule.skill_id
        if self.rule.license_id:
            type_id = "license_id" + self.rule.license_id

        if self.rule.penalty > 0:
            for shift_group_id in self.rule.shift_group_ids:
                if not self.rule.is_mandatory:
                    pos_slack_var = solver.var_by_name(name='positive_slack_minimum_skill_{}_{}_{}_{}'.format(type_id, minimum_of_skill, shift_group_id,
                                                                                 self.rule.rule_counter))
                    neg_slack_var = solver.var_by_name(name='negative_slack_minimum_skill_{}_{}_{}_{}'.format(type_id, minimum_of_skill, shift_group_id,
                                                                                 self.rule.rule_counter))
                    if pos_slack_var and pos_slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                violation_costs=pos_slack_var.x * pos_slack_var.obj,
                                                parameters={"parameter1": type_id},
                                                shift_group=shift_group_id))

                    if neg_slack_var and neg_slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                violation_costs=neg_slack_var.x * neg_slack_var.obj,
                                                parameters={"parameter1": type_id},
                                                shift_group=shift_group_id))
