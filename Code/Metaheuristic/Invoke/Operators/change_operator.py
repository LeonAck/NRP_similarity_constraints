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

    employee_id, d_index, curr_assignment = get_feasible_removal(solution, scenario)

    allowed_shift_types = get_allowed_s_type(solution, scenario, rule_collection, employee_id, d_index)

    # pick random shift type
    new_s_type = random.choice(np.append(allowed_shift_types, "off"))
    # if off remove shift assignments
    if new_s_type == "off":
        solution.remove_shift_assignment(employee_id, d_index)
    # check if same shift as before
    else:
        allowed_skills = scenario.employees._collection[employee_id].skill_indices
        if curr_assignment:
            if new_s_type == curr_assignment[1]:
                allowed_skills = np.delete(allowed_skills, curr_assignment[2])

        new_sk_type = random.choice(allowed_skills)

        # update solution
        solution.replace_shift_assignment(employee_id, d_index, new_s_type, new_sk_type)

        # update solution information
        solution.update_information_insertion(solution, employee_id,
                                              d_index=d_index,
                                              s_index=int(new_s_type),
                                              sk_index=new_sk_type)
        if curr_assignment:
            solution.update_information_removal(solution, employee_id,
                                              assignment_info=curr_assignment)

    return None

def get_feasible_removal(solution, scenario):
    """
    Get employee that can be savely removed from current assignment without
    leading to understaffing
    """
    feasible = False
    n = 0
    while not feasible:
        # pick random nurse
        employee_id = random.choice(list(scenario.employees._collection.keys())) # remove nurse if picked before
        # pick a random day
        d_index = random.randint(0, scenario.num_days_in_horizon-1)
        # check if working on day
        if solution.check_if_working_day(employee_id, d_index):
            # get day assignment
            curr_assignment = tuple([d_index,
                                    solution.shift_assignments[employee_id][d_index][0],
                                    solution.shift_assignments[employee_id][d_index][1]])
            # check if removal does not lead to understaffing
            # if so, pick new day
            if solution.diff_min_request[curr_assignment]<1:
                feasible = True
        else:
            feasible = True
            curr_assignment = False

        if n > 100:
            print("No feasible solution found within {} iterations".format(n))
            break
        n = n+1

    if employee_id and curr_assignment:
        return employee_id, d_index, curr_assignment
    else:
        return employee_id, d_index, curr_assignment

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