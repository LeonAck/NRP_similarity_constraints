from config import constants, configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule18:
    def __init__(self, rule):
        self.rule = rule
        self.maxValue = 18446744073709551615

    def set_rule(self, solver, domain):
        # the weekend block rule per payperiod
        checkShiftTypes = parse_boolean(self.rule.parameter1)
        shift_type = str(self.rule.parameter1)
        use_start_times = not parse_boolean(self.rule.parameter3)
        minutes_after_last_day = int(self.rule.parameter4) if self.rule.parameter4 else 0
        minutes_before_first_day = int(self.rule.parameter7) if self.rule.parameter7 else 0

        max_weekends = int(self.rule.parameter2)
        # create variables for the entire pay period to see if there are domain.shifts of the specified shift type in the roster

        weekdays_combination = self.rule.weekdays if self.rule.weekdays else [5, 6]

        for employee, day, payperiod_length in self.get_rule_applicable_combinations(domain):
            if employee.max_weekends:
                max_weekends = employee.max_weekends
            work_weekend_vars = []

            for first_day_weekend in domain.days.get_days_in_payperiod(day, payperiod_length).get_first_day_weekends(weekdays_combination):
                duration = 2 if first_day_weekend.weekday == weekdays_combination[0] else 1

                shifts_rule = employee.eligible_shifts_in_schedule.get_rule_applicable_shifts(self.rule)

                start_interval = first_day_weekend.date - int(minutes_before_first_day * constants.time.seconds_per_minute)
                end_interval = first_day_weekend.date + int(duration * constants.time.seconds_per_day + minutes_after_last_day * constants.time.seconds_per_minute)
                if use_start_times:
                    shifts_rule = shifts_rule.get_shifts_starts_in_interval(start_interval, end_interval)
                else:
                    shifts_rule = shifts_rule.get_shifts_eq_in_interval(start_interval, end_interval)
                    #get_shifts_in_interval is different from original rule 18 implementation filter
                if checkShiftTypes:
                    shifts_rule = shifts_rule.get_shifts_of_type(shift_type)

                left_hand_side = [(-1,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))) for shift in shifts_rule]
                _, works_weekend_var = solver.create_slacked_constraint(
                    id=RULES_DEFAULTS[self.rule.tag].help_constr_id(employee, day, first_day_weekend,self.rule.rule_counter),
                    constraint_lhs=left_hand_side,
                    constraint_sense=">=",
                    constraint_rhs=0,
                    slack_lower_bound=0,
                    slack_upper_bound=1,
                    slack_constraint_coeff=1000,
                    slack_objective_coeff=0
                )
                work_weekend_vars.append((1,works_weekend_var))

            if len(work_weekend_vars) > 0:
                # this is where we create the constraint. We add the variables of the previous block + slack <= maximum number of items in the payperiod
                solver.create_slacked_constraint(
                    id=RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter),
                    constraint_lhs=work_weekend_vars,
                    constraint_sense="<=",
                    constraint_rhs=max_weekends,
                    slack_lower_bound=0,
                    slack_upper_bound=len(domain.days),
                    slack_constraint_coeff=-int(not self.rule.is_mandatory),
                    slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
                )

    def add_violation_to_output(self, solver, domain, output):
        for employee, day, _ in self.get_rule_applicable_combinations(domain):
            slack_var = solver.find_slack_variable_constraint(RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter))
            if slack_var and slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                user_id=employee.id,
                                                violation_costs=slack_var.x * slack_var.obj))

    def get_rule_applicable_combinations(self, domain):
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            payperiod_length = 7
            if employee.payperiod_length:
                payperiod_length = employee.payperiod_length
            if self.rule.parameter5:
                payperiod_length = self.rule.parameter5
            rule_step_size = payperiod_length
            if self.rule.parameter6:
                rule_step_size = self.rule.parameter6
            for day in domain.days.get_start_days_for_steps(rule_step_size, self.rule.period_start, self.rule.period_end).get_rule_applicable_days(self.rule):
                yield employee, day, payperiod_length