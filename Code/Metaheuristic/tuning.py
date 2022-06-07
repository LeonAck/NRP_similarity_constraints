from run import run_two_stage, run_two_stage_one_input_one_output
from Output.output import create_json, collect_total_output, create_date_time_for_folder, write_output_instance
from leon_thesis.invoke.Domain.settings import Settings
from Input.input_NRC import Instance
from Input.prepare_input import folder_to_json
from run import run_stage
import Output.create_plots as plot
import os
import random


def run_parameter_tuning_random(number_of_instances, params=(18, 24), param_to_change="initial_temp",
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
        create_output_folder_no_date("C:/Master_thesis/Code/Metaheuristic/output_files/tuning/" + tuning_folder + "/" + str(param))
        output = {}
        # TODO parallel

        for folder_name in tuning_list:
            input_dict = folder_to_json(file_path, folder_name, similarity, settings_file_path, param=param, param_to_change=param_to_change)
            output[folder_name] = run_two_stage_one_input_one_output(input_dict)

        plot.all_plots(output, output_folder, input_dict)

        output['totals'] = collect_total_output(output)

        # save json in output_files folder
        create_json(output_folder, output)


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


def run_two_stage_tuning(folder_name, output_folder, param, similarity=False, settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
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