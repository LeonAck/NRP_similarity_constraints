from datetime import timedelta
from config import configuration, constants
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables


class Rule25:
    """
    Generates constraints and violations for each employee and period.
    Each constraint sets a maximum to the number of contract hours for the applicable employees for a specific period.
    Violation (if any) indicates the number of minutes the employee is over contract hours in a period.

    Parameters
    ----------
    rule : Rule object
        rule object that defines specific properties of the rule

        Rule properties
        ----------
        parameter1 : maximum working minutes: the maximum time in minutes per pay period
        parameter2 : pay period length: The period of days over which the rule will be set
        parameter3 : minimum shifts of type: the minimum number of shifts in a pay period in order to set the rule
        parameter4 : shift type id rule: the id of the shift type for which a minimum should hold
        parameter5 : use previous hours: incorporate the previous_hours field on employees
        parameter6 : shifting window size: the step size in days to increment per time to set the rule
    """

    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        for employee, day, pay_period_length in self._get_rule_applicable_combinations(domain):
            self._add_constraint_to_solver(solver, domain, employee, day, pay_period_length)

    def add_violation_to_output(self, solver, domain, output):
        for employee, day, pay_period_length in self._get_rule_applicable_combinations(domain):
            if solver.positive_slack_var(
                    RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter)):
                output.append(self._generate_violation(solver, employee, day, pay_period_length))

    def _get_rule_applicable_combinations(self, domain):
        pay_period_length = self.rule.parameter2 if self.rule.parameter2 else RULES_DEFAULTS[
            self.rule.tag].pay_period_length_default
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            if not self.rule.parameter2 and employee.payperiod_length:
                pay_period_length = employee.payperiod_length
            shifting_window_size = self.rule.parameter6 if self.rule.parameter6 else pay_period_length
            for day in domain.days.get_start_days_for_steps(shifting_window_size, self.rule.period_start,
                                                            self.rule.period_end).get_rule_applicable_days(self.rule):
                yield employee, day, pay_period_length

    def _add_constraint_to_solver(self, solver, domain, employee, day, pay_period_length):
        maximum_working_minutes = self.rule.parameter1
        minimum_shifts_of_type = self.rule.parameter3
        shift_type_rule = self.rule.parameter4
        use_prev_hours = parse_boolean(self.rule.parameter5)
        previous_minutes = int(use_prev_hours) * employee.previous_hours * constants.time.minutes_per_hour
        minimum_shifts_of_type = minimum_shifts_of_type - employee.shifts_of_type
        end_period = domain.days.get_ts_day_index(day.day_number_in_schedule + pay_period_length)

        shifts_in_pay_period = [shift for shift in
                                employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date,
                                                                                                   end_period).get_rule_applicable_shifts(
                                    self.rule)]
        shifts_of_type_in_pay_period = [shift for shift in shifts_in_pay_period if
                                        shift_type_rule in shift.shift_types]

        shift_type_slack_var = 1 if shift_type_rule else 0
        # do not create min and max shift type constraints if constraint not feasible, shift type slack var is 1
        if shift_type_rule and len(shifts_of_type_in_pay_period) >= minimum_shifts_of_type:
            shift_type_slack_var = self._create_shift_type_slack_var(solver, employee, day, shifts_in_pay_period,
                                                                     shifts_of_type_in_pay_period,
                                                                     minimum_shifts_of_type)

        assignment_vars = [
            (shift.pay_duration, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
            for shift in shifts_in_pay_period
        ]

        # shift type slack var is 0 if minimum of shift type is reached, and if not reached 1
        assignment_vars.append((-sum([shift.pay_duration for shift in shifts_in_pay_period]), shift_type_slack_var))

        unavailability_duration = employee.get_payduration_unavailabilities(day.date, end_period)
        solver.create_slacked_constraint(
            id=RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter),
            constraint_lhs=assignment_vars,
            constraint_sense="<=",
            constraint_rhs=maximum_working_minutes - previous_minutes - unavailability_duration,
            slack_lower_bound=0,
            slack_upper_bound=constants.numbers.infinity,
            slack_constraint_coeff=0 if self.rule.is_mandatory else -1,
            slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
        )

    def _create_shift_type_slack_var(self, solver, employee, day, shifts_in_pay_period, shifts_of_type_in_pay_period,
                                     minimum_shifts_of_type):
        assignment_vars_shift_type = [
            (1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
            for shift in shifts_of_type_in_pay_period
        ]
        _, shift_type_slack_var = solver.create_slacked_constraint(
            id=RULES_DEFAULTS[self.rule.tag].shifts_of_type_min(employee, day, self.rule.rule_counter),
            constraint_lhs=assignment_vars_shift_type,
            constraint_sense=">=",
            constraint_rhs=minimum_shifts_of_type,
            slack_lower_bound=0,
            slack_upper_bound=1,
            slack_constraint_coeff=len(shifts_in_pay_period) - minimum_shifts_of_type + 1,
            slack_objective_coeff=0
        )
        assignment_vars_shift_type.append(
            (len(shifts_in_pay_period) - minimum_shifts_of_type + 1, shift_type_slack_var))
        solver.create_slacked_constraint(
            id=RULES_DEFAULTS[self.rule.tag].shifts_of_type_max(employee, day, self.rule.rule_counter),
            constraint_lhs=assignment_vars_shift_type,
            constraint_sense="<=",
            constraint_rhs=len(shifts_in_pay_period),
            slack_lower_bound=0,
            slack_upper_bound=0,
            slack_constraint_coeff=0,
            slack_objective_coeff=0,
        )
        return shift_type_slack_var

    def _generate_violation(self, solver, employee, day, pay_period_length):
        end_period = min(day.date + int(timedelta(days=pay_period_length).total_seconds()),
                         self.rule.period_end)
        shifts_in_pay_period = [shift for shift in
                                employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date,
                                                                                                   end_period).get_rule_applicable_shifts(
                                    self.rule)]
        violation_shift_ids = [shift.id for shift in shifts_in_pay_period if
                               solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
        return Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                         user_id=employee.id,
                         violation_costs=solver.get_violation_costs_slack_var(
                             RULES_DEFAULTS[self.rule.tag].id(employee, day, self.rule.rule_counter)),
                         date=day.date,
                         relevant_shifts=violation_shift_ids,
                         violation_description=generate_violation_text(self.rule.parameter1,
                                                                       pay_period_length, str(day)),
                         parameters=self.rule.get_parameters())


def generate_violation_text(maximum_minutes, period_length, start_date):
    return f"More than {round(maximum_minutes / constants.time.minutes_per_hour, 2)} working hours in the period of {period_length} days starting on {start_date}"
