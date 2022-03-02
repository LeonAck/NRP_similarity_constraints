# Auto Assign (AA)

## General Introduction

The purpose of the Auto Assign algorithm is to assign a set of anonymous (unassigned) shifts to a set of employees. The
assignment is done based on a set of rules that can be configured. The set of rules usually consists of labour laws, as
well as customer-specific scheduling rules. The goal of the algorithm is to do the assignment in the most optimal way.
Dependent on the configuration, the algorithm can optimise for costs, employee happiness, proficiency, or a mix of
those. After solving the optimisation problem, the algorithm returns the set of assigned shifts, shifts that are not
assigned to an employee, and potential violations in any of the defined rules.

## Input

The input of the Auto Assign algorithm is structured as follows:

* [Users](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Users):
* [Shifts](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Shifts):
* [Rules](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Rules):
* [Shift Type Definitions](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Shift-Type-Definitions):
* [Settings](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Settings):
* [Initial Solution](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Initial-Solution):

```
{
    "users": [
        {
            "id": "1",
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
        },
        ...
    ],
    "shifts": [
        {
            "id": "1",
            "is_fixed": False,
            "break_duration": 0,
            "pay_multiplication_factor": 1,
            "shift_skill": {
                "min_level": 0,
                "difficulty": 0
            }
        },
        ...
    ],
    "rules": [
        {   
            "rule_id": 1,
            "rule_tag": "shift_assignment",
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
            "user_ids": null,
            "department_id": null,
            "department_id_2": null,
            "shift_types": null,
            "skill_id": null,
            "skill_id_2": null,
            "license_id": null,
            "license_id_2": null,
            "weekdays": null,
            "shift_group_ids": null,
            "rule_start": 0,
            "rule_end": 9999999999,
            "period_start": 0,
            "period_end": 9999999999,
            "start_payperiod": null,
            "required_times": null,
            "special_days": [],
            "improvement_heuristic_only": True,
            "is_active": True,
        },
        ...
    ],
    "shift_type_definitions": [
        {
            "id": "1",
        },
        ...
    ],
    "settings": {
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
    "initial_solution": [
        {
            "user_id": "1",
        },
        ...
    ]
}
```

The values in the JSON are the default values for the properties.

### Users

The list of users/employees that to which to assign shifts.

* **id**: (integer) The ID of the employee. Should (by definition) be unique.
* **start_contract**: (unix timestamp) Start of the contract of the employee. Shifts ending before the **
  start_contract** cannot be assigned to this employee.
* **finish_contract**: (unix timestamp) End of the contract of the employee. Shifts starting after the **
  finish_contract** cannot be assigned to this employee.
* **hourly_rate**: (float) Hourly rate of the employee. Used in case **cost_objective** is set to a non-zero value in
  the **settings**. The **hourly_rate** is used for calculating the total costs of the schedule, which the algorithm
  tries to minimise.
* **is_fixed**: (boolean) If set to true, no shifts are assigned to the employee and only the potential rule violations
  will be reported for this employee.
* **use_availabilities**: (boolean) If set to true, the employee is regarded as being unavailable unless stated
  otherwise.
* **start_first_of_month**: (boolean) If set to true, the contract hour calculations are starting from the first of each
  month.
* **pay_period_cycle**: (string) ("daily"/"monthly") Variable that states if the period cycle of the employee is on
  weekly or monthly basis. Used for assigning the correct number of shift hours within each period.
* **payperiod_length**: (integer) The length of the period (days in case **pay_period_cycle** is set to "daily", months
  in case **pay_period_cycle** is set to "monthly") for which to generate minimum and maximum hours constraints.
* **payperiod_minutes_min**: (float) Minimum number of shift minutes to be assigned within each period. Only used in
  case Rule 14 is configured in the rule setup.
* **payperiod_minutes_max**: (float) Maximum number of shift minutes to be assigned within each period. Only used in
  case Rule 2 is configured in the rule setup.
* **minimum_time_between_shifts**: (integer) Minimum number of time between two sequential shifts. Only used in case
  Rule 5 is configured in the rule setup. This overwrites the values that is configured in Rule 5.

---

### Shifts

Set (List/Array)  of shifts ...

* **id**: (integer) The ID of the employee. Should (by definition) be unique.
* **start**: (unix timestamp) Start time of the shift.
* **finish**: (unix timestamp) End time of the shift.
* **is_fixed**: (boolean) If set to true, shift is regarded as being assigned already and will not be assigned to other
  employees.
* **user_id**: (integer) ID of the employee to which the shift is already assigned.
* **pay_duration**: (integer) Number of minutes the shift should count for contract hours. In case this is not set, the
  pay duration is automatically calculated as the shift duration minus the break duration(s).
* **breaks**: (array of objects)
    * **start**: (integer) Start time of the break.
    * **finish**: (integer) End time of the break.

---

### Rules

Set of rules imposed when assigning shifts to employees.

* **rule_id**: (string) The identifier of the rule, [description of rules](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3536584753/Rules+AA). 
* **rule_tag**: (string) 
* **penalty**: (integer) costs caused by violating rule
* **parameter_1**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **parameter_2**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **parameter_3**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **parameter_4**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **parameter_5**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **parameter_6**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **parameter_7**: (integer) input parameter for rule. Meaning differs per rule, in the description of the rules the parameters per rule are specified as well.
* **is_mandatory**: (boolean) indicates whether the rule is applied as a hard (labor) rule
* **is_fixed**: (boolean)
* **user_ids**: (array of strings) list of user ids for which this rule applies. If left empty or field not added, it will apply to all users
* **department_ids** (array of strings) list of department ids for which this rule applies to. If left empty or field not added, the rule will apply to all department ids
* **department_id**: (string)
* **department_id_2**: (string)
* **shift_types**: null,
* **skill_id**: (string)
* **skill_id_2**: (string)
* **license_id**: (string)
* **license_id_2**: (string)
* **weekdays**: (array of integers)
* **shift_group_ids**: (array of strings)
* **rule_start**: (unix timestamp)
* **rule_end**: (unix timestamp)
* **period_start**: (unix timestamp)
* **period_end**: (unix timestamp)
* **start_payperiod**: (unix timestamp)
* **required_times**: (object of objects)
* **special_days**: (array of integers)
* **improvement_heuristic_only**: (boolean)
* **is_active**: (boolean)
---

### Shift Type Definitions

Set (List/Array)  of shift type definitions ...

* **id**:

---

### Settings

Settings (Dictionary/Object)...

* **start**:

---

### Initial Solution
-
Set (List/Array) of assignments for initial solution..

* **user_id**:

---

## Output

The output returned by AA is structured as follows:

* [Shifts](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Shifts.1):
* [Unassigned shifts](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Unassigned-shifts):
* [Rule Violations](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Rule-Violations):
* [Technical KPIs](https://quinyx.atlassian.net/wiki/spaces/RD/pages/3511844877/Auto+Assign+AA#Technical-KPI's):

```
{
    "shifts": [
        {
            "id": "1",
            "is_fixed": False
        },
        ...
    ],
    "unassigned_shifts": [
        {
            "id": "1",
            "is_fixed": False
        },
        ...
    ],
    "rule_violations": [
        {
            "rule_id": "1"
        },
        ...
    ],
    "technical_kpis": {
        "runtime": 2.750812,
    }
    "result": 1,
    "lower_bound": 8500758.0,
    "upper_bound": 8500758.0,
    "goal_score": 8500758.0,
}
```

The values in the JSON are the default values for the properties.

### Shifts

Set (List/Array) of assigned shifts...

* **shift_id**:

---

### Unassigned shifts

Set (List/Array) of unassigned shifts...

* **shift_id**:

---

### Rule Violations

Set (List/Array) of rule violations...

* **id**:

---

### Technical KPIs

Technical KPIs (Dictionary/Object)...

* **runtime**:

---

### Other

* **result**:

---