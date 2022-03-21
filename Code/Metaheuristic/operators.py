import random
def change_operator(solution):
    """
    Function to change activity of one nurse
    Options:
    skill request --> day off
    skill request --> skill request
    day off --> skill request
    :return:
    new_solutions
    """
    return None


def sk_request_to_day_off(solution, sk_set_collection, employees, employee_id, d_index, s_type_index):
    """
    Move nurse from skill request to day off
    """
    # TODO check function that checks what removal keeps optimality
    # choose random index from set of nurses
    skill_set_id = employees._collection[employee_id].skill_set_id
    skill_to_remove = random.choice(sk_set_collection.collection[skill_set_id].skill_indices_in_set)
    # change skill counter randomly
    solution.update_skill_counter(d_index, s_type_index, skill_to_remove,
                                  skill_set_index=employees._collection[employee_id].skill_set_id,
                                  add=False)
    # change nurse assignment to zero
    solution.remove_shift_assignment(employee_id, d_index)

    # update solution information
    return None