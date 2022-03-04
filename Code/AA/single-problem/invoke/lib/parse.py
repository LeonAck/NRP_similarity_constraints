from copy import deepcopy
from distutils.util import strtobool
from config import constants
import pytz

def rename_all_keys(dictionary, old_name, new_name):
    if old_name == new_name:
        return
    for value in dictionary.values():
        if isinstance(value, dict):
            rename_all_keys(value, old_name, new_name)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    rename_all_keys(item, old_name, new_name)
    if old_name in dictionary and not new_name in dictionary:
        _rename_key(dictionary, old_name, new_name)

def _rename_key(dictionary, old_name, new_name):
    dictionary[new_name] = dictionary[old_name]
    del dictionary[old_name]

def parse_settings(settings):
    """
    Parses the specified settings to the right format.
    """
    settings = deepcopy(settings)
    if isinstance(settings, list):
        return [parse_settings(settings_item) for settings_item in settings]

    #time
    _parse_value(settings, "start", float)
    _parse_value(settings, "finish", float)
    _parse_value(settings, "time_zone", pytz.timezone)
    #solver properties
    _parse_value(settings, "runtime", int)
    _parse_value(settings, "mip_gap", float)
    _parse_value(settings, "max_nodes", int)
    _parse_value(settings, "max_solutions", int)
    _parse_value(settings, "lp_method", int)
    _parse_value(settings, "emphasis", int)
    _parse_value(settings, "max_mip_gap_abs", float)
    _parse_value(settings, "logging", parse_boolean)
    _parse_value(settings, "linear_relaxation", parse_boolean)
    _parse_value(settings, "preprocess", parse_boolean)
    _parse_value(settings, "pump_passes", int)
    #objectives
    _parse_value(settings, "cost_objective", float)
    _parse_value(settings, "rule_objective", float)
    _parse_value(settings, "fairness_objective", float)
    _parse_value(settings, "proficiency_objective", float)
    _parse_value(settings, "skill_objective", float)
    _parse_value(settings, "use_proficiency_per_hour", parse_boolean)
    #shifting_window
    _parse_value(settings, "run_shifting_window", parse_boolean)
    _parse_value(settings, "shifting_window_day_size", int)
    _parse_value(settings, "fix_window_day_size", int)
    _parse_value(settings, "include_shifts_days", int)
    _parse_value(settings, "fix_drop_ratio", float)
    #shifting_window
    _parse_value(settings, "improve_results", parse_boolean)
    _parse_value(settings, "improve_time_limit", int)
    _parse_value(settings, "acceptance_gap_improvement", float)
    _parse_value(settings, "batch_size", int)
    _parse_value(settings, "number_of_unassigned_shifts", int)
    #remaining
    _parse_value(settings, "use_travel_expenses", parse_boolean)
    _parse_value(settings, "split_skills", parse_boolean)
    _parse_value(settings, "add_subshifts_to_output", parse_boolean)
    _parse_value(settings, "reduce_contract_hours_factor", float)
    _parse_value(settings, "disallow_employee_mix", parse_boolean)

    return settings

def parse_shifts(shifts):
    """
    Parses the specified shifts to the correct format.
    """
    shifts = deepcopy(shifts)
    for shift in shifts:
        _parse_value(shift, "id", str)
        _parse_value(shift, "start", int)
        _parse_value(shift, "end", int)
        _parse_value(shift, "pay_duration", float)
        _parse_value(shift, "break_duration", float)
        _parse_value(shift, "is_fixed", parse_boolean)
        _parse_value(shift, "user_id", str)
        _parse_value(shift, "department_id", str)
        _parse_value(shift, "postal_code", str)
        _parse_value(shift, "group_id", str)
        _parse_value(shift, "break_duration", float)
        _parse_value(shift, "shift_cost", float)

        _parse_value(
            shift,
            "shift_types",
            lambda shift_types: [str(shift_type) for shift_type in shift_types],
        )

        if "skills" in shift:
            for skill in shift["skills"]:
                _parse_value(skill, "id", str)
                _parse_value(skill, "min_level", int)

        if "licenses" in shift:
            for license in shift["licenses"]:
                _parse_value(license, "id", str)

        if "subshifts" in shift:
            for subshift in shift["subshifts"]:
                _parse_value(subshift, "id", str)
                _parse_value(subshift, "start", int)
                _parse_value(subshift, "end", int)
                _parse_value(subshift, "department_id", str)

        if "breaks" in shift:
            for subshift in shift["breaks"]:
                _parse_value(subshift, "start", int)
                _parse_value(subshift, "end", int)
                _parse_value(subshift, "break_duration", float)
                _parse_value(subshift, "isPaid", parse_boolean) ##only input with camelCase

    return shifts

def parse_employees(employees):
    """
    Parses the specified users to the correct format.
    """
    employees = deepcopy(employees)
    for employee in employees:
        _parse_value(employee, "id", str)
        _parse_value_and_none(employee, "start_contract", int)
        _parse_value_and_none(employee, "finish_contract", int)
        _parse_value_and_none(employee, "hourly_rate", float)
        _parse_value(employee, "is_fixed", parse_boolean)
        _parse_value(employee, "postal_code", str)
        _parse_value(employee, "max_weekends", int)
        _parse_value(employee, "free_weekends_quarter", int)
        _parse_value(employee, "free_weekends_month", int)
        _parse_value(employee, "free_weekends_month", int)
        _parse_value(employee, "use_availabilities", parse_boolean)
        _parse_value(employee, "start_first_of_month", parse_boolean)
        _parse_value_and_none(employee, "pay_period_cycle", str)
        _parse_value_and_none(employee, "payperiod_minutes_min", int)
        _parse_value_and_none(employee, "payperiod_minutes_max", int)
        _parse_value(employee, "payperiod_length", int)
        _parse_value(employee, "payperiod_start", int)
        _parse_value(employee, "minimum_time_between_shifts", int)
        _parse_value(employee, "maximum_shift_duration", float)
        _parse_value(employee, "consecutive_shifts", int)
        _parse_value(employee, "previous_hours", int)

        if "department_ids" in employee:
            for department in employee["department_ids"]:
                _parse_value(department, "id", str)
                _parse_value(department, "proficiency_rating", float)
                _parse_value_and_none(department, "from", int)
                _parse_value_and_none(department, "to", int, constants.numbers.infinity)

        if "skills" in employee:
            for skill in employee["skills"]:
                _parse_value(skill, "id", str)
                _parse_value(skill, "level", int)
                _parse_value_and_none(skill, "from", int)
                _parse_value_and_none(skill, "expires", int, constants.numbers.infinity)

        if "licenses" in employee:
            for license in employee["licenses"]:
                _parse_value(license, "id", str)
                _parse_value_and_none(license, "from", int)
                _parse_value_and_none(license, "expires", int, constants.numbers.infinity)

        if "agreements" in employee:
            for agreement in employee["agreements"]:
                _parse_value(agreement, "id", str)
                _parse_value(agreement, "start", int)
                _parse_value(agreement, "end", int)
                _parse_value(agreement, "payperiod_minutes_min", int)
                _parse_value(agreement, "payperiod_minutes_max", int)
                _parse_value(agreement, "payperiod_length", int)
                _parse_value(agreement, "payperiod_days", int)

        ###map unavailability to unavailabilities necessary?
        if "unavailabilities" in employee:
            for unavailability in employee["unavailabilities"]:
                _parse_value(unavailability, "start", int)
                _parse_value(unavailability, "end", int)
                _parse_value(unavailability, "pay_duration", int)
                if "unavailability_workdays" in unavailability:
                    for workday in unavailability["unavailability_workdays"]:
                        _parse_value(workday, "start", int)
                        _parse_value(workday, "end", int)
                        _parse_value(workday, "pay_duration", int)

        if "availabilities" in employee:
            for availability in employee["availabilities"]:
                _parse_value(availability, "start", int)
                _parse_value(availability, "end", int)

        if "shift_type_preferences" in employee:
            for shift_type_preference in employee["shift_type_preferences"]:
                _parse_value(shift_type_preference, "shift_types", lambda shift_types: [str(shift_type) for shift_type in shift_types])
                _parse_value(shift_type_preference, "weight", int)

        if "pay_penalties" in employee:
            for pay_penalty in employee["pay_penalties"]:
                _parse_value(pay_penalty, "penalty", float)
                _parse_value(pay_penalty, "from_date", int)
                _parse_value(pay_penalty, "to_date", int)
                _parse_value(pay_penalty, "shift_type_ids", lambda shift_type_ids: [str(shift_type_id) for shift_type_id in shift_type_ids])
                _parse_value(pay_penalty, "weekdays",
                             lambda weekdays: [str(weekday) for weekday in weekdays])

        if "preferences" in employee:
            for preference in employee["preferences"]:
                _parse_value(preference, "penalty", float)
                _parse_value(preference, "start", int)
                _parse_value(preference, "end", int)
                _parse_value(preference, "type", str)

        if "off_day_preferences" in employee:
            for off_day_preference in employee["off_day_preferences"]:
                _parse_value(off_day_preference, "penalty", float)
                _parse_value(off_day_preference, "start", int)
                _parse_value(off_day_preference, "end", int)
                _parse_value(off_day_preference, "type", str)

        if "shift_counts" in employee:
            for shift_count in employee["shift_counts"]:
                _parse_value(shift_count, "shift_types", lambda shift_types: [str(shift_type) for shift_type in shift_types])
                _parse_value(preference, "weight", int)

    return employees

def parse_rules(rules):
    """
    Parses the specified rules to the correct format.
    """
    rules = deepcopy(rules)
    for rule in rules:
        _parse_value(rule, "rule_id", str)
        _parse_value(rule, "rule_tag", str)
        _parse_to_list(rule, "department_ids")
        _parse_value(
            rule,
            "department_ids",
            lambda department_ids: [str(department_id) for department_id in department_ids],
        )
        _parse_value_and_none(rule, "parameter_1", int)
        _parse_value_and_none(rule, "parameter_2", int)
        _parse_value_and_none(rule, "parameter_3", int)
        _parse_value_and_none(rule, "parameter_4", int)
        _parse_value_and_none(rule, "parameter_5", int)
        _parse_value_and_none(rule, "parameter_6", int)
        _parse_value_and_none(rule, "parameter_7", int)
        _parse_value(rule, "penalty", float)
        _parse_value(rule, "is_mandatory", parse_boolean)
        _parse_to_list(rule, "user_ids")
        _parse_value(
            rule,
            "user_ids",
            lambda user_ids: [str(user_id) for user_id in user_ids],
        )
        _parse_value(
            rule,
            "shift_types",
            lambda shift_types: [str(shift_type) for shift_type in shift_types],
        )
        _parse_value(rule, "department_id", str)
        _parse_value(rule, "department_id_2", str)
        _parse_value(rule, "skill_id", str)
        _parse_value(rule, "skill_id_2", str)
        _parse_value(rule, "license_id", str)
        _parse_value(rule, "license_id_2", str)
        _parse_to_list(rule, "weekdays")
        _parse_value(
            rule,
            "weekdays",
            lambda weekdays: [int(weekday) for weekday in weekdays],
        )
        _parse_value(
            rule,
            "shift_group_ids",
            lambda shift_group_ids: [str(shift_group_id) for shift_group_id in shift_group_ids],
        )
        _parse_value(rule, "rule_start", int)
        _parse_value(rule, "rule_end", int)
        _parse_value(rule, "start_payperiod", int)
        _parse_value(rule, "start_payperiod", int)
        if "required_times" in rule:
            for weekday in rule["required_times"]:
                _parse_key(rule, weekday, str)
                _parse_value(weekday, "minutes_from", int)
                _parse_value(weekday, "minutes_to", int)

        _parse_value(
            rule,
            "special_days",
            lambda special_days: [int(special_day) for special_day in special_days],
        )

    return rules


def parse_shift_types(shift_types):
    """
    Parses the specified shift types to the correct format.
    """
    shift_types = deepcopy(shift_types) if shift_types else []
    for shift_type in shift_types:
        _parse_value(shift_type, "id", str)
        _parse_value(shift_type, "name", str)
        _parse_value(shift_type, "start_after", int)
        _parse_value(shift_type, "start_before", int)
        _parse_value(shift_type, "end_after", int)
        _parse_value(shift_type, "end_before", int)
        _parse_value(shift_type, "minimum_duration", int)

        _parse_value(
            shift_type,
            "weekdays",
            lambda weekdays: [int(weekday) for weekday in weekdays],
        )

    return shift_types

def _parse_key(dictionary, key, parser):
    """
    Replaces the specified key in the dictionary with a key that is parsed by the parser.
    """
    if key in dictionary:
        parsed_key = parser(key)
        dictionary[parsed_key] = dictionary[key]
        if key != parsed_key:
            del dictionary[key]

def _parse_value(dictionary, key, parser):
    """
    Replaces the value in the dictionary with the specifed key with the current value
    that is parsed by the parser.
    """
    if key in dictionary and dictionary[key] is not None:
        dictionary[key] = parser(dictionary[key])

#
def _parse_value_and_none(dictionary, key, parser, value_if_none = 0):
    if key in dictionary:
        if dictionary[key] is None or dictionary[key] == "":
            dictionary[key] = value_if_none
        else:
            dictionary[key] = parser(dictionary[key])

def parse_boolean(value):
    """
    Parses the value to a boolean.
    """
    try:
        return bool(strtobool(value))
    except (ValueError, AttributeError):
        return bool(value)

def _parse_to_list(dictionary, key):
    """
    Parses the value to a boolean.
    """
    if key in dictionary and dictionary[key] is not None:
        if isinstance(dictionary[key], str):
            dictionary[key] = dictionary[key].split(",")
