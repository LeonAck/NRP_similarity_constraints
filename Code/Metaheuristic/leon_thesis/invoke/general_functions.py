

def check_if_working_day(shift_assignments, employee_id, d_index):
    """
    Check if nurse works on specific day
    :return:
    True or False
    """
    return shift_assignments[employee_id][d_index][0] > -1


def check_if_working_s_type_on_day(shift_assignments, employee_id, d_index, s_index):
    """
    Check if nurse works specific shift type on specific day
    """
    return shift_assignments[employee_id][d_index][0] == s_index


def check_if_first_day(d_index):
    return d_index == 0


def check_if_last_day(num_days_in_horizon, d_index):
    return d_index == num_days_in_horizon - 1


def check_if_middle_day(num_days_in_horizon, d_index):
    return not check_if_last_day(num_days_in_horizon, d_index) and not check_if_first_day(d_index)


def check_if_same_shift_type(shift_assignments, employee_id, d_index_1, d_index_2):
    return shift_assignments[employee_id][d_index_1][0] \
           == shift_assignments[employee_id][d_index_2][0]
