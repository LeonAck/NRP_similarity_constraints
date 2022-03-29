import random
from Invoke.Constraints.Rules import RuleH3
import numpy as np

def change_operator(solution, scenario, rule_collection):
    """
        Function to change activity of one nurse
        Options:
        skill request --> day off
        skill request --> skill request
        day off --> skill request
        :return:
        new_solutions
    """
    # get a change that is allowed by hard constraints
    change_info = get_feasible_change(solution, scenario, rule_collection)

    # calculate incremental penalties
    # change additional information
    # change solution

def get_feasible_change(solution, scenario, rule_collection):
    """
    Function to get a feasible change of assignment that is allowed by hard
    constraints and does not result in the same assignment
    :return:
    object with information about the change
    """

    feasible = False
    feasible_employees = list((scenario.employees._collection.keys()))
    change_info = dict()
    while len(feasible_employees) > 0 or not feasible:
        # pick random nurse
        change_info["employee_id"] = random.choice(feasible_employees)  # remove nurse if picked before
        feasible_days = list(range(0, scenario.num_days_in_horizon))
        feasible_days = remove_infeasible_days_understaffing(
            solution, change_info["employee_id"], feasible_days)
        while len(feasible_days) > 0 or not feasible:
            # choose day
            change_info["employee_id"] = random.choice(feasible_days)
            change_info = fill_change_info_curr_ass(solution, change_info)

            # get allowed shifts for insertion
            allowed_shift_types = get_allowed_s_type(solution, scenario, rule_collection, change_info["employee_id"],
                                                     change_info["d_index"])

            # add off day to options if currently not working
            if change_info["current_working"]:
                allowed_shift_types = np.append(allowed_shift_types, "off")

            while len(allowed_shift_types) > 0 or not feasible:
                # pick random shift type
                change_info["new_s_type"] = random.choice(allowed_shift_types)

                if change_info["new_s_type"] == "off":
                    feasible = True
                    change_info["new_working"] = False
                else:
                    allowed_skills = get_allowed_skills(scenario, change_info)
                    if len(allowed_skills) == 0:
                        allowed_shift_types = np.delete(allowed_shift_types,
                                                        np.in1d(allowed_shift_types,
                                                                change_info["new_s_type"]))
                    else:
                        change_info["new_sk_type"] = random.choice(allowed_skills)
                        feasible = True

            feasible_days.remove(change_info["d_index"])

        feasible_employees.remove(change_info["employee_id"])

    return change_info

def get_feasible_removal2(solution, scenario, feasible_employees):
    """
    Get employee that can be savely removed from current assignment without
    leading to understaffing
    """
    feasible = False
    n = 0
    change_info = dict()

    while not feasible:
        # pick random nurse
        employee_id = random.choice(feasible_employees) # remove nurse if picked before
        feasible_days = list(range(0, scenario.num_days_in_horizon))
        feasible_days = remove_infeasible_days_understaffing(solution, employee_id, feasible_days)

        if len(feasible_days) == 0:
            feasible_employees = feasible_employees.remove(employee_id)
        else:
            d_index = random.choice(feasible_days)
            feasible = True
            # save info of current assignment
            change_info = fill_change_info_curr_ass(solution, employee_id, d_index)


    if not feasible:
        return "no change possible"
    else:
        return change_info, feasible_employees

def remove_infeasible_days_understaffing(solution, employee_id, feasible_days):
    """
    Remove days where a employee cannot be removed since this might cause understaffing
    :Return:
    list of feasible days
    """
    working_days = [d_index for d_index in feasible_days if solution.check_if_working_day(employee_id, d_index)]

    for d_index in working_days:
        if solution.diff_min_request[
            tuple([d_index,
                   solution.shift_assignments[employee_id][d_index][1],
                   solution.shift_assignments[employee_id][d_index][0]])
        ] < 1:
            feasible_days.remove(d_index)

    return feasible_days

def get_feasible_insertion(solution, scenario, rule_collection, change_info, feasible_employees):
    """
    For a given removal, get feasible insertion
    :return:
    If there is a feasible insertion: change_info with assignment information of insertion
    If there is none, return change object containing that information
    """
    allowed_shift_types = get_allowed_s_type(solution, scenario, rule_collection, change_info["employee_id"], change_info["d_index"])

    if change_info["current_working"]:
        allowed_shift_types = np.append(allowed_shift_types, "off")

    if len(allowed_shift_types) > 0:
        # pick random shift type
        new_s_type = random.choice(allowed_shift_types)
    else:
        # remove day from list of days
        change_info["feasible_insertion"] = False

    return change_info, feasible_employees


    # if off remove shift assignments
    # if new_s_type == "off":
    #     solution.remove_shift_assignment(change_info["employee_id"], change_info["d_index"])

    #     # calculate change in penalty
    #     rule_collection.collection["S1"].increment_violations_day_shift_skill(solution, d_index, curr_assignment[1],
    #                                                                           curr_assignment[2], insertion=False)
    #
    #     # remove assignment information
    #     solution.update_information_removal(solution, employee_id,
    #                                         assignment_info=curr_assignment)
    #
    # # check if same shift as before
    # else:
    #     new_s_type = int(new_s_type)
    #     allowed_skills = scenario.employees._collection[employee_id].skill_indices
    #     if curr_assignment:
    #         if new_s_type == curr_assignment[1]:
    #             allowed_skills = np.delete(allowed_skills, np.in1d(allowed_skills, curr_assignment[2]))
    #
    #     new_sk_type = random.choice(allowed_skills)


def get_allowed_s_type(solution, scenario, rule_collection, employee_id, d_index):
    """
    Get s_types that are allowed according to hard constraints and different than current assignment
    """
    # create allowed shifts to choose from
    # check if shift type succession rule is mandatory
    if rule_collection.collection['H3'].is_mandatory:
        allowed_shift_types = RuleH3().get_allowed_shift_types(solution=solution,
                                                               scenario=scenario,
                                                               employee_id=employee_id,
                                                               d_index=d_index)
    else:
        allowed_shift_types = scenario.shift_collection.shift_types_indices

    return allowed_shift_types

def get_allowed_skills(scenario, change_info):
    """
    Get skills that the employee has
    and exclude skills that will lead to the current shift-skill combination
    """

    allowed_skills = scenario.employees._collection[change_info["employee_id"]].skill_indices
    if change_info["current_working"]:
        if change_info["new_s_type"] == change_info["curr_ass"][1]:
            allowed_skills = np.delete(allowed_skills, np.in1d(allowed_skills, change_info["curr_ass"][2]))

    return allowed_skills


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

def fill_change_info_curr_ass(solution, change_info):
    """
    Create object to store information about the change
    :return:
    dict with d_index, old_assignment, new_assignment
    """

    change_info["current_working"] = solution.check_if_working_day(
        change_info["employee_id"],
        change_info["d_index"])

    change_info["curr_ass"] = tuple([change_info["d_index"],
                solution.shift_assignments[
                    change_info["employee_id"]][
                    change_info["d_index"]][
                    0],
                solution.shift_assignments[
                                         change_info["employee_id"]][
                                         change_info["d_index"]][
                                         1]]) \
        if change_info["current_working"] else None

    return change_info





