

def change_operator(solution, scenario, k):
    """
        Function to swap the assignments of two skill-compatible nurses for k
        consecutive days
        Skill-compatible means that the nurses have the same skillset

        :return:
        change_information
    """
    # get a change that is allowed by hard constraints
    change_info = get_feasible_change(solution, scenario)

    # add penalty to objective
    if change_info['feasible']:
        change_info["cost_increment"], change_info['violation_increment'] = calc_new_costs_after_change(solution, scenario, change_info)

    return change_info