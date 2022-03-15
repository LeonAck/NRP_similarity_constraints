from dotmap import DotMap
import pytz
import math

constants = DotMap(
    {
        "time": {
            "milliseconds_per_second": 1000,
            "minutes_per_day": 1440,
            "minutes_per_hour": 60,
            "seconds_per_day": 86400,
            "seconds_per_hour": 3600,
            "seconds_per_minute": 60,
            "weekdays": [0, 1, 2, 3, 4, 5, 6],
            "date_format": '%Y.%m.%d_%H_%M_%S',
        },
        "numbers": {
            "infinity": math.inf
        }
    }
)

rule_mapping_by_tag = DotMap(
    {
        "no_overlapping_shifts": "0",
        "shift_assignment": "1",
        "max_contract_hours": "2",
        "max_consecutive_working_days": "3",
        "min_consecutive_resting_days": "4",
        "min_rest_time_between_shifts": "5",
        "not_used1": "6",
        "max_working_days": "7",
        "earliest_shift_start": "8",
        "latest_shift_end": "9",
        "max_shift_length": "10",
        "min_shift_length": "11",
        "max_employees_per_day": "12",
        "max_minutes_per_day": "13",
        "min_contract_hours": "14",
        "max_shifts_per_day": "15",
        "shift_break_correct_timing_and_length": "16",
        "shift_type_preference": "17",
        "max_weekends": "18",
        "preassigned_employees": "19",
        "working_time_preference": "20",
        "equal_hour_distribution": "21",
        "equal_shift_type_distribution": "22",
        "min_rest_time_period1": "23",
        "min_consecutive_days_off_input_period": "24",
        "max_working_time": "25",
        "consecutive_shift_types": "26",
        "rest_work_rest": "27",
        "work_rest_work": "28",
        "max_shifts_of_type": "29",
        "max_working_days_shifting": "30",
        "shift_type_followed_by_shift_type_or_rest_period": "31",
        "min_rest_time_period2": "32",
        "equal_start_time_sequential_days1": "33",
        "equal_distrubution_shifts": "34",
        "equal_start_time_sequential_days2": "35",
        "max_weekends_input_period": "36",
        "max_special_days": "37",
        "shift_type_before_dayoff": "38",
        "shift_type_after_dayoff": "39",
        "min_number_of_weekday_combinations_off": "40",
        "not_used3": "41",
        "min_rest_period_exceptions": "42",
        "min_rest_after_shift_type": "43",
        "shift_of_type_proceeded_and_followed_by_shift_type": "41",
        "min_rest_after_series_of_shift_types": "45",
        "min_break_duration": "46",
        "min_rest_with_split": "47",
        "max_length_series_including_shift_type": "48",
        "notused4": "49",
        "single_shift_of_type": "50",
        "not_used5": "51",
        "min_free_sundays": "52",
        "one_of_two_weekdays_per_week": "53",
        "same_shift_type_after_X_days": "54",
        "no_shift_typeX_after_shift_typeY": "55",
        "min_free_days": "56",
        "min_X_times_consecutive_daysoff": "57",
        "connected_weekends": "58",
        "preference_off_time": "59",
        "min_employees_with_skill_for_required_times": "60",
        "max_time_within_interval": "61",
        "min_employees_with_skill_in_shift_group": "62",
        "after_shift_type_free_or_same_type": "63",
        "min_shifts_of_type": "64",
        "skill_difficulty_difference": "65",
        "max_different_shift_types": "66",
        "min_shifts_in_shift_group": "67",
        "max_shifts_in_shift_group": "68",
        "min_hours_per_day": "69",
        "min_working_time": "70",
    }
)
rule_mapping_by_id = {y:x for x,y in rule_mapping_by_tag.iteritems()}

configuration = DotMap(
    {
        "domain": {
            "settings": {
                "defaults": {
                    "start": 0,
                    "end": 9999999999,
                    "time_zone": pytz.utc,
                    "cost_objective": 1,
                    "rule_objective": 1,
                    "fairness_objective": 0,
                    "skill_objective": 0,
                    "proficiency_objective": 0,
                    "use_proficiency_per_hour": False,
                    "use_travel_expenses": False,
                    "split_skills": False,
                    "reduce_contract_hours_factor": 1,
                    "number_of_unassigned_shifts": 75,
                    "runtime": 10,
                    "seed": 0,
                    "logging": False,
                    "linear_relaxation": False,
                    "preprocess": -1,
                    "search_progress_log_size": 5,
                    "run_shifting_window": False,
                    "shifting_window_day_size": 28,
                    "fix_window_day_size": 28,
                    "include_shifts_days": 28,
                    "return_shifting_window_results": False,
                    "fix_drop_ratio": 0.10,
                    "improve_results": False,
                    "improve_time_limit": 600,
                    "acceptance_gap_improvement": 0.0001
                },
            },
            "shift": {
                "defaults": {
                    "is_fixed": False,
                    "break_duration": 0,
                    "pay_multiplication_factor": 1,
                    "shift_skill": {
                        "min_level": 0,
                        "difficulty": 0
                    }
                }
            },
            "employee": {
                "defaults": {
                    "start_contract": 0,
                    "finish_contract": 0,
                    "hourly_rate": 0,
                    "is_fixed": False,
                    "use_availabilities": False,
                    "start_first_of_month": True,
                    "pay_period_cycle": "daily",
                    "payperiod_minutes_min": 0,
                    "payperiod_minutes_max": 0,
                    "minimum_time_between_shifts": 600,
                    "payperiod_length": 7,
                    "previous_consecutive_shifts": 0,
                    "previous_hours": 0,
                    "shifts_of_type": 0
                }
            },
            "rule": {
                "defaults": {
                    "rule_counter": 0,
                    "penalty": 0,
                    "parameter_1": 0,
                    "parameter_2": 0,
                    "parameter_3": 0,
                    "parameter_4": 0,
                    "parameter_5": 0,
                    "parameter_6": 0,
                    "parameter_7": 0,
                    "is_mandatory": False,
                    "is_fixed": False,
                    "user_ids": None,
                    "department_id": None,
                    "department_id_2": None,
                    "shift_types": None,
                    "skill_id": None,
                    "skill_id_2": None,
                    "license_id": None,
                    "license_id_2": None,
                    "weekdays": None,
                    "shift_group_ids": None,
                    "rule_start": 0,
                    "rule_end": 9999999999,
                    "period_start": 0,
                    "period_end": 9999999999,
                    "start_payperiod": None,
                    "required_times": None,
                    "special_days": [],
                    "improvement_heuristic_only": True,
                    "is_active": True,
                },
                "rule0": {
                    "rule_id": "0", "parameter_1": 0, "parameter_2": 0, "parameter_3": 0, "penalty": 10000,
                    "is_mandatory": True
                }
            },
            "shift_type": {
                "defaults": {
                    "is_fixed": False
                }
            },
        },
            "optimiser": {
                "variables": {
                    "assignment": {
                        "id": lambda employee, shift: f"assignment_{employee.id}_{shift.id}",
                        "lower_bound": lambda employee, shift: int(shift.is_fixed and shift.employee_id == employee.id),
                        "upper_bound": 1,
                    },
                    "works_on": {
                        "id": lambda employee, day: f"works_on_{employee.id}_{str(day)}",
                        "lower_bound": 0,
                        "upper_bound": 1,
                    },
                    "is_off": {
                        "id": lambda employee, day: f"is_off_{employee.id}_{str(day)}",
                        "lower_bound": 0,
                        "upper_bound": 1,
                    }
                },
                "constraints": {
                    "works_on": {
                        "id": lambda employee, day: f"works_on_{employee.id}_{str(day)}",
                    },
                    "is_off": {
                        "id": lambda employee, day: f"is_off_{employee.id}_{str(day)}",
                    },
                    "equality_works_on_off": {
                        "id": lambda employee, day: f"equality_works_on_off{employee.id}_{str(day)}",
                    },
                    "disallow_employee_mix": {
                        "id": lambda employee, shift: f"disallow_employee_mix{employee.id}_{shift.id}",
                    },
                },
                "rules": {
                    "no_overlapping_shifts": {
                        "batch_constraint": {
                            "id": lambda employee, shift, rule_counter: f"no_overlapping_shifts_{employee.id}_{shift.id}_{rule_counter}",
                        },
                        "singular_constraint": {
                            "id": lambda employee, shift_i, shift_j, rule_counter: f"no_overlapping_shifts_{employee.id}_{shift_i.id}_{shift_j.id}_{rule_counter}",
                        }
                    },
                    "shift_assignment": {
                        "id": lambda shift, rule_counter: f"shift_assignment_{shift.id}_{rule_counter}"
                    },
                    "max_contract_hours": {
                        "id": lambda employee, payperiod_start, agreement_id, rule_counter: f"max_contract_hours_{employee.id}_{str(payperiod_start.strftime(constants.time.date_format))}_{agreement_id}_{rule_counter}",
                    },
                    "max_consecutive_working_days": {
                        "id": lambda employee, day, rule_counter: f"max_consecutive_working_days{employee.id}_{str(day)}_{rule_counter}",
                    },
                    "min_consecutive_resting_days": {
                        "id": lambda employee, day: f"min_consecutive_resting_days{employee.id}_{str(day)}",
                    },
                    "min_rest_time_between_shifts": {
                        "id": lambda employee, shift, rule_counter: f"min_rest_time_between_shifts{employee.id}_{shift.id}_{rule_counter}",
                    },
                    "not_used1": "6",
                    "max_working_days": {
                        "id": lambda employee, day, rule_counter: f"max_working_days{employee.id}_{str(day)}_{rule_counter}",
                    },
                    "earliest_shift_start": {
                        "id": lambda employee: f"no_overlapping_shifts_{employee.id}",
                    },
                    "latest_shift_end": {
                        "id": lambda employee: f"no_overlapping_shifts_{employee.id}",
                    },
                    "max_shift_length": "10",
                    "min_shift_length": "11",
                    "max_employees_per_day": "12",
                    "max_minutes_per_day": "13",
                    "min_contract_hours": {
                        "id": lambda employee, payperiod_start, agreement_id, rule_counter: f"min_contract_hours_{employee.id}_{payperiod_start.strftime(constants.time.date_format)}_{agreement_id}_{rule_counter}",
                    },
                    "max_shifts_per_day": "15",
                    "shift_break_correct_timing_and_length": "16",
                    "shift_type_preference": "17",
                    "max_weekends": {
                        "id": lambda employee, day, rule_counter: f"max_weekends_{employee.id}_{str(day)}_{rule_counter}",
                        "help_constr_id": lambda employee, first_day_weekend, day, rule_counter: f"max_weekends_help_var_{employee.id}_{str(first_day_weekend)}_{str(day)}_{rule_counter}"
                    },
                    "preassigned_employees": "19",
                    "working_time_preference": {
                        "id": lambda employee, preference, shift, rule_counter: f"min_contract_hours_{employee.id}_{preference.start}_{preference.end}_{shift.id}_{rule_counter}",
                    },
                    "equal_hour_distribution": "21",
                    "equal_shift_type_distribution": "22",
                    "min_rest_time_period1": "23",
                    "min_consecutive_days_off_input_period": "24",
                    "max_working_time": {
                        "id": lambda employee, day, rule_counter: f"max_working_time{employee.id}_{str(day)}_{rule_counter}",
                        "shifts_of_type_min": lambda employee, day, rule_counter: f"min_shifts_of_type_min{employee.id}_{str(day)}_{rule_counter}",
                        "shifts_of_type_max": lambda employee, day,
                                                         rule_counter: f"min_shifts_of_type_max{employee.id}_{str(day)}_{rule_counter}",

                        "pay_period_length_default": 7
                    },
                    "consecutive_shift_types": "26",
                    "rest_work_rest": "27",
                    "work_rest_work": "28",
                    "max_shifts_of_type": "29",
                    "max_working_days_shifting": {
                        "id": lambda employee, day, rule_counter: f"max_working_days_shifting{employee.id}_{str(day)}_{rule_counter}",
                    },
                    "shift_type_followed_by_shift_type_or_rest_period": "31",
                    "min_rest_time_period2": "32",
                    "equal_start_time_sequential_days1": "33",
                    "equal_distrubution_shifts": "34",
                    "equal_start_time_sequential_days2": "35",
                    "max_weekends_input_period": "36",
                    "max_special_days": "37",
                    "shift_type_before_dayoff": "38",
                    "shift_type_after_dayoff": "39",
                    "min_number_of_weekday_combinations_off": {
                        "id": lambda employee, day, rule_counter:
                        f"min_number_of_weekday_combinations_off_{employee.id}_{str(day.date)}_{rule_counter}",
                        "help_constr_id_1": lambda employee, first_day_weekend, day,
                                                 rule_counter: f"day_combination_off_help_var_{employee.id}_{str(first_day_weekend)}_{str(day.date)}_{rule_counter}",
                        "help_constr_id_2": lambda employee, week_number, day,
                                                   rule_counter: f"week_day_combination_off_help_var_{employee.id}_{str(week_number)}_{str(day.date)}_{rule_counter}"
                    },
                    "not_used3": "41",
                    "min_rest_period_exceptions": "42",
                    "min_rest_after_shift_type": "43",
                    "shift_of_type_proceeded_and_followed_by_shift_type": "41",
                    "min_rest_after_series_of_shift_types": "45",
                    "min_break_duration": "46",
                    "min_rest_with_split": "47",
                    "max_length_series_including_shift_type": "48",
                    "notused4": "49",
                    "single_shift_of_type": "50",
                    "not_used5": "51",
                    "min_free_sundays": "52",
                    "one_of_two_weekdays_per_week": "53",
                    "same_shift_type_after_X_days": "54",
                    "no_shift_typeX_after_shift_typeY": "55",
                    "min_free_days": "56",
                    "min_X_times_consecutive_daysoff": "57",
                    "connected_weekends": "58",
                    "preference_off_time": "59",
                    "min_employees_with_skill_for_required_times": "60",
                    "max_time_within_interval": "61",
                    "min_employees_with_skill_in_shift_group": "62",
                    "min_shifts_in_shift_group": {
                        "id": lambda group_id,
                                     rule_counter: f"min_shifts_in_shift_group_{group_id}_{rule_counter}",
                    },
                    "max_shifts_in_shift_group": {
                        "id": lambda group_id,
                                     rule_counter: f"max_shifts_in_shift_group_{group_id}_{rule_counter}",
                        },
                    "min_hours_per_day": {
                        "id": lambda day, employee, rule_counter: f"min_hours_per_day_{day}_{employee.id}_{rule_counter}",
                    },
                }
            }
        }
    )
