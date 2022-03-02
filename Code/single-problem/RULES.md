* **No Overlap shifts**
  * **rule id**: 0
  * **rule tag**: no_overlapping_shifts
  * **description**: Added by default in shift fill algorithm. Function: Do not assign overlapping shifts to employees
  * **parameter 1**: Create a batch constraint if false, so no cut in solution space
  * **parameter 6**: None
* **Assigning Shifts Penalty**
  * **rule id**: 1
  * **rule tag**: shift_assignment
  * **description**: Ensures that penalty is added for each shift that is not assigned to an employee. Must always be included in the input such that shifts actually get assigned
  * **parameter 1**: penalize per hour
  * **parameter 6**: None
* **Contract Hours**
  * **rule id**: 2
  * **rule tag**: max_contract_hours
  * **description**: Ensures that the amount of worked time does not exceed the contract hours of the employee. If users go over their contract hours, for each hour additional to the user's max contract hours, the penalty is applied. The penalty is given per minute
  * **parameter 1**: Optional, if set defines the payperiod
  * **parameter 2**: Optional, if set defines the maximum hours
  * **parameter 3**: None
  * **parameter 6**: None
* **Maximum Consecutive Working Days**
  * **rule id**: 3
  * **rule tag**: max_consecutive_working_days
  * **description**: Limits the number of consecutive days (parameter 1) that an employee can be working. The penalty is applied for each additional day of work
  * **parameter 1**: The maximum number of days. Defined as a number. E.g. 6
  * **parameter 6**: None
* **Minimum Consecutive Resting Days**
  * **rule id**: 4
  * **rule tag**: min_consecutive_resting_days
  * **description**: Ensures that an employee will get a minimum number of consecutive resting days (parameter 1) in a period. The penalty is applied for each rest day block which does not follow the minimum days.
  * **parameter 1**: The minimum number of days. Defined as a number. E.g. 2
  * **parameter 6**: None
* **Minimum Resting Time between Shifts**
  * **rule id**: 5
  * **rule tag**: min_rest_time_between_shifts
  * **description**: Ensures that there is at least a period of X minutes (parameter 1), between two sequential shifts. An exception is made for shifts that are closer to each other than Y minutes (parameter 2). The penalty is applied for each time rest time is shorter than the minimum limit.
  * **parameter 1**: The minimum minutes between any two assigned shifts for one employee. Defined in minutes. E.g. 11h should be set as 660
  * **parameter 2**: If the shifts are closer than a certain time, the rule is ignored. Defined in minutes. E.g. 1h should be set as 60
  * **parameter 3**: None
  * **parameter 4**: Only consider shifts ending after number of minutes after midnight (e.g. 120 is 02:00)
  * **parameter 5**: Avoid creating constraints for shifts on same day. If set to 1 constraints are not created
  * **parameter 6**: None
* **Maximum Working Days per Period**
  * **rule id**: 7
  * **rule tag**: max_working_days
  * **description**: Limits the number of working days (parameter 1) in the pay-period for each employee. The penalty is applied for each additional day assigned in the pay-period
  * **parameter 1**: The maximum working days per pay-period. Defined as a number. E.g. 5
  * **parameter 2**: Optional, 1 if shifts should be used to determine if employee works on day, 0 if worksOn variable should be used. Defined as 1 or 0
  * **parameter 3**: Optional, if set defines the payperiod
  * **parameter 6**: None
* **Earliest Shift Starttime**
  * **rule id**: 8
  * **rule tag**: earliest_shift_start
  * **description**: Shifts cannot start earlier than X minutes (parameter 1) after midnight. The penalty is applied for each minute the shift starts too early
  * **parameter 1**: Minutes after midnight after which the shift must start. Defined in minutes after midnight. E.g. 06:00 (6 am) should be set as 360
  * **parameter 6**: None
* **Latest Shift Endtime**
  * **rule id**: 9
  * **rule tag**: latest_shift_end
  * **description**: Shifts cannot end later than X minutes (parameter 1) after midnight. The penalty is applied for each minute the shift ends too late
  * **parameter 1**: Minutes after midnight before which the shift must end. Defined in minutes after midnight. E.g. 14:00 (2 pm) should be set as 840
  * **parameter 6**: None
* **Maximum Shift Length**
  * **rule id**: 10
  * **rule tag**: max_shift_length
  * **description**: Maximum minutes per shift which ensures that shifts longer than X minutes (parameter 1) will not be assigned. The penalty is applied for each minute the shift is longer than maximum time.
  * **parameter 1**: Maximum shift length. Defined in minutes. E.g. 10h becomes 600
  * **parameter 2**: Shifttype to which the maximum shift length applies.
  * **parameter 3**: If  1, the break time will not be included.
  * **parameter 6**: None
* **Minimum Shift Length**
  * **rule id**: 11
  * **rule tag**: min_shift_length
  * **description**: Minimum minutes per shift which ensures that shifts shorter than X minutes (parameter 1) will not be assigned. The penalty is applied for each minute the shift is shorter than the minimum time
  * **parameter 1**: Minimum shift length. Defined in minuted. E.g. 6h becomes 360
  * **parameter 6**: None
* **Maximum Employees per Day**
  * **rule id**: 12
  * **rule tag**: max_employees_per_day
  * **description**: Limits the maximum number of employees (parameter 1) that are working on the same day. The penalty is applied for every employee per day going over the maximum
  * **parameter 1**: Maximum employees per day. Defined as a number. E.g. 6 employees should be set as 6
  * **parameter 6**: None
* **Maximum Minutes per Day**
  * **rule id**: 13
  * **rule tag**: max_minutes_per_day
  * **description**: Limits the maximum number of working minutes (parameter 1) for an employee per day. The penalty is applied for every minute assigned over the maximum number
  * **parameter 1**: Maximum number of minutes per day. Defined in minutes. E.g. 10h should be set as 600
  * **parameter 6**: None
* **Minimum Minutes per Pay-Period**
  * **rule id**: 14
  * **rule tag**: min_contract_hours
  * **description**: Sets the minimum number of minutes an employee is working per pay-period. The minimum is set by the "payperiod_minutes_min" property of the employee. The penalty is applied for every minute the employee is not assigned minutes under their own minimum value. The penalty is given per minute
  * **parameter 1**: Optional parameter indicating minimim minutes per pay-period per employee. If not defined, minimum minutes per payperiod is defined in employee json
  * **parameter 6**: None
* **Maximum Shifts per Day per Employee**
  * **rule id**: 15
  * **rule tag**: max_shifts_per_day
  * **description**: Limits the maximum number of shifts (parameter 1) an employee is working on a day. The penalty is applied for each additional shift over the limit
  * **parameter 1**: Maximum shifts per day for an employee. Defined as a number. E.g. 2
  * **parameter 6**: None
* **Minimum Break Length**
  * **rule id**: 16
  * **rule tag**: shift_break_correct_timing_and_length
  * **description**: Ensures that there is a minimum break of X minutes (parameter 2), if shift is longer than X (parameter 1) minutes. The penalty is applied for each shift that is assigned violating the rule
  * **parameter 1**: Time after which the break should occur. Defined in minutes into the shift. For example 1h into the shift should be set as 60
  * **parameter 2**: Length of the break in minutes. Defined in minutes. E.g. 15 minutes should be set as 15
  * **parameter 6**: None
* **Shift Type Preference Bonus**
  * **rule id**: 17
  * **rule tag**: shift_type_preference
  * **description**: Adds a bonus in case a shift of a certain type is assigned an employee who prefers to work that shifttype. The bonus is applied for each shift that is assigned but with a shift-type not preferred by that employee (value should be positive)
* **Weekend Block**
  * **rule id**: 18
  * **rule tag**: max_weekends
  * **description**: Ensures that at most X (parameter 2) weekends shifts of type (parameter 1) are assigned to an employee. The penalty is applied for each weekend that an employee gets assigned to work above the specified limit
  * **parameter 1**: Shift type the rule relates to. Defined as the id of the shift type. E.g morning shifts with id 1 should be set to 1
  * **parameter 2**: Maximum number of worked weekends in the pay-period. Defined as a number. E.g. 2
  * **parameter 3**: Boolean if start times of the shifts are being used. In case boolean is set to 1, starting times are not used
  * **parameter 4**: None
  * **parameter 5**: Period for which the rule should check
  * **parameter 6**: Rolling-horizon period
* **Assign Shifts to Preassigned Employees**
  * **rule id**: 19
  * **rule tag**: preassigned_employees
  * **description**: Adds a bonus for assigning the shift to the employee with matching employee ID that is set on the shift. The bonus is applied for each shift assigned to preferred employee (value should be positive)
* **Shift Preference Bonus**
  * **rule id**: 20
  * **rule tag**: working_time_preference
  * **description**: Adds a bonus in case a shift is assigned an employee who prefers to work during that time. The bonus is applied for each preferred shift assigned to employee (value should be positive)
* **Equal Hour Distribution**
  * **rule id**: 21
  * **rule tag**: equal_hour_distribution
  * **description**: Ensures that employees get a number of working hours close to the number in the previous pay-period. The penalty is applied for each hour of the employee different from the previous hours of that employee.
* **Equal Shift Type Distribution**
  * **rule id**: 22
  * **rule tag**: equal_shift_type_distribution
  * **description**: Ensures that employees get a number of shifts of type X (parameter 1) is close to the number in the previous pay-period. The penalty is applied for each shift of this shift type assigned to the employee different from the previous shifts fo this shift type of that employee
  * **parameter 1**: Shift type the rule relates to. Defined as the id of the shift type. E.g morning shifts with id 1 should be set to 1
  * **parameter 6**: None
* **Minimum Resting Period per Time-Window**
  * **rule id**: 23
  * **rule tag**: min_rest_time_period1
  * **description**: Ensures each period of X days (parameter 1) an employee gets a work-free period of at least Y minutes (parameter 2). The penalty is applied for each period in which there is no resting period with the length of at least the minimum
  * **parameter 1**: The period in which the resting period must be. Defined in days. E.g. 14 days should be set as 14
  * **parameter 2**: Minimum resting period. Defined in minutes. E.g. 24h should be set as 1440
  * **parameter 6**: None
* **Number of Consecutive Days off per Y Days**
  * **rule id**: 24
  * **rule tag**: min_consecutive_days_off_input_period
  * **description**: Ensures that each period of Y (parameter 2) days has at least one period with X (parameter 1) consecutive days off. The penalty is applied for each period in which there is no resting period
  * **parameter 1**: Required consecutive number of days off. Defined in days. E.g. 2 days should be set to 2
  * **parameter 2**: Length of period for which the rule applies. Defined in days. E.g. 14 days should be set to 14
  * **parameter 6**: None
* **Maximum Working Time**
  * **rule id**: 25
  * **rule tag**: max_working_time
  * **description**: Generates constraints and violations for each employee and period.
    Each constraint sets a maximum to the number of contract hours for the applicable employees for a specific period.
    Violation (if any) indicates the number of minutes the employee is over contract hours in a period (The penalty is applied for each minute assigned over the limit).
  * **parameter 1**: Maximum working minutes: the maximum time in minutes per pay period. E.g. 48h should be set to 2880
  * **parameter 2**: Pay period length: The period of days over which the rule will be set
  * **parameter 3**: Minimum shifts of type: the minimum number of shifts in a pay period in order to set the rule
  * **parameter 4**: Shift type id rule: the id of the shift type for which a minimum should hold
  * **parameter 5**: Use previous hours: incorporate the previous_hours field on employees
  * **parameter 6**: Shifting window size: the step size in days to increment per time to set the rule
* **Consecutive Shift Types**
  * **rule id**: 26
  * **rule tag**: consecutive_shift_types
  * **description**: Adds a penalty for working two consecutive shifts of different types (e.g. Night - Morning). The penalty is applied for each pair of onsecutive shifts that violates the rule
  * **parameter 1**: Minimum hours between two assigned shifts. Defined in minutes. E.g. 11h should be set to 660
  * **parameter 2**: Should be set to 1 to ensure 1 rest day in between the shifts
  * **parameter 6**: None
* **Penalty for Rest - Work - Rest**
  * **rule id**: 27
  * **rule tag**: rest_work_rest
  * **description**: Ensures that a penalty is added when a single working day is assigned. The penalty is applied for each time there is a workday in between two rest days
* **Penalty for Work - Rest - Work**
  * **rule id**: 28
  * **rule tag**: work_rest_work
  * **description**: Ensures that a penalty is added when a single rest day is assigned. The penalty is applied for each time there is a rest day in between two workdays
* **Maximum number of shift type in period**
  * **rule id**: 29
  * **rule tag**: max_shifts_of_type
  * **description**: Make sure that the number of shifts of type X (parameter 1) does not exceed Y (parameter 2) in a period of Z days (parameter 3). The penalty is applied for each shift assigned of a certain type over the specified limit
  * **parameter 1**: Shift type the rule relates to. Defined as the id of the shift type. E.g morning shifts with id 1 should be set to 1
  * **parameter 2**: Maximum number of shifts of that type per period. Defined as a number. E.g. 4
  * **parameter 3**: Period length. Defined as a number in days. E.g. 14 days should be set to 14
  * **parameter 4**: Time in minutes after midnight after which shift should end to be counted in the rule
  * **parameter 5**: Check frequency in days. If this is set to 1, the rule will check using rolling horizon
  * **parameter 6**: None
* **Maximum Working Days per Shifting Period**
  * **rule id**: 30
  * **rule tag**: max_working_days_shifting
  * **description**: Ensures that the number of working days does not exceed X days (parameter 1) in a period of Y days (parameter 3). The check is done on a rolling window.
  * **parameter 1**: The maximum number of days. Defined as a number. E.g. 5 days should be set to 5
  * **parameter 2**: If zero use works on variable, otherwise use assignment variables
  * **parameter 3**: Period length. Defined as a number in days. E.g. 14 days should be set to 14
  * **parameter 6**: None
* **Resting Period of Shift of Type X after Shift of Type Y**
  * **rule id**: 31
  * **rule tag**: shift_type_followed_by_shift_type_or_rest_period
  * **description**: Ensure that after a shift of Type X (Parameter 1), either a shift of the same type is scheduled or a resting period of length Y (Parameter 2) is ensured
  * **parameter 1**: Shift type the rule relates to. Defined as the id of the shift type. E.g morning shifts with id 1 should be set to 1
  * **parameter 2**: Resting period length. Defined as a number in minutes. E.g. 24h should be set to 1440
  * **parameter 3**: None
  * **parameter 6**: None
* **Minimum Resting Time per Period**
  * **rule id**: 32
  * **rule tag**: min_rest_time_period2
  * **description**: Ensures that each period of X days (Parameter 1) contains a resting period of at least Y minutes (Parameter 2) 
  * **parameter 1**: Period length. Defined as a number in days. E.g. 14 days should be set to 14
  * **parameter 2**: Resting period length. Defined as a number in minutes. E.g. 24h should be set to 1440
  * **parameter 6**: None
* **Equal Start Times on Sequential Days**
  * **rule id**: 33
  * **rule tag**: equal_start_time_sequential_days1
  * **description**: Ensure that on sequential days shifts have the same start times
  * **parameter 1**: None
  * **parameter 2**: None
  * **parameter 3**: None
  * **parameter 6**: None
* **Equal Distribution of Shifts in the period**
  * **rule id**: 34
  * **rule tag**: equal_distrubution_shifts
  * **description**: None
  * **parameter 1**: None
  * **parameter 6**: None
* **Same Starting Time Bonus**
  * **rule id**: 35
  * **rule tag**: equal_start_time_sequential_days2
  * **description**: Bonus for similar starting times on sequential days
  * **parameter 1**: Left hand side range in minutes
  * **parameter 2**: Right hand side range in minutes
  * **parameter 6**: None
* **Max weekend rule**
  * **rule id**: 36
  * **rule tag**: max_weekends_input_period
  * **description**: Defines how many weekends are allowed to be worked in a certain period
  * **parameter 1**: Shift Types for this weekend
  * **parameter 2**: Number of weekends
  * **parameter 3**: Length of payperiod
  * **parameter 6**: None
* **Max number of special days**
  * **rule id**: 37
  * **rule tag**: max_special_days
  * **description**: None
  * **parameter 1**: None
  * **parameter 6**: None
* **desired shift type before day off**
  * **rule id**: 38
  * **rule tag**: shift_type_before_dayoff
  * **description**: None
  * **parameter 1**: shift type id of desired shift type
  * **parameter 6**: None
* **desired shift type after day off**
  * **rule id**: 39
  * **rule tag**: shift_type_after_dayoff
  * **description**: None
  * **parameter 1**: shift type id of desired shift type
  * **parameter 6**: None
* **Minimum rest per period with exceptions**
  * **rule id**: 42
  * **rule tag**: min_rest_period_exceptions
  * **description**: Minimum V minutes (parameter1) of rest per period of W minutes (parameter2), but X times (parameter3) per period of Y minutes (parameter4), the rest time can be decreased to a minimum of Z minutes (parameter5)
  * **parameter 1**: Minimum rest in minutes
  * **parameter 2**: Period in minutes in which rest of parameter1 must be included
  * **parameter 3**: Number of times the minimum rest of parameter2 can be shortened
  * **parameter 6**: None
* **Rest after shift of type ending after certain time with exceptions**
  * **rule id**: 43
  * **rule tag**: min_rest_after_shift_type
  * **description**: At most W times (parameter5) per period (parameter6) the rest after a shift of type X (parameter3) ending after Y minutes after midnight (parameter4) can be shorter than Z minutes (parameter1)
  * **parameter 1**: Minimum rest time after shift in minutes
  * **parameter 2**: Minimum time between shifts in minutes for the rest time to be checked
  * **parameter 3**: Shift type for rule
  * **parameter 6**: None
* **Minimum rest after series shifts of type**
  * **rule id**: 45
  * **rule tag**: min_rest_after_series_of_shift_types
  * **description**: After a series of shifts of type X (parameter 1) with a minimum length of Y (parameter 2), there must be a rest period of minimum Z minutes (parameter 3)
  * **parameter 1**: Shifttype
  * **parameter 2**: Minimum length of the series 
  * **parameter 3**: Minimum resting time after the series in minutes
  * **parameter 6**: None
* **Minimum breaktime for shifts of length**
  * **rule id**: 46
  * **rule tag**: min_break_duration
  * **description**: minimum X minutes (parameter2) of break for shifts with pay duration longer than Y minutes (parameter1), possibly split in breaks of minimum Z minutes (parameter3)
  * **parameter 1**: The minimum length in minutes of shifts to which the rule applies
  * **parameter 2**: The minimum total break time in minutes that must be included in a shift
  * **parameter 3**: The minimum break time per break
  * **parameter 6**: None
* **Minimum rest per period with split option**
  * **rule id**: 47
  * **rule tag**: min_rest_with_split
  * **description**: Minimum X minutes rest (parameter2) in every period of Y*24 hours (parameter1), which can be split up in periods of minimum Z minutes (parameter3)
  * **parameter 1**: Period length in days in which the rest must be included
  * **parameter 2**: Minimum total rest time in minutes
  * **parameter 3**: Minimum length of a rest period in minutes to be counted as part of the total rest time
  * **parameter 6**: None
* **Max length series including shift of type**
  * **rule id**: 48
  * **rule tag**: max_length_series_including_shift_type
  * **description**: Series including at least 1 shift of type X (parameter2) can have a length of at most Y (parameter1). A series ends with a resting period of minimum Z minutes (parameter3).
  * **parameter 1**: Maximum number of shifts allowed in a series
  * **parameter 2**: Shift type that must be included in the series
  * **parameter 3**: Minimum resting period in minutes to end a series
  * **parameter 6**: None
* **Penalty for single shift of certain type**
  * **rule id**: 50
  * **rule tag**: single_shift_of_type
  * **description**: Penalty for single shift of certain type
  * **parameter 1**: Shift type for rule
  * **parameter 6**: None
* **Minimum free sundays per period**
  * **rule id**: 52
  * **rule tag**: min_free_sundays
  * **description**: Minimum number of free sundays (parameter 1) per period of X weeks (parameter 2) taking into account the employee counter of previous free sundays.
  * **parameter 1**: The minimum number of free sundays required
  * **parameter 2**: The period length in weeks
  * **parameter 3**: Shifting window size in days
  * **parameter 6**: None
* **Do not work weekday1 and weekday2 in the same week**
  * **rule id**: 53
  * **rule tag**: one_of_two_weekdays_per_week
  * **description**: Do not work weekday parameter1 and weekday parameter2 in the same week starting on weekday parameter3 (0 = Monday, 6 = Sunday)
  * **parameter 1**: Weekday 1
  * **parameter 2**: Weekday 2
  * **parameter 3**: Weekday that must be seen as the start of the week
  * **parameter 6**: None
* **Work both weekend days**
  * **rule id**: 58
  * **rule tag**: connected_weekends
  * **description**: Ensure that zero or both weekend days are worked
* **Penalty for preference not to work**
  * **rule id**: 59
  * **rule tag**: preference_off_time
  * **description**: Penalty for preference not to work
* **Minimum required skill for specified times **
  * **rule id**: 60
  * **rule tag**: min_employees_with_skill_for_required_times
  * **description**: Minimum requirement for a skill/license/department during specific times 
  * **parameter 1**: minimum requirement of skill
  * **parameter 2**: bucket size in minutes 
  * **parameter 6**: None
* **Maximum working time within a specified time interval**
  * **rule id**: 61
  * **rule tag**: max_time_within_interval
  * **description**: Maximum working time within a specified time interval
  * **parameter 1**: Maximum time in minutes
  * **parameter 2**: Period to check in days
  * **parameter 3**: Time window start in minutes from midnight
  * **parameter 6**: None
* **Minimum number of shifts of skill/department/licence**
  * **rule id**: 62
  * **rule tag**: min_employees_with_skill_in_shift_group
  * **description**: Minimum number of shifts of skill/department/licence
  * **parameter 1**: Minimum number
  * **parameter 6**: None
* **Day after shift of type another shift of the same type, otherwise x days no shift of the same type.**
  * **rule id**: 63
  * **rule tag**: after_shift_type_free_or_same_type
  * **description**: Day after shift of type another shift of the same type, otherwise x days no shift of the same type.
  * **parameter 1**: Number of days to check
  * **parameter 2**: Shift type to check
  * **parameter 6**: None
* **Minimum number of shift type in period**
  * **rule id**: 64
  * **rule tag**: min_shifts_of_type
  * **description**: Make sure that the number of shifts of type X (parameter 1) exceeds Y (parameter 2) in a period of Z days (parameter 3). The penalty is applied for each shift assigned of a certain type under the specified limit.
  * **parameter 1**: Shift type id
  * **parameter 2**: Minimum number per period
  * **parameter 3**: Period in number of days
  * **parameter 4**: Time in minutes after midnight after which shift should end to be counted in the rule
  * **parameter 5**: Check frequency in days. If this is set to 1, the rule will check using rolling horizon
  * **parameter 6**: 0: Linear penalty. Penalty incurred per shift under threshold, 1: Single penalty. Penalty incurred upon violation regardless of distance to threshold.
* **Maximum number shift types per period**
  * **rule id**: 66
  * **rule tag**: max_different_shift_types
  * **description**: None
  * **parameter 1**: Number of days in period
  * **parameter 2**: Maximum number of shift types
  * **parameter 6**: None
* **Assign minimum number of shifts per shift group**
  * **rule id**: 67
  * **rule tag**: min_shifts_in_shift_group
  * **description**: This rules ensures that a minimum number of shifts gets assignment per shift group. The shift groups are expected to be given as input to the rule and each shift can belong to a shift group.
  * **parameter 1**: Minimum number per shift group to assign
  * **parameter 6**: None
* **Assign maximum number of shifts per shift group**
  * **rule id**: 68
  * **rule tag**: max_shifts_in_shift_group
  * **description**: This rules ensures that a maximum number of shifts gets assignment per shift group. The shift groups are expected to be given as input to the rule and each shift can belong to a shift group.
  * **parameter 1**: Maximum number per shift group to assign
  * **parameter 6**: None
* **Minimum working hours per day**
  * **rule id**: 69
  * **rule tag**: min_hours_per_day
  * **description**: This rules ensures each employee gets assigned a minimum number of hours each day. The penalty is binary, which makes sure that the rule wants to either give an employee the minimum hours or does not give a shift at all (no hours).
  * **parameter 1**: Minimum working time per day in minutes
  * **parameter 6**: None
