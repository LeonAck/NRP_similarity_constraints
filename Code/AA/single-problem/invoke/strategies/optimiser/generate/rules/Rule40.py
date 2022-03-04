from datetime import datetime, timedelta
from mip import xsum
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean
from config import constants, configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables


class Rule40:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        # the block rule with custom domain.days for Friday/Saturday, Saturday/Sunday, Sunday/Monday
        day_combinations_to_check = [[4, 5], [5, 6], [6, 0]]
        minimum_number_of_times_in_period = int(self.rule.parameter1)

        for employee, day, payperiod_length in self.get_rule_applicable_combinations(domain):
            off_on_days_variable_mapping = {}
            for day_combination_to_check in day_combinations_to_check:
                for first_day_weekend in domain.days.get_days_in_payperiod(day,
                                                                           payperiod_length).get_first_day_weekends(
                        day_combination_to_check):
                    duration = 2 if first_day_weekend.weekday == day_combination_to_check[0] else 1
                    if first_day_weekend.weekday == day_combination_to_check[0]:
                        week_number = int(first_day_weekend.date_time.isocalendar()[1])
                    elif day_combination_to_check[1] < day_combination_to_check[0]:
                        week_number = int(first_day_weekend.date_time.isocalendar()[1]) - 1 if int(
                            first_day_weekend.date_time.isocalendar()[1]) - 1 >= 1 else 52

                    if week_number not in off_on_days_variable_mapping:
                        off_on_days_variable_mapping[week_number] = []

                    shifts_rule = employee.eligible_shifts_in_schedule.get_rule_applicable_shifts(
                        self.rule).get_shifts_starts_in_interval(first_day_weekend.date,
                                                                 first_day_weekend.date + int(
                        duration * constants.time.seconds_per_day))

                    if first_day_weekend.date + int((duration-1) * constants.time.seconds_per_day) <= domain.settings.end:
                        left_hand_side = [(1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))) for shift
                                          in shifts_rule]
                        constraint_text = RULES_DEFAULTS[self.rule.tag].help_constr_id_1(employee, first_day_weekend, day,
                                                                                         self.rule.rule_counter)

                        # First, per weekend we create a constraint to check if both days are off
                        _, both_days_off_variable = solver.create_slacked_constraint(
                            id=constraint_text,
                            constraint_lhs=left_hand_side,
                            constraint_sense="<=",
                            constraint_rhs=1000,
                            slack_lower_bound=0,
                            slack_upper_bound=1,
                            slack_constraint_coeff=1000,
                            slack_objective_coeff=0
                        )
                        off_on_days_variable_mapping[week_number].append(both_days_off_variable)

            free_period_variables = []
            for week_number in off_on_days_variable_mapping:
                constraint_text = RULES_DEFAULTS[self.rule.tag].help_constr_id_2(employee, week_number, day,
                                                                                 self.rule.rule_counter)
                left_hand_side = [(1, variable) for variable in off_on_days_variable_mapping[week_number]]
                # Next, per week we create a constraint to check if there is a free period
                _, free_period_variable = solver.create_slacked_constraint(
                    id=constraint_text,
                    constraint_lhs=left_hand_side,
                    constraint_sense=">=",
                    constraint_rhs=0,
                    slack_lower_bound=0,
                    slack_upper_bound=1,
                    slack_constraint_coeff=-1,
                    slack_objective_coeff=0
                )
                free_period_variables.append(free_period_variable)

            left_hand_side = [(1, free_period_variable) for free_period_variable in free_period_variables]
            constraint_text = RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter)
            # Finally, we add all free period variables, to make sure the minimum is met
            solver.create_slacked_constraint(
                id=constraint_text,
                constraint_lhs=left_hand_side,
                constraint_sense=">=",
                constraint_rhs=minimum_number_of_times_in_period,
                slack_lower_bound=0,
                slack_upper_bound=len(domain.days),
                slack_constraint_coeff=int(not self.rule.is_mandatory),
                slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
            )

    def add_violation_to_output(self, solver, domain, output):
        for employee, day, payperiod_length in self.get_rule_applicable_combinations(domain):
            slack_var = solver.find_slack_variable_constraint(
                RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter))
            if slack_var and slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                        user_id=employee.id,
                                        violation_costs=slack_var.x * slack_var.obj))

    def get_rule_applicable_combinations(self, domain):
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            payperiod_length = 7
            if employee.payperiod_length:
                payperiod_length = employee.payperiod_length
            if self.rule.parameter2:
                payperiod_length = self.rule.parameter2
            rule_step_size = payperiod_length
            if self.rule.parameter6:
                rule_step_size = self.rule.parameter6
            for day in domain.days.get_start_days_for_steps(rule_step_size, self.rule.period_start, self.rule.period_end).get_rule_applicable_days(self.rule):
                yield employee, day, payperiod_length
