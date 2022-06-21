from Output.output import create_json, collect_total_output, create_date_time_for_folder, write_output_instance
from leon_thesis.invoke.Domain.settings import Settings
from leon_thesis.invoke.Domain.input_NRC import Instance
from leon_thesis.invoke.utils.concurrency import parallel
from external.alfa import execute_heuristic
from leon_thesis.invoke.main import run
from Input.prepare_input import folder_to_json
import Output.create_plots as plot
import os
import random
import json
import numpy as np
import cProfile
from copy import deepcopy


def run_parameter_tuning_random(number_of_instances, params=(["change"], ['change', 'swap'],
                                                             ['change', 'swap', 'greedy_change']),
                                param_to_change="operators",
                                week_range=(4, 10), nurse_range=(30, 120),
                                similarity=False,
                                file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                                settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
    tuning_folder = create_date_time_for_folder()
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output_files/tuning/" + tuning_folder)

    folders_list = os.listdir(file_path)
    # make selection of folders
    folders_list = keep_files_within_selection(folders_list, week_range, nurse_range)
    tuning_list = []
    for i in range(0, number_of_instances):
        tuning_list.append(get_random_folder(folders_list, file_path))

    for param in params:
        output_folder = "tuning/" + tuning_folder + "/" + str(param)
        create_output_folder_no_date(
            "C:/Master_thesis/Code/Metaheuristic/output_files/tuning/" + tuning_folder + "/" + str(param))
        output = {}
        input_dicts = []

        # create list of inputs
        for folder_name in tuning_list:
            input_dicts.append(folder_to_json(file_path, folder_name, similarity, settings_file_path, param=param,
                                              param_to_change=param_to_change))
        # run parallel
        arguments = [[{"input_dict": input_dict}] for input_dict in input_dicts]
        # arguments = [[input_dict] for input_dict in input_dicts]

        try:
            results = parallel(execute_heuristic, arguments, max_workers=40)
            print("done")
        except RuntimeError:
            print("hi")
            continue

        # create output dict
        output = {results[i]['folder_name']: results[i] for i in range(len(tuning_list))}
        # create plots
        plot.all_plots(output, output_folder, stage_2=False)

        # remove unnecessary information
        keys_to_keep = {"iterations", "run_time", "best_solution", "violation_array", "feasible"}

        for result in results:
            result["stage_1"] = {k: v for k, v in result["stage_1"].items() if k in keys_to_keep}
            if "stage_2" in result:
                result["stage_2"] = {k: v for k, v in result["stage_2"].items() if k in keys_to_keep}

        # calc totals
        output['totals'] = collect_total_output(output)

        # save json in output_files folder
        create_json(output_folder, output)


def tuning_single_run_create_plot(repeat, params, param_to_change, max_workers,
                                  week_range=(4, 10), nurse_range=(30, 120),
                                  similarity=False,
                                  file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                                  settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
    tuning_folder = create_date_time_for_folder()
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output_files/tuning/" + tuning_folder)

    folders_list = os.listdir(file_path)

    # make selection of folders
    folders_list = keep_files_within_selection(folders_list, week_range, nurse_range)
    tuning_list = [get_random_folder(folders_list, file_path)]
    # create param dict for plots
    param_dict = {param: {} for param in params}

    for param in params:
        input_dicts = []

        # create list of inputs
        for i in range(repeat):
            input_dicts.append(folder_to_json(file_path, tuning_list[0], similarity, settings_file_path, param=param,
                                              param_to_change=param_to_change))

        # run parallel
        # arguments = [[{"input_dict": input_dict}] for input_dict in input_dicts]
        arguments = [[input_dict] for input_dict in input_dicts]
        # for i in range(1, 10):
        #     results = run(deepcopy(arguments[0][0]))
        results = parallel(run, deepcopy(arguments), max_workers=max_workers)

        max_iter, max_run_time, avg_obj_values = get_info_single_instance_multiple_params(results)

        param_dict = update_info_plot_multiple_params(param_dict, param, max_iter, max_run_time, avg_obj_values)

    # create plot with line of avg objective
    plot.create_obj_value_multiple_params(param_dict, tuning_list[0])

def get_info_single_instance_multiple_params(results):
    max_run_time = 0
    max_iter = 0

    for result in results:
        if result['stage_1']['feasible']:
            if result['stage_2']['iterations'] > max_iter:
                max_iter = result['stage_2']['iterations']
            if result['stage_2']['run_time'] > max_run_time:
                max_run_time = result['stage_2']['run_time']

    if max_run_time > 0:
        avg_obj_values = np.zeros(max_iter-1)
        for result in results:
            if result['stage_1']['feasible']:
                # create array of length as max_iter
                obj_values_array = np.concatenate((np.array(result['stage_2']['obj_values']),
                                                   np.zeros(max_iter - result['stage_2']['iterations'])))
                avg_obj_values += obj_values_array
    else:
        avg_obj_values = None

    return max_iter, max_run_time, avg_obj_values


def update_info_plot_multiple_params(param_dict, param, max_iter, max_run_time, avg_obj_values):
    if avg_obj_values is not None:
        param_dict[param]['run_time'] = max_run_time
        param_dict[param]['iterations'] = max_iter
        param_dict[param]['obj_values'] = avg_obj_values

    return param_dict

def get_random_folder(folders_list, file_path):
    instance_folder = random.choice(folders_list)
    history_file = random.choice(range(0, 2))
    weeks = pick_random_weeks(file_path, instance_folder)

    return transform_instance_name(instance_folder, history_file, weeks)


def pick_random_weeks(file_path, instance_folder):
    num_week_files = len(os.listdir(file_path + "/" + instance_folder)) - 4

    num_weeks = int(instance_folder[5:])

    return random.choices(range(0, num_week_files), k=num_weeks)


def transform_instance_name(instance_name, history, weeks):
    list_of_items = [instance_name[1:4], instance_name[5:], str(history)] + [str(week) for week in weeks]
    return "-".join(list_of_items)


def keep_files_within_selection(folders_list, week_range, nurse_range):
    return [folder_name for folder_name in folders_list if week_range[0] <= int(folder_name[5:]) <= week_range[1]
            and nurse_range[0] <= int(folder_name[1:4]) <= nurse_range[1]]


def create_output_folder_no_date(path="C:/Master_thesis/Code/Metaheuristic/output_files"):
    os.mkdir(path)

    # create plots folder
    os.mkdir(path + "/obj_plots")
    os.mkdir(path + "/weight_plots")
    os.mkdir(path + "/temp_plots")


def run_two_stage_tuning(folder_name, output_folder, param, similarity=False,
                         settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
    """
    Function to execute heuristic
    """
    settings = Settings(settings_file_path, param)

    instance = Instance(settings, folder_name)

    # run stage_1
    heuristic_1, stage_1_solution = run_stage(instance, settings.stage_1_settings)
    # check if first stage feasible
    if not heuristic_1.stage_1_feasible:
        plot.objective_value_plot(heuristic_1, folder_name, suppress=True, output_folder=output_folder)
        plot.operator_weight_plot(heuristic_1, folder_name, suppress=True, output_folder=output_folder)
        plot.temperature_plot(heuristic_1, folder_name, suppress=True, output_folder=output_folder)
        return write_output_instance(heuristic_1, feasible=False)

    else:
        # run stage 2
        heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings,
                                                  previous_solution=stage_1_solution)
        plot.objective_value_plot(heuristic_2, folder_name, suppress=True, output_folder=output_folder)
        plot.operator_weight_plot(heuristic_2, folder_name, suppress=True, output_folder=output_folder)
        plot.temperature_plot(heuristic_2, folder_name, suppress=True, output_folder=output_folder)

        return write_output_instance(heuristic_2, feasible=True)


def get_list_random_folders(number_of_instances, file_path, week_range, nurse_range):
    folders_list = os.listdir(file_path)
    # make selection of folders
    folders_list = keep_files_within_selection(folders_list, week_range, nurse_range)
    tuning_list = []
    for i in range(0, number_of_instances):
        tuning_list.append(get_random_folder(folders_list, file_path))

    return tuning_list
