from copy import deepcopy
import cProfile
from Domain.settings import Settings
from Domain.scenario import Scenario
from Invoke.Initial_solution.initial_solution import BuildSolution
from Check.check_function_feasibility import FeasibilityCheck
from Heuristic import Heuristic
from Input.input_NRC import Instance
import create_plots as plot
import os
import numpy as np
import random
from output import write_output_instance, collect_total_output, create_output_folder, create_json

similarity = False
if similarity:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_similarity.json"
else:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"

two_stage = True


def run_stage(instance, stage_settings, previous_solution=None):
    scenario = Scenario(stage_settings, instance)

    init_solution = BuildSolution(scenario, previous_solution)
    heuristic = Heuristic(scenario, stage_settings=stage_settings)
    best_solution = heuristic.run_heuristic(starting_solution=deepcopy(init_solution))

    return heuristic, best_solution


def run_two_stage(settings_file_path, folder_name=None, instance_info=None, output_folder=None):
    """
    Function to execute heuristic
    """
    settings = Settings(settings_file_path)
    if folder_name:
        instance = Instance(settings, folder_name)
    else:
        instance = Instance(settings=settings, instance_info=instance_info)

    # run stage_1
    heuristic_1, stage_1_solution = run_stage(instance, settings.stage_1_settings)

    if not np.array_equal(stage_1_solution.violation_array, np.array([0,0])):
        plot.objective_value_plot(heuristic_1, instance.instance_name, suppress=True, output_folder=output_folder)
        plot.operator_weight_plot(heuristic_1, instance.instance_name, suppress=True, output_folder=output_folder)
        return write_output_instance(heuristic_1, feasible=False)

    else:
        # run stage 2
        # cProfile.run("run_stage(instance, settings.stage_2_settings, previous_solution=stage_1_solution)")
        heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings, previous_solution=stage_1_solution)

        plot.objective_value_plot(heuristic_2, instance.instance_name, suppress=True, output_folder=output_folder)
        plot.operator_weight_plot(heuristic_2, instance.instance_name, suppress=True, output_folder=output_folder)

        return write_output_instance(heuristic_2, feasible=True)

def run_one_stage(settings_file_path, stage_number=2):
    settings = Settings(settings_file_path)
    instance = Instance(settings)
    if stage_number == 2:
        heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings)
    else:
        heuristic_2, stage_2_solution = run_stage(instance, settings.stage_1_settings)

    print(stage_2_solution.obj_value)
    print(stage_2_solution.violation_array)
    print(stage_2_solution.change_counters)

    return stage_2_solution


def run_multiple_files(file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions",
                       settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json", similarity=False):
    output_folder = create_output_folder()
    output = {}
    folders_list = os.listdir(file_path)
    if similarity:
        folders_list = keep_files_with_8_weeks(folders_list)

    for folder_name in folders_list[2:4]:
        output[folder_name] = run_two_stage(settings_file_path, folder_name=folder_name, output_folder=output_folder)

    output['totals'] = collect_total_output(output)

    # save json in output folder
    create_json(output_folder, output)

def run_parameter_tuning_random(number_of_instances, week_range=(4, 10), nurse_range=(30, 80),
                                file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                                settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
    output_folder = create_output_folder()
    output = {}
    folders_list = os.listdir(file_path)
    # make selection of folders
    folders_list = keep_files_within_selection(folders_list, week_range, nurse_range)

    for i in range(0, number_of_instances):
        instance_folder = random.choice(folders_list)
        history_file = random.choice(range(0, 2))
        weeks = pick_random_weeks(file_path, instance_folder)
        instance_info = {"name": instance_folder, "history": history_file, "weeks": weeks}
        json_header = transform_instance_name(instance_folder, history_file, weeks)
        output[json_header] = run_two_stage(settings_file_path, instance_info=instance_info, output_folder=output_folder)

    output['totals'] = collect_total_output(output)

    # save json in output folder
    create_json(output_folder, output)
    return output

def pick_random_weeks(file_path, instance_folder):
    num_week_files = len(os.listdir(file_path + "/" + instance_folder)) - 4

    num_weeks = int(instance_folder[5:])

    return random.choices(range(0, num_week_files), k=num_weeks)

def keep_files_within_selection(folders_list, week_range, nurse_range):
    return [folder_name for folder_name in folders_list if week_range[0] <= int(folder_name[5:]) <= week_range[1]
            and nurse_range[0] <= int(folder_name[1:4]) <= nurse_range[1]]

def keep_files_with_8_weeks(folders_list):
    return [folder_name for folder_name in folders_list if folder_name[4] == '8']

def transform_instance_name(instance_name, history, weeks):
    list_of_items = [instance_name[1:4], instance_name[5:], str(history)] + [str(week) for week in weeks]
    return "-".join(list_of_items)


if __name__ == '__main__':
    if two_stage:
        run_two_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/two_stage_005.json")
    else:
        run_one_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/two_stage_005.json")

# cProfile.run("Heuristic(scenario).run_heuristic(starting_solution=deepcopy(init_solution))", sort=1)
