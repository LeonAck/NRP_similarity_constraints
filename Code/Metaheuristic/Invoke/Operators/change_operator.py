import random
import numpy as np
from general_functions import check_if_working_day
from copy import copy


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
    if change_info['feasible']:
        change_info["cost_increment"], change_info['violation_increment'] = calc_new_costs_after_change(solution, scenario, change_info)

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

    return np.matmul(violation_array, scenario.rule_collection.penalty_array), violation_array

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
        skill_indices = scenario.employees._collection[change_info["employee_id"]].skill_indices
        # get feasible days for given employee
        feasible_days = list(range(0, scenario.num_days_in_horizon))

        # check if we allow for understaffing compared to minimum requirement
        if scenario.rule_collection.collection['H2'].is_mandatory:
            feasible_days = remove_infeasible_days_understaffing(
                solution, change_info["employee_id"], feasible_days)

        while len(feasible_days) > 0 and not feasible:
            # choose day
            change_info["d_index"] = random.choice(feasible_days)
            change_info = fill_change_info_curr_ass(solution.shift_assignments, change_info)

            # get allowed shifts for insertion for given day
            allowed_shift_types = get_allowed_s_type(solution, scenario, change_info["employee_id"],
                                                     change_info["d_index"])

            # add off day to options if employee currently not working
            if change_info["current_working"]:
                allowed_shift_types.append("off")

            while len(allowed_shift_types) > 0 and not feasible:
                # pick random shift type
                change_info["new_s_type"] = random.choice(allowed_shift_types)

                if change_info["new_s_type"] == "off":
                    feasible = True
                    change_info["new_working"] = False
                else:
                    change_info['new_s_type'] = int(change_info['new_s_type'])
                    # get allowed shifts for this shift type
                    allowed_skills = get_allowed_skills(skill_indices, change_info)

                    # check if there are allowed shift types
                    if len(allowed_skills) == 0:
                        try:
                            allowed_shift_types.remove(change_info['new_s_type'])
                        except ValueError:
                            print("erorr")
                    # = np.delete(allowed_shift_types,
                        #                                 np.where(allowed_shift_types==change_info["new_s_type"]))
                    else:
                        change_info["new_sk_type"] = random.choice(allowed_skills)
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



def remove_infeasible_days_understaffing(solution, employee_id, feasible_days):
    """
    Remove days where a employee cannot be removed since this might cause understaffing
    :Return:
    list of feasible days
    """

    feasible_working_days = set(feasible_days).intersection(set(solution.working_days[employee_id]))
    # [d_index for d_index in feasible_days if solution.check_if_working_day(employee_id, d_index)]

    return [d_index for d_index in feasible_days if d_index not in feasible_working_days or (d_index in feasible_working_days
                and solution.diff_min_request[
                    tuple([d_index,
                   solution.shift_assignments[employee_id][d_index][1],
                   solution.shift_assignments[employee_id][d_index][0]])] > 1)
            ]


def get_allowed_s_type(solution, scenario, employee_id, d_index):
    """
    Get s_types that are allowed according to hard constraints and different than current assignment
    """
    # create allowed shifts to choose from
    # check if shift type succession rule is mandatory
    if scenario.rule_collection.collection['H3'].is_mandatory:
        allowed_shift_types = get_allowed_shift_types(solution.shift_assignments,
                                                               allowed_shift_types=copy(scenario.shift_collection.shift_types_indices),
                                                               num_days_in_horizon=scenario.num_days_in_horizon,
                                                               forbidden_shift_type_successions=scenario.forbidden_shift_type_successions,
                                                               last_assigned_shift=solution.last_assigned_shift,
                                                               employee_id=employee_id,
                                                               d_index=d_index)
    else:
        allowed_shift_types = copy(scenario.shift_collection.shift_types_indices)

    return allowed_shift_types


def get_allowed_skills(skill_indices, change_info):
    """
    Get skills that the employee has
    and exclude skills that will lead to the current shift-skill combination
    """

    allowed_skills = copy(skill_indices)
    if change_info["current_working"]:
        if change_info["new_s_type"] == change_info["curr_s_type"]:
            allowed_skills = np.delete(allowed_skills, np.in1d(allowed_skills, change_info["curr_sk_type"]))

    return allowed_skills


def fill_change_info_curr_ass(shift_assignments, change_info):
    """
    Create object to store information about the change
    :return:
    dict with d_index, old_assignment, new_assignment
    """

    change_info["current_working"] = check_if_working_day(shift_assignments,
        change_info["employee_id"],
        change_info["d_index"])

    # add new s type
    change_info["curr_s_type"] = shift_assignments[
                    change_info["employee_id"]][
                    change_info["d_index"]][
                    0] \
        if change_info["current_working"] else None
    # add new sk type
    change_info["curr_sk_type"] = shift_assignments[
                                         change_info["employee_id"]][
                                         change_info["d_index"]][
                                         1] \
        if change_info["current_working"] else None

    change_info["new_working"] = None

    return change_info

def find_difference_dict(first_dict, second_dict):
    return { k : second_dict[k] for k in set(second_dict) - set(first_dict) }

def get_allowed_shift_types(shift_assignments, allowed_shift_types, num_days_in_horizon,
                            forbidden_shift_type_successions,
                            last_assigned_shift, employee_id, d_index):
    """
    For a given day get the shift types that are not allowed given
    the assignment the day before and the day after
    """

    if d_index > 0:
        # check if working the day before
        if check_if_working_day(shift_assignments, employee_id, d_index - 1):
            # get shift type of the day before
            shift_type_day_before = shift_assignments[employee_id][d_index - 1][0]

            # delete forbidden shifts
            allowed_shift_types = [s_type for s_type in allowed_shift_types if
                                   s_type not in set(forbidden_shift_type_successions[shift_type_day_before][1])]

    elif d_index == 0 and last_assigned_shift[employee_id] != -1:

        # delete forbidden shifts
        allowed_shift_types = [s_type for s_type in allowed_shift_types if
                               s_type not in set(
                                   forbidden_shift_type_successions[last_assigned_shift[employee_id]][1])]

    # check if there is a day after
    if d_index < num_days_in_horizon - 1:
        # check if working the day after
        if check_if_working_day(shift_assignments, employee_id, d_index + 1):
            # get shift type of day after
            shift_type_day_after = shift_assignments[employee_id][d_index + 1][0]
            allowed_shift_types = [s_type for s_type in allowed_shift_types if
                                   shift_type_day_after not in forbidden_shift_type_successions[s_type][1]]

    return allowed_shift_types





