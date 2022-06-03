from Invoke.Operators.change_operator import calc_new_costs_after_change, \
    remove_infeasible_days_understaffing, get_allowed_s_type, \
    fill_change_info_curr_ass
import random
import numpy as np

def similarity_operator(solution, scenario):
    """
        Function to change activity of one nurse.
        Nurse and day is not chosen randomly, but one that improves the similarity between schedules
        Options:
        skill request --> day off
        skill request --> skill request
        day off --> skill request
        :return:
        new_solutions
    """
    # get a change that is allowed by hard constraints
    change_info = get_feasible_change_improving_similarity(solution, scenario)

    # add penalty to objective
    if change_info['feasible']:
        change_info["cost_increment"], change_info['violation_increment'] = calc_new_costs_after_change(solution, scenario, change_info)

    return change_info


def get_feasible_change_improving_similarity(solution, scenario):
    """
    Function to get a feasible change of assignment that is allowed by hard
    constraints and does not result in the same assignment
    :return:
    object with information about the change
    """
    # flag is set to true if feasible change operation is found
    feasible = False

    # get list of employees that are feasible for the change
    feasible_employees = list((scenario.employees._collection.keys()))

    change_info = dict()
    while len(feasible_employees) > 0 and not feasible:
        # pick random nurse
        change_info["employee_id"] = random.choice(feasible_employees)  # remove nurse if picked before

        # get feasible days for given employee
        feasible_days = list(range(0, scenario.num_days_in_horizon))

        # check if we allow for understaffing compared to minimum requirement
        if scenario.rule_collection.collection['H2'].is_mandatory:
            feasible_days = remove_infeasible_days_understaffing(
                solution, change_info["employee_id"], feasible_days)

        while len(feasible_days) > 0 and not feasible:
            # choose day
            change_info["d_index"] = choose_day_improving_similarity(feasible_days, solution.ref_comparison_day_level[change_info["employee_id"]])
            # if no possible d_index
            if change_info["d_index"] is None:
                break

            change_info = fill_change_info_curr_ass(solution.shift_assignments, change_info)

            # add off day to options if employee currently not working
            if change_info["current_working"]:
                change_info["new_s_type"] = "off"
                change_info["new_working"] = False
                feasible = True
            else:
                # get allowed shifts for insertion for given day
                allowed_shift_types = get_allowed_s_type(solution, scenario, change_info["employee_id"],
                                                         change_info["d_index"])

                # check if copying reference period is possible
                if solution.ref_assignments[change_info["employee_id"]][change_info["d_index"]][0] in allowed_shift_types:
                    change_info["new_s_type"] = solution.ref_assignments[change_info["employee_id"]][change_info["d_index"]][0]
                    change_info["new_sk_type"] = solution.ref_assignments[change_info["employee_id"]][change_info["d_index"]][1]
                    change_info["new_working"] = True
                    feasible = True
                else:
                    if len(allowed_shift_types) > 0:
                        # pick random shift type
                        change_info["new_s_type"] = random.choice(allowed_shift_types)

                        # choose skill type
                        change_info["new_sk_type"] = random.choice(scenario.employees._collection[change_info["employee_id"]].skill_indices)
                        change_info["new_working"] = True
                        feasible = True

            # if no allowed shift type for day, remove day and find new day
            feasible_days.remove(change_info["d_index"])

        # if no feasible day for change for employee, remove employee and find new employee
        feasible_employees.remove(change_info["employee_id"])

    # check whether a feasible change was possible
    if not change_info['current_working'] and not change_info['new_working']:
        change_info['feasible'] = False
    else:
        change_info['feasible'] = True
    return change_info

def choose_day_improving_similarity(feasible_days, similarity_object):
    # get intersections of feasible days and where similarity object can be improved
    set_of_options = np.intersect1d(np.array(feasible_days), np.where(similarity_object==0)[0])
    return random.choice(set_of_options) if set_of_options.any() else None