import random
from Invoke.Constraints.Rules import RuleH3
import numpy as np


def change_operator(solution, scenario):
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
    change_info = get_feasible_change(solution, scenario)

    # add penalty to objective
    change_info["cost_increment"] = calc_new_costs_after_change(solution, scenario, change_info)

    return change_info


def calc_new_costs_after_change(solution, scenario, change_info):
    """
    Function to calculate the number of violations given a change operations
    :return:
    array with violations per rule
    """
    # calculate incremental penalties
    violation_array = np.zeros(len(scenario.rule_collection.soft_rule_collection))
    relevant_rules = scenario.rule_collection.soft_rule_collection.collection
    for i, rule in enumerate(relevant_rules.values()):
        violation_array[i] = rule.incremental_violations_change(solution, change_info, scenario)
    # TODO what if no penalty array
    return np.matmul(violation_array, scenario.rule_collection.penalty_array)

def get_feasible_change(solution, scenario):
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
        feasible_days = remove_infeasible_days_understaffing(
            solution, change_info["employee_id"], feasible_days)

        while len(feasible_days) > 0 and not feasible:
            # choose day
            change_info["d_index"] = random.choice(feasible_days)
            change_info = fill_change_info_curr_ass(solution, change_info)

            # get allowed shifts for insertion for given day
            allowed_shift_types = get_allowed_s_type(solution, scenario, change_info["employee_id"],
                                                     change_info["d_index"])

            # add off day to options if employee currently not working
            if change_info["current_working"]:
                allowed_shift_types = np.append(allowed_shift_types, "off") # todo replace "off" by a number

            while len(allowed_shift_types) > 0 and not feasible:
                # pick random shift type
                change_info["new_s_type"] = random.choice(allowed_shift_types)

                if change_info["new_s_type"] == "off":
                    feasible = True
                    change_info["new_working"] = False
                else:
                    # get allowed shifts for this shift type
                    allowed_skills = get_allowed_skills(scenario, change_info)

                    # check if there are allowed shift types
                    if len(allowed_skills) == 0:
                        allowed_shift_types = np.delete(allowed_shift_types,
                                                        np.in1d(allowed_shift_types,
                                                                change_info["new_s_type"]))
                    else:
                        change_info["new_sk_type"] = random.choice(allowed_skills)
                        change_info["new_working"] = True
                        if change_info["new_working"] and change_info["current_working"]:
                            print("yes")
                        feasible = True

            # if no allowed shift type for day, remove day and find new day
            feasible_days.remove(change_info["d_index"])

        # if no feasible day for change for employee, remove employee and find new employee
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


def get_allowed_s_type(solution, scenario, employee_id, d_index):
    """
    Get s_types that are allowed according to hard constraints and different than current assignment
    """
    # create allowed shifts to choose from
    # check if shift type succession rule is mandatory
    if scenario.rule_collection.collection['H3'].is_mandatory:
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

    change_info["new_working"] = None

    return change_info





