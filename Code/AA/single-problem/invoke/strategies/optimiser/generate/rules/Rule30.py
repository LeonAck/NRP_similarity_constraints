from datetime import timedelta
from config import configuration, constants
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean
from lib.dt import addition_timezone_aware

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables
CONSTANTS = constants

# Rule 30: Maximum work domain.days in payperiod
class Rule30:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        max_days = self.rule.parameter1
        use_shifts = parse_boolean(self.rule.parameter2)
        rule_step_size_days = self.rule.parameter4 if self.rule.parameter4 else 1

        for employee in domain.employees:
            if self.rule.penalty > 0 and not employee.is_fixed and self.rule.is_applicable(None, employee):
                pay_period_length = 7
                if self.rule.parameter3:
                    pay_period_length = self.rule.parameter3
                elif employee.payperiod_length:
                    pay_period_length = employee.payperiod_length

                for day in domain.days.get_start_days_for_steps(rule_step_size_days, self.rule.period_start, self.rule.period_end).get_rule_applicable_days(self.rule):
                    if use_shifts:
                        left_hand_side_vars = [
                            (1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                            for shift in employee.unfixed_eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date_time, addition_timezone_aware(day.date_time, timedelta(days=pay_period_length), domain.settings.time_zone))
                        ]
                        for day_in_payperiod in domain.days.get_days_in_period(day.date_time, addition_timezone_aware(day.date_time, timedelta(days=pay_period_length), domain.settings.time_zone)):
                            fixed_shifts_day = [shift for shift in
                                            employee.fixed_shifts_in_schedule.get_shifts_starts_in_interval(day_in_payperiod.date_time,
                                                                                                            addition_timezone_aware(day_in_payperiod.date_time, timedelta(days=1), domain.settings.time_zone))]
                            if len(fixed_shifts_day) > 0:
                                left_hand_side_vars.append((1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, fixed_shifts_day[0]))))
                    else:
                        left_hand_side_vars = [
                            (1, solver.find_variable(VAR_DEFAULTS.works_on.id(employee, day)))
                            for day in domain.days.get_days_in_period(day.date, day.date + pay_period_length * CONSTANTS.time.seconds_per_day)
                        ]

                    solver.create_slacked_constraint(
                        id=RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter),
                        constraint_lhs=left_hand_side_vars,
                        constraint_sense="<=",
                        constraint_rhs=max_days,
                        slack_lower_bound=0,
                        slack_upper_bound=100,
                        slack_constraint_coeff=-int(not self.rule.is_mandatory),
                        slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
                    )

    def add_violation_to_output(self, solver, domain, output):
        for employee in domain.employees:
            if self.rule.penalty > 0 and not self.rule.is_mandatory and not employee.is_fixed and self.rule.is_applicable(None, employee):
                for day in domain.days:
                    slack_var = solver.find_slack_variable_constraint(
                        RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter))
                    if slack_var and slack_var.x > 0:
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                     user_id=employee.id,
                                                     violation_costs=slack_var.x * slack_var.obj,
                                                     date=day.date))
