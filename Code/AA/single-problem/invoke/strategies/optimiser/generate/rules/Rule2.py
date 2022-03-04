from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from lib.parse import parse_boolean
from config import configuration, constants
from strategies.optimiser.output import Violation
from lib.dt import parse_timestamp, start_of_day, end_of_day, addition_timezone_aware, difference_timezone_aware

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule2:
    def __init__(self, rule):
        self.rule = rule
        self.max_value = 18446744073709551615

    def set_rule(self, solver, domain):
        # Rule 2: Do not violate contract hours
        for employee, payperiod_start, payperiod_end, employee_payperiod_minutes_max, agreement_id in self.get_rule_applicable_combinations(domain):
            if self.rule.parameter1 and self.rule.parameter2:
                ##hard coded 2400 minutes is full time
                employee_payperiod_minutes_max = round(
                    self.rule.parameter2 * 60 * (employee_payperiod_minutes_max / 2400))

            factor = float(self.rule.parameter3 / 100) if self.rule.parameter3 else 1

            new_employee_payperiod_minutes_max = max(0, int(factor * (
                        employee_payperiod_minutes_max - employee.get_payduration_unavailabilities(payperiod_start.timestamp(),
                                                                                                   payperiod_end.timestamp()))))

            assignment_vars = [(shift.pay_duration, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                               for shift in
                               employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(payperiod_start,
                                                                                                  payperiod_end).get_rule_applicable_shifts(
                                   self.rule)]

            solver.create_slacked_constraint(
                id=RULES_DEFAULTS[self.rule.tag].id(employee, payperiod_start, agreement_id,
                                                        self.rule.rule_counter),
                constraint_lhs=assignment_vars,
                constraint_sense="<=",
                constraint_rhs=new_employee_payperiod_minutes_max,
                slack_lower_bound=0,
                slack_upper_bound=self.max_value,
                slack_constraint_coeff=-int(not self.rule.is_mandatory),
                slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
            )


    def add_violation_to_output(self, solver, domain, output):
        # max contract hours
        for employee, payperiod_start, payperiod_end, _, agreement_id in self.get_rule_applicable_combinations(domain):
            contract_hours_slack_var = solver.find_slack_variable_constraint(
                RULES_DEFAULTS.max_contract_hours.id(employee, payperiod_start, agreement_id, self.rule.rule_counter))
            if contract_hours_slack_var and contract_hours_slack_var.x > 0:
                output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                        user_id=employee.id,
                                        violation_costs=contract_hours_slack_var.x * contract_hours_slack_var.obj,
                                        date=payperiod_start.timestamp(),
                                        date_time=payperiod_start.strftime(constants.time.date_format),
                                        agreement_id=agreement_id))

    def get_rule_applicable_combinations(self, domain):
        # Rule 2: Do not violate contract hours
        use_input_payperiod = parse_boolean(self.rule.parameter1)
        payperiod_length = int(self.rule.parameter1) if self.rule.parameter1 else 7
        use_custom_minutes = parse_boolean(self.rule.parameter4)
        custom_contract_minutes = self.rule.parameter4 if self.rule.parameter4 else None

        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            if employee.payperiod_minutes_max > 0 or len(employee.agreements) > 0 or use_custom_minutes:
                if len(employee.agreements) > 0:
                    for agreement in employee.agreements:
                        agreement_start = start_of_day(parse_timestamp(agreement.start, domain.settings.time_zone))
                        agreement_end = end_of_day(parse_timestamp(agreement.end if agreement.end else domain.settings.end, domain.settings.time_zone))
                        if not use_input_payperiod and agreement.payperiod_length:
                            payperiod_length = agreement.payperiod_length
                        first_payperiod_schedule = get_first_payperiod_schedule(domain, employee, agreement, agreement_start, payperiod_length)
                        payperiod_start = first_payperiod_schedule
                        while payperiod_start < agreement_end:
                            payperiod_end = min(agreement_end, get_payperiod_end(employee, payperiod_start, payperiod_length, domain.settings.time_zone))
                            if len(domain.days.get_days_in_period(payperiod_start, payperiod_end)) > 0:
                                max_minutes = adjust_minutes(domain,
                                                             custom_contract_minutes if use_custom_minutes else agreement.payperiod_minutes_max,
                                                             payperiod_start, payperiod_end, payperiod_length, agreement.scale_contract_minutes)

                                yield employee, payperiod_start, payperiod_end, max_minutes, agreement.id

                            payperiod_start = payperiod_end
                else:
                    if not use_input_payperiod:
                        payperiod_length = 7
                        if employee.payperiod_length:
                            payperiod_length = employee.payperiod_length

                    payperiod_start = start_of_day(parse_timestamp(employee.payperiod_start if employee.payperiod_start else domain.settings.start, domain.settings.time_zone))
                    settings_end_dt = end_of_day(parse_timestamp(domain.settings.end, domain.settings.time_zone))
                    while payperiod_start < settings_end_dt:
                        payperiod_end = get_payperiod_end(employee, payperiod_start, payperiod_length, domain.settings.time_zone)

                        if len(domain.days.get_days_in_period(payperiod_start, payperiod_end)) > 0:
                            max_minutes = adjust_minutes(domain,
                                                         custom_contract_minutes if use_custom_minutes else employee.payperiod_minutes_max,
                                                         payperiod_start, payperiod_end, payperiod_length)

                            yield employee, payperiod_start, payperiod_end, max_minutes, "no_agreement"

                        payperiod_start = payperiod_end


def get_payperiod_end(employee, payperiod_start, payperiod_length, tz):
    if employee.pay_period_cycle == 'monthly':
        payperiod_end = add_months(payperiod_start, payperiod_length, employee.start_first_of_month)
        return payperiod_end
    else:
        return addition_timezone_aware(payperiod_start, timedelta(days=payperiod_length), tz)


def get_first_payperiod_schedule(domain, employee, agreement, agreement_start, payperiod_length):
    if agreement_start > domain.days[0].date_time:
        return agreement_start
    if employee.pay_period_cycle == 'monthly':
        return domain.days[0].date_time.replace(day=1)
    if agreement.payperiod_start:
        payperiod_start = start_of_day(parse_timestamp(agreement.payperiod_start, domain.settings.time_zone))
        return addition_timezone_aware(domain.days[0].date_time, -timedelta(
            days=(difference_timezone_aware(domain.days[0].date_time, payperiod_start)).days % payperiod_length),
                                       domain.settings.time_zone)
    return addition_timezone_aware(domain.days[0].date_time, -timedelta(
        days=(difference_timezone_aware(domain.days[0].date_time, agreement_start)).days % payperiod_length),
                                   domain.settings.time_zone)


def add_months(original_date, months, start_first_of_month):
    new_date = original_date + relativedelta(months=months)
    if start_first_of_month:
        new_date.replace(day=1)
    return new_date


def adjust_minutes(domain, max_minutes, payperiod_start, payperiod_end, payperiod_length, scale_contract_minutes=False):
    number_of_period_days = len(domain.days.get_days_in_period(payperiod_start, payperiod_end))
    if number_of_period_days < payperiod_length and scale_contract_minutes:
        return int(max_minutes * number_of_period_days / payperiod_length)
    return max_minutes
