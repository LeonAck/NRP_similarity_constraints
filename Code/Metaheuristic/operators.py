
def change_operator(solution):
    """
    Function to change activity of one nurse
    Options:
    skill request --> day off
    skill request --> skill request
    day off --> skill request
    :return:
    new_solution
    """
    return None

def sk_request_to_day_off(solution, scenario, employee_id, d_index, s_type_index):
    """
    Move nurse from skill request to day off
    """

    skill_index = None
    # change skill counter randomly
    solution.update_skill_counter(d_index, s_type_index, skill_index,
                                  skill_set_index=scenario.employees._collection[employee_id].skill_set_id,
                                  add=False)
    # change nurse assignment to zero
    solution.remove_shift_assignment(employee_id, d_index)
