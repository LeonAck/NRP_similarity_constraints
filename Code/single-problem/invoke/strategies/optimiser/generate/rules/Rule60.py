from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 60: Minimum of skill/department/license working for specified times
class Rule60:
    def __init__(self, rule):
        self.rule = rule
        self.max_ts = 2208988800   #2040-01-01

    def set_rule(self, solver, domain, superset_emps=None, superset_shifts=None):
        minimum_of_skill = int(self.rule.parameter1)
        bucket_size = 15
        if self.rule.parameter2:
            bucket_size = int(self.rule.parameter2)

        activate_shift_type_id = False
        if self.rule.parameter3:
            activate_shift_type_id = True

        has_type_id = True
        if self.rule.department_id:
            type_id = "department_id" + self.rule.department_id
            has_type_id = any([department.id == self.rule.department_id
                               for employee in domain.employees
                               for department in employee.departments])
        if self.rule.skill_id:
            type_id = "skill_id" + self.rule.skill_id
            has_type_id = any([skill.id == self.rule.skill_id
                               for employee in domain.employees
                               for skill in employee.skills])

        if self.rule.license_id:
            type_id = "license_id" + self.rule.license_id
            has_type_id = any([license.id == self.rule.license_id
                               for employee in domain.employees
                               for license in employee.licenses])

        if not has_type_id:
            return

        shifts_in_departments = domain.shifts
        super_shifts_in_departments = sorted(superset_shifts,
                                             key=lambda x: x.end) if superset_shifts else superset_shifts
        if self.rule.department_ids:
            shifts_in_departments = [shift for shift in domain.shifts if shift.department_id in self.rule.department_ids]
            if superset_shifts:
                super_shifts_in_departments = [shift for shift in superset_shifts if
                                               shift.department_id in self.rule.department_ids]

        if superset_emps:
            employee_mapping = {}
            for employee in superset_emps:
                employee_mapping[employee.id] = employee

        if self.rule.penalty > 0:
            for day in domain.days:
                if not str(day.weekday) in self.rule.required_times:
                    continue
                current_time = day.date + self.rule.required_times[str(day.weekday)]["minutes_from"]*60
                end_time = day.date + self.rule.required_times[str(day.weekday)]["minutes_to"]*60
                while current_time < end_time and current_time < self.max_ts:
                    superset_assignments = 0
                    if superset_shifts:
                        for super_shift in super_shifts_in_departments:
                            if current_time <= super_shift.end:
                                if super_shift.start <= current_time:
                                    superset_assignments += int(
                                        self.emp_shift_has_type_id(employee_mapping[super_shift.employee_id],
                                                                   super_shift,
                                                                   activate_shift_type_id))
                            else:
                                break

                    assignment_vars = []
                    for shift in shifts_in_departments:
                        if shift.in_schedule(domain.settings.start, domain.settings.end):
                            if shift.start <= current_time <= shift.end:
                                for employee in domain.employees:
                                    if not employee.is_eligible(shift):
                                        continue

                                    if self.emp_shift_has_type_id(employee, shift, activate_shift_type_id):
                                        var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                        assignment_vars.append(var)

                    if len(assignment_vars) > 0 or superset_assignments > 0:
                        minimum_slack = solver.add_var(lb=0, ub=minimum_of_skill, var_type='I',
                                                  name='minimum_of_skill_{}_{}_{}_{}'.format(type_id, minimum_of_skill, current_time,
                                                                                         self.rule.rule_counter))
                        slack_coeff = 0
                        if not self.rule.is_mandatory:
                            slack_coeff = 1
                            minimum_slack.obj = minimum_slack.obj + int(self.rule.penalty * domain.settings.rule_objective)

                        solver.add_constr(xsum(assignment_vars) + superset_assignments + slack_coeff*minimum_slack >= minimum_of_skill,name = 'minimum_of_skill_{}_{}_{}_{}'.format(type_id,minimum_of_skill,current_time,
                                                                                             self.rule.rule_counter))
                    current_time += bucket_size*60

    def add_violation_to_output(self, solver, domain, output):
        minimum_of_skill = int(self.rule.parameter1)
        bucket_size = 15
        if self.rule.parameter2:
            bucket_size = int(self.rule.parameter2)

        has_type_id = True
        if self.rule.department_id:
            type_id = "department_id" + self.rule.department_id
            has_type_id = any([department.id == self.rule.department_id
                               for employee in domain.employees
                               for department in employee.departments])
        if self.rule.skill_id:
            type_id = "skill_id" + self.rule.skill_id
            has_type_id = any([skill.id == self.rule.skill_id
                               for employee in domain.employees
                               for skill in employee.skills])

        if self.rule.license_id:
            type_id = "license_id" + self.rule.license_id
            has_type_id = any([license.id == self.rule.license_id
                               for employee in domain.employees
                               for license in employee.licenses])

        if not has_type_id:
            return

        if self.rule.penalty > 0:
            for day in domain.days:
                if not str(day.weekday) in self.rule.required_times:
                    continue
                current_time = day.date + self.rule.required_times[str(day.weekday)]["minutes_from"]*60
                end_time = day.date + self.rule.required_times[str(day.weekday)]["minutes_to"]*60
                while current_time < end_time and current_time < self.max_ts:
                    if not self.rule.is_mandatory:
                        slack_var = solver.var_by_name(name='minimum_of_skill_{}_{}_{}_{}'.format(type_id, minimum_of_skill, current_time,
                                                                                     self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=current_time,
                                                    parameters={"parameter1": type_id}))

                    current_time += bucket_size*60

    def emp_shift_has_type_id(self, employee, shift, activate_shift_type_id):
        department_ids = employee.department_ids
        license_ids = [str(license.id) for license in employee.licenses]
        skill_ids = [str(skill.id) for skill in employee.skills]
        shift_has_type_id = True
        if activate_shift_type_id:
            shift_license_ids = [str(license.id) for license in shift.shiftLicenses]
            shift_skill_ids = [str(skill.id) for skill in shift.shiftSkills]
            shift_has_type_id = self.rule.department_id == str(shift.departmentId) or self.rule.license_id == shift_license_ids or self.rule.skill_id == shift_skill_ids
        employee_has_type_id = self.rule.department_id in department_ids or self.rule.license_id in license_ids or self.rule.skill_id in skill_ids
        return employee_has_type_id and shift_has_type_id