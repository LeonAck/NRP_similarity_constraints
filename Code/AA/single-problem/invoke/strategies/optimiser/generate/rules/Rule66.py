from datetime import timedelta
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean
from mip import xsum

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables


def create_shift_type_map(shifts, shift_types_to_check_for):
    shift_type_map = {}
    for shift in shifts:
        for shift_type in shift.shift_types:
            if (not shift_types_to_check_for or len(shift_types_to_check_for) == 0) or shift_type.id in shift_types_to_check_for:
                if shift_type.id not in shift_type_map:
                    shift_type_map[shift_type.id] = []
                shift_type_map[shift_type.id].append(shift)
    return shift_type_map


### Note that this does not work in case a shift has multiple shift types, to be implemented later
class Rule66:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            period_to_check_for = self.rule.parameter1
            maximum_different_shift_types = self.rule.parameter2

            # minimize number of different shift types per week
            shift_type_map = create_shift_type_map(domain.shifts, self.rule.shift_types)

            for employee in domain.employees:
                for index, day in enumerate(domain.days):
                    if index / period_to_check_for % 1 == 0 and self.rule.is_applicable_day(day.date):
                        has_shift_of_type_vars = []
                        if len(shift_type_map.keys()) > 1:
                            for shift_type in shift_type_map.keys():
                                # Per shift_type we create a help variable
                                has_shift_of_type_var = solver.add_var(
                                    name='has_shift_of_type_{}_{}_{}_{}'.format(employee.id, day.date, shift_type,
                                                                                self.rule.rule_counter), var_type='B')
                                shift_of_type_vars = []
                                has_shift_of_type_vars.append(has_shift_of_type_var)
                                for shift in shift_type_map[shift_type]:
                                    if employee.is_eligible(shift) and domain.days[index].date <= shift.start < domain.days[index].date + \
                                            int(timedelta(days=period_to_check_for).total_seconds()):
                                        shift_employee_variable = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                                        if shift_employee_variable:
                                            shift_of_type_vars.append(shift_employee_variable)

                                solver.add_constr(xsum(shift_of_type_vars) <= 1000 * has_shift_of_type_var,
                                                  name='has_shift_of_type_constraint_{}_{}_{}_{}'.format(employee.id,
                                                                                                         shift_type, index,
                                                                                                         self.rule.rule_counter))

                            slack_var = solver.add_var(lb=0, ub=len(shift_type_map.keys()),
                                                       name='maximum_diff_shift_types_slack_{}_{}_{}'.format(employee.id,
                                                                                                            index,
                                                                                                            self.rule.rule_counter))
                            if not self.rule.is_mandatory:
                                slack_coefficient = -1
                                slack_var.obj = self.rule.penalty * domain.settings.rule_objective
                            solver.add_constr(xsum(
                                has_shift_of_type_vars) + slack_coefficient * slack_var <= maximum_different_shift_types,
                                              name='maximum_diff_shift_types_{}_{}_{}'.format(employee.id, index,
                                                                                              self.rule.rule_counter))

    def add_violation_to_output(self, solver, domain, output):
        if self.rule.penalty > 0 and not self.rule.is_mandatory:
            shift_type_map = create_shift_type_map(domain.shifts, self.rule.shift_types)
            period_to_check_for = self.rule.parameter1
            maximum_different_shift_types = self.rule.parameter2

            for employee in domain.employees:
                for index, day in enumerate(domain.days):
                    if index / period_to_check_for % 1 == 0 and self.rule.is_applicable_day(day.date):
                        slack_var = solver.var_by_name(
                            'maximum_diff_shift_types_slack_{}_{}_{}'.format(employee.id, index, self.rule.rule_counter))
                        if slack_var and slack_var.x > 0:
                            violation_shifts = []
                            for shift_type in shift_type_map.keys():
                                for shift in shift_type_map[shift_type]:
                                    if employee.is_eligible(shift) and domain.days[index].date <= shift.start < domain.days[
                                        index].date + int(timedelta(days=period_to_check_for).total_seconds()):
                                        violation_shifts.append(shift)

                            output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                    user_id=employee.id,
                                                    violation_costs=slack_var.x * slack_var.obj,
                                                    date=day.date,
                                                    violation_description=generate_violation_text(maximum_different_shift_types, day.date,
                                                                      period_to_check_for)))

def generate_violation_text(maximum_different_shift_types, starting_period, period_to_check_for):
    return "More than {} different shift types in the period of {} days starting on {}".format(
        maximum_different_shift_types,
        period_to_check_for,
        starting_period)
