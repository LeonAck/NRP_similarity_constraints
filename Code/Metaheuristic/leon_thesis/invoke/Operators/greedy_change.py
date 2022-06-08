from invoke.Operators.change_operator import get_feasible_change, calc_new_costs_after_change

def greedy_change(solution, scenario):
    """
        Function to get 5 changes and pick the one that decreases the objective function the most
        Options:
        skill request --> day off
        skill request --> skill request
        day off --> skill request
        :return:
        new_solutions
    """
    best_cost_increment = 100000
    best_change_info = None
    for i in range(0, scenario.greedy_number):
        change_info = get_feasible_change(solution, scenario)
        # get a change that is allowed by hard constraints

        # add penalty to objective
        if change_info['feasible']:
            change_info["cost_increment"], change_info['violation_increment'] = calc_new_costs_after_change(solution, scenario, change_info)
            if change_info['cost_increment'] < best_cost_increment:
                best_cost_increment = change_info['cost_increment']
                best_change_info = change_info

    return best_change_info