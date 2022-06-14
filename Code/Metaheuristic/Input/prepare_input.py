from copy import copy
import os
import json
import numpy as np


def folder_to_json(path, folder_name, similarity, settings_file_path, param=None, param_to_change=None, solution_path=None, reg_run=False):
    f = open(settings_file_path)
    settings_json = json.load(f)
    # tuning. T
    if param:
        settings_json['stage_1_settings']['heuristic_settings'][param_to_change] = param
        settings_json['stage_2_settings']['heuristic_settings'][param_to_change] = param
    # information for loading instance

    instance_name = deduce_folder_name(folder_name)
    history_file = int(folder_name[6])
    weeks = get_weeks_from_folder_name(folder_name, reg_run)

    # create dict to store json files
    history_data, scenario_data, weeks_data = load_instance(path, instance_name, weeks, history_file)

    skills = scenario_data['skills']

    # get reference period
    if not param:
        ref_assignments = prev_solution_to_ref_assignments(solution_path,
                                                           folder_name, scenario_data, weeks, skills)
        for k in ref_assignments.keys():
            ref_assignments[k] = [ref_assignments[k][:, 0].tolist(), ref_assignments[k][:, 1].tolist()]
    else:
        ref_assignments = None

    instance_data = create_instance_data_dict(history_data, scenario_data,
                                              weeks_data, instance_name, history_file, weeks, skills, ref_assignments, settings_json, folder_name)
    return instance_data


def create_instance_data_dict(history_data, scenario_data, weeks_data, instance_name, history_file, weeks, skills,
                              ref_assignments, settings_json, folder_name):
    instance_data = {}
    instance_data['folder_name'] = folder_name
    instance_data['instance_name'] = instance_name
    instance_data['history_file'] = history_file
    instance_data['weeks'] = weeks
    instance_data['history_data'] = history_data
    instance_data['scenario_data'] = scenario_data
    instance_data['weeks_data'] = weeks_data
    instance_data['ref_assignments'] = ref_assignments
    instance_data['skills'] = skills
    instance_data['settings'] = settings_json

    return instance_data


def deduce_folder_name(folder_name):
    num_nurses = folder_name[0:3]
    num_weeks = folder_name[4]

    return "n{}w{}".format(num_nurses, num_weeks)


def get_weeks_from_folder_name(folder_name, reg_run=False):
    folder_name_copy = copy(folder_name)
    week_string = folder_name_copy[7:]
    weeks = []
    while len(week_string) > 0:
        weeks.append(int(week_string[1]))
        week_string = week_string[2:]
    return weeks[4:] if not reg_run else weeks


def load_instance(path, instance_name, weeks, history_file):
    """
    Function to load instances and save into dicitonary
    :return:
    dictionary with files
    keys as filenames and value are dictionaries
    """

    # get list of json files
    path_to_json = instance_to_path(path, instance_name)

    all_json_files = get_json_files(path_to_json)

    # create path for each json file
    file_path = path_to_json + "/{}".format(get_history_file(all_json_files, history_file) + ".json")

    # add json file to dictionary
    history_data = load_json_file(file_path)

    # create path for each json file
    file_path = path_to_json + "/{}".format(get_scenario_file(all_json_files) + ".json")

    # add json file to dictionary
    scenario_data = load_json_file(file_path)

    weeks_data = []

    for file in get_week_files(all_json_files, weeks):
        # create path for each json file
        file_path = path_to_json + "/{}".format(file + ".json")

        # add json file to dictionary
        weeks_data.append(load_json_file(file_path))

    return history_data, scenario_data, weeks_data


def instance_to_path(path, instance_name):
    """
    Function to create a path from the name of the instance
    :return:
    string stating the path of the folder
    """
    return path + "/{}".format(instance_name)


def get_json_files(path_to_json):
    """Function to get list of json files in folder
    :return:
    list of json files
    """

    return [pos_json.rstrip(".json") for pos_json
            in os.listdir(path_to_json) if pos_json.endswith('.json')]


def load_json_file(file_path):
    """
    Function to load json file
    :param file_path:
    :return:
    json_file in dictionary format
    """
    f = open(file_path)
    json_value = json.load(f)

    return json_value


def get_history_file(list_of_files, history_file):
    """
    Function to get name of right history file
    """
    return [file for file in list_of_files if file.startswith("H0")
            and file.endswith(str(history_file))][0]


def get_scenario_file(list_of_files):
    """
    Function to get scenario file
    """
    scenario_file = [file for file in list_of_files if file.startswith("Sc")]

    if not scenario_file:
        raise Exception("Folder does not contain a scenario file")

    else:
        return scenario_file[0]


def get_week_files(list_of_files, weeks):
    """
    Function to get selection of week files chosen in settings
    """
    weeks_strings = ["-" + str(i) for i in weeks]
    week_files = []
    for string in weeks_strings:
        for file in list_of_files:
            if file.startswith("WD") \
                    and file.endswith(string):
                week_files.append(file)
    return week_files


def prev_solution_to_ref_assignments(solution_path, folder_name, scenario_data, weeks, skills):
    solution_path = solution_path + "/{}/solution.txt".format(folder_name)
    # create object for ref_assignments
    ref_assignments = {}
    for nurse in scenario_data['nurses']:
        ref_assignments[nurse['id']] = np.full((len(weeks) * 7, 2), -1, dtype=int)

    with open(solution_path, "rb") as s_file:
        lines = s_file.readlines()
    for line in lines[1:-4]:
        split_line = prepare_line_for_assignment(scenario_data, skills, line)
        if split_line[1] <= 27:
            ref_assignments[split_line[0]][split_line[1]] = np.array([split_line[2], split_line[3]])
    return ref_assignments


def prepare_line_for_assignment(scenario_data, skills, line):
    split_line = str(line).split(" ")
    split_line[0] = split_line[0][2:]
    split_line[1] = int(split_line[1][:-4])
    split_line[2] = get_index_of_shift_type(scenario_data, split_line[2])
    split_line[3] = get_index_of_skill_type(skills, split_line[3][:-5])
    return split_line


def get_index_of_shift_type(scenario_data, shift_type_id):
    """
    Function to get index when given a skill type
    """
    for index, s_type in enumerate(scenario_data['shiftTypes']):
        if s_type['id'] == shift_type_id:
            return index


def get_index_of_skill_type(skills, skill_type):
    return skills.index(skill_type)
