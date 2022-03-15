from datetime import datetime, timedelta
import pytz
from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule58:
    def __init__(self, rule):
        self.rule = rule

    # bonus if working 0 or >= 2 domain.shifts in a weekend
    def set_rule(self, solver, domain):
        for employee, day in self.get_rule_applicable_combinations(domain):
            week_day = day.weekday
            if week_day == 5:
                start_saturday = day.date
                end_saturday = start_saturday + 24 * 60 * 60
                start_sunday = day.date + 24 * 60 * 60
                end_sunday = start_sunday + 29.5 * 60 * 60
                saturday_shifts = [shift for shift in employee.eligible_shifts_in_schedule if
                                   (start_saturday < shift.start < end_saturday) or (
                                               3 in shift.shift_types and start_saturday < shift.end < end_saturday)]
                sunday_shifts = [shift for shift in employee.eligible_shifts_in_schedule if (start_sunday < shift.start < end_sunday)]
                saturday_vars, sunday_vars = [], []
                for shift in saturday_shifts:
                    shiftEmployeeVariable = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))

                    if shiftEmployeeVariable:
                        saturday_vars.append(shiftEmployeeVariable)

                for shift in sunday_shifts:
                    shiftEmployeeVariable = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))

                    if shiftEmployeeVariable:
                        sunday_vars.append(shiftEmployeeVariable)

                is_off_saturday_var = solver.add_var(name='is_off_saturday_{}_{}'.format(employee.id, day.date),
                                                     var_type='B')
                works_on_saturday_var = solver.add_var(name='works_on_saturday_{}_{}'.format(employee.id, day.date),
                                                       var_type='B')
                solver.add_constr(1000 * works_on_saturday_var - xsum(saturday_vars) >= 0,
                                  name='worksOnSaturdayConstraint_{}_{}'.format(employee.id, day.date))
                solver.add_constr(xsum(saturday_vars) + 1000 * is_off_saturday_var >= 1,
                                  name='isOffSaturday_{}_{}'.format(employee.id, day.date))
                solver.add_constr(is_off_saturday_var + works_on_saturday_var == 1,
                                  name='equalitySaturdayConstraint_{}_{}'.format(employee.id, day.date))

                is_off_sunday_var = solver.add_var(name='is_off_sunday_{}_{}'.format(employee.id, day.date),
                                                   var_type='B')
                works_on_sunday_var = solver.add_var(name='works_on_sunday_{}_{}'.format(employee.id, day.date),
                                                     var_type='B')
                solver.add_constr(1000 * works_on_sunday_var - xsum(sunday_vars) >= 0,
                                  name='worksOnSundayConstraint_{}_{}'.format(employee.id, day.date))
                solver.add_constr(xsum(sunday_vars) + 1000 * is_off_sunday_var >= 1,
                                  name='isOffSunday_{}_{}'.format(employee.id, day.date))
                solver.add_constr(is_off_sunday_var + works_on_sunday_var == 1,
                                  name='equalitySundayConstraint_{}_{}'.format(employee.id, day.date))

                weekend_slack_var_1 = solver.add_var(name='{}_{}_work_one_day_slack_1'.format(employee.id, day.date),
                                                     var_type='B')
                weekend_slack_var_2 = solver.add_var(name='{}_{}_work_one_day_slack_2'.format(employee.id, day.date),
                                                     var_type='B')
                weekend_slack_var_1.obj = self.rule.penalty * domain.settings.rule_objective
                weekend_slack_var_2.obj = self.rule.penalty * domain.settings.rule_objective

                solver.add_constr(
                    works_on_saturday_var - works_on_sunday_var + weekend_slack_var_1 - weekend_slack_var_2 == 0,
                    'one_of_two_days_constraint_{}_{}'.format(day.date, employee.id))


    def add_violation_to_output(self, solver, domain, output):
        for employee, day in self.get_rule_applicable_combinations(domain):
            week_day = day.weekday
            if week_day == 5:
                slack_var1 = solver.var_by_name('{}_{}_work_one_day_slack_1'.format(employee.id, day.date))
                slack_var2 = solver.var_by_name('{}_{}_work_one_day_slack_2'.format(employee.id, day.date))
                if slack_var1 and slack_var1.x > 0:
                   output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                            user_id=employee.id,
                                            violation_costs=slack_var1.x * slack_var1.obj,
                                            date=day.date))
                if slack_var2 and slack_var2.x > 0:
                    output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                            user_id=employee.id,
                                            violation_costs=slack_var2.x * slack_var2.obj,
                                            date=day.date))

    def get_rule_applicable_combinations(self, domain):
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            for day in domain.days:
                yield employee, day