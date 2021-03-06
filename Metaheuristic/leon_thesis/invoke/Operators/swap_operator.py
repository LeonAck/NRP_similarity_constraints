from Rules.RuleH3 import check_forbidden_before_day
from Rules.RuleS2Max import RuleS2Max
from Rules.RuleS7 import RuleS7
from Rules import RuleS8RefDay
from Rules.RuleS8RefShift import RuleS8RefShift
from Rules import RuleS8RefSkill

import random
import numpy as np


def swap_operator(solution, scenario):
    """
        Function to swap the assignments of two skill-compatible nurses for k
        consecutive days
        Skill-compatible means that the nurses have the same skill set

        :return:
        swap_info
    """
    # get a change that is allowed by hard constraints
    swap_info = get_feasible_swap(solution, scenario, solution.k_swap)

    # get stretch information for swap
    swap_info = get_stretch_information_swap(solution, swap_info)

    if "S7" in solution.rules:
        swap_info = RuleS7().incremental_working_weekends_swap(solution, swap_info)
    if "S8RefDay" in solution.rules:
        swap_info = RuleS8RefDay().check_comparison_swap(solution, swap_info, RuleS8RefDay().compare_function,
                                                      solution.ref_comparison_day_level, "ref_comparison_day_level")

    if "S8RefShift" in solution.rules:
        swap_info = RuleS8RefShift().check_comparison_swap(solution, swap_info, "ref_comparison_shift_level")

    if "S8RefSkill" in solution.rules:
        swap_info = RuleS8RefSkill().check_comparison_swap(solution, swap_info, "ref_comparison_skill_level")

    # add penalty to objective
    if swap_info['feasible']:
        swap_info["cost_increment"], swap_info['violation_increment'] \
            = calc_new_costs_after_swap(solution, swap_info)

    return swap_info

def calc_new_costs_after_swap(solution, swap_info):
    """
    Function to calculate the number of violations given a change operations
    :return:
    array with violations per rule
    """
    # calculate incremental penalties
    violation_array = np.zeros(len(solution.rule_collection.soft_rule_collection))
    relevant_rules = solution.rule_collection.soft_rule_collection.collection
    for i, rule in enumerate(relevant_rules.values()):
        if rule.swap:
            violation_array[i] = rule.incremental_violations_swap(solution, swap_info, rule.id)

    return np.matmul(violation_array, solution.rule_collection.penalty_array), violation_array

def get_feasible_swap(solution, scenario, k):
    """
    Function to find a swap between to nurses that are skill-compatible and
    is allowed by shift type successions
    """
    feasible = False
    # create object to store information
    infeasible_combinations = []
    feasible_employees = list((scenario.employees._collection.keys()))
    k_chosen = random.randrange(1, k+1)
    while not feasible:
        employee_id_1, employee_id_2, compatible = find_skill_compatible_employees(feasible_employees,
                                                                                   scenario.employees,
                                                                                   infeasible_combinations)

        if compatible:
            feasible_days = find_feasible_days_swap(solution, scenario, k_chosen, employee_id_1, employee_id_2)

            if feasible_days:
                swap_d_index = random.choice(feasible_days)
                feasible = True

        # remove infeasible combinations of nurses
        infeasible_combinations.append([employee_id_1, employee_id_2])

    if feasible:
        # create information object
        swap_info = create_swap_info(employee_id_1, employee_id_2, swap_d_index, k_chosen)
        swap_info['feasible'] = True
    else:
        swap_info = {}
        swap_info['feasible'] = False

    return swap_info


def find_feasible_days_swap(solution, scenario, k, employee_id_1, employee_id_2):
    """
    Find a swap that is allowed by the shift type successions
    Start and end-point of stretch of nurse 1 can be entered in shift_assignment
    of nurse 2, and vice versa.
    :return:
    start and end date of swap
    """
    # check what days are possible as a starting date for k number of days
    feasible_days = list(range(0, scenario.num_days_in_horizon - k))

    # for each day in range get assignmetns of nurse 1
    # for each assignment of nurse 1, find the non-forbidden assignmetns of nurse 2
    # this returns a list of feasible days
    feasible_days = check_one_way_swap(solution, k, feasible_days, employee_id_1, employee_id_2)
    feasible_days = check_one_way_swap(solution, k, feasible_days, employee_id_2, employee_id_1)

    # for each day in feasible days get assignments of nurse 2
    # for each assignments of nurse 2, check whether they match the assignments of nurse 1
    # this should result into a list or None

    return feasible_days


def create_swap_info(employee_id_1, employee_id_2, start_index, k):
    swap_info = {}

    swap_info['employee_id_1'] = employee_id_1
    swap_info['employee_id_2'] = employee_id_2
    swap_info['start_index'] = start_index
    swap_info['end_index'] = start_index + k - 1
    swap_info['k_swap'] = k

    return swap_info


def check_one_way_swap(solution, k, feasible_days, employee_id_1, employee_id_2):
    """
    Function to check for list of feasible days whether a swap can be
    made for a stretch starting at d_index in feasible days
    """

    for d_index in feasible_days:
        # collect whether start index is infeasible
        start_index_check = check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
                                               employee_id_1,
                                               employee_id_2,
                                               d_index)

        end_index_check = check_forbidden_before_day(solution, solution.forbidden_shift_type_successions,
                                               employee_id_2,
                                               employee_id_1,
                                               d_index + k)

        if start_index_check or end_index_check:
            feasible_days.remove(d_index)

    return feasible_days

def find_skill_compatible_employees(feasible_employees, employee_collection, infeasible_combinations):
    compatible = False
    employee_id_1 = random.choice(feasible_employees)
    skill_set_id = employee_collection._collection[employee_id_1].skill_set_id

    employees_w_skill_set = [employee_id for employee_id in feasible_employees
                             if employee_collection._collection[employee_id].skill_set_id == skill_set_id
                             and employee_id != employee_id_1]

    # remove combinations that have already been checked as infeasible
    for combination in infeasible_combinations:
        if employee_id_1 in combination:
            combination.remove(employee_id_1)
            try:
                if combination[0] in employees_w_skill_set:
                    employees_w_skill_set.remove(combination[0])
            except IndexError:
                pass

    # check if nonempty
    if employees_w_skill_set:
        employee_id_2 = random.choice(employees_w_skill_set)
        compatible = True
    else:
        employee_id_2 = None

    return employee_id_1, employee_id_2, compatible

def swap_assignments(solution, d_index, employee_id_1, employee_id_2):
    # save stretch of employee 1
    stretch_1 = solution.shift_assignments[employee_id_1][d_index:d_index+solution.k_swap-1, ]

    # replace stretch of employee 1 with the one from employee 2
    solution.shift_assignments[employee_id_1][d_index:d_index+solution.k_swap-1, ] \
        = solution.shift_assignments[employee_id_2][d_index:d_index+solution.k_swap-1, ]

    # replace stretch of employee 1 with the one from employee 2
    solution.shift_assignments[employee_id_2][d_index:d_index+solution.k_swap-1, ] \
        = stretch_1

    return solution


def get_stretch_information_swap(solution, swap_info):
    """
    Function to find for the exchanged streaks of consecutive days
    the work, off and shift stretches in the streak
    We only save the stretches that are completely in the streak
    """
    if "S2Max" in solution.rules or "S2Min" in solution.rules:
        swap_info = collect_edge_stretches(swap_info, solution.work_stretches, "work_stretches")
        swap_info = stretches_in_range(swap_info, solution.work_stretches, "work_stretches")
        swap_info['work_stretches_new'] = RuleS2Max().collect_new_stretches(solution, solution.work_stretches,
                                                                                swap_info, "work_stretches")

    if "S3Max" in solution.rules or "S3Min" in solution.rules:
        swap_info = collect_edge_stretches(swap_info, solution.day_off_stretches, "day_off_stretches")
        swap_info = stretches_in_range(swap_info, solution.day_off_stretches, "day_off_stretches")
        swap_info['day_off_stretches_new'] = RuleS2Max().collect_new_stretches(solution, solution.day_off_stretches,
                                                                                swap_info, "day_off_stretches")

    if "S2ShiftMax" in solution.rules or "S2ShiftMin" in solution.rules:
        for s_index in range(0, solution.num_shift_types):
            stretch_name = "shift_stretches_{}".format(s_index)
            swap_info = collect_edge_stretches(swap_info, solution.shift_stretches[s_index], stretch_name)
            swap_info = stretches_in_range(swap_info, solution.shift_stretches[s_index], stretch_name)
            swap_info['{}_new'.format(stretch_name)] = RuleS2Max().collect_new_stretches(solution, solution.shift_stretches[s_index],
                                                                                   swap_info, stretch_name)
    return swap_info


def stretches_in_range(swap_info, stretch_object, object_name):
    day_range = range(swap_info['start_index']+1, swap_info['end_index'])

    for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
        stretches_in_swap = {}
        start_indices_to_keep = None
        for key, value in stretch_object[employee_id].items():
            if key in day_range and value['end_index'] in day_range:

                stretches_in_swap[key] = value
                if swap_info['edge_{}'.format(object_name)][swap_info['employee_id_{}'.format(2 - i)]]['end'] is not None \
                        and key == swap_info['edge_{}'.format(object_name)][swap_info['employee_id_{}'.format(2 - i)]]['end'][
                            'start_index']:
                    start_indices_to_keep = key

        swap_info['{}_{}'.format(object_name, i+1)] = stretches_in_swap
        swap_info['{}_{}_start_indices_to_keep'.format(object_name, i+1)] = start_indices_to_keep
    return swap_info


def collect_edge_stretches(swap_info, stretch_object, object_name):
    start_index = swap_info['start_index']
    end_index = swap_info['end_index']
    swap_info['edge_{}'.format(object_name)] = {swap_info['employee_id_1']: None, swap_info['employee_id_2']: None}
    swap_info['overlapping_{}'.format(object_name)] = {}
    for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
        overlapping_stretch = None
        edge_stretches_employee = {"start": None, "end": None}
        # TODO verkorten door uit te sluiten dat hij gaat zoeken naar overlapping stretches
        # wanneer ook inside stretches zijn
        for key, value in stretch_object[employee_id].items():
            if key <= start_index and value['end_index'] >= end_index:
                overlapping_stretch = create_stretch_new_format(key, value['end_index'])
            elif key <= start_index <= value['end_index']:
                edge_stretches_employee['start'] = create_stretch_new_format(key, value['end_index'])
            elif key <= end_index <= value['end_index']:
                edge_stretches_employee['end'] = create_stretch_new_format(key, value['end_index'])

        swap_info['edge_{}'.format(object_name)][employee_id] = edge_stretches_employee
        swap_info['overlapping_{}'.format(object_name)][employee_id] = overlapping_stretch

    return swap_info

def create_stretch_new_format(start_index, end_index):
    return {"start_index": start_index, "end_index": end_index, "length": end_index - start_index + 1}