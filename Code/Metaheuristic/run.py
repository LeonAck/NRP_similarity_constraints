from copy import deepcopy
import cProfile
from leon_thesis.invoke.Domain.settings import Settings
from external.alfa import run_stage, run_stage_add_similarity
from leon_thesis.invoke.Domain.input_NRC import Instance
import Output.create_plots as plot
import os
import json
from Output.output import write_output_instance, collect_total_output, create_output_folder, create_json
from leon_thesis.invoke.output_from_alfa import create_output_dict


# similarity = False
# if similarity:
#     settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_similarity.json"
# else:
#     settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
#
# two_stage = True

def run_two_stage(settings_file_path, folder_name, output_folder=None, similarity=False):
    """
    Function to execute heuristic
    """
    f = open(settings_file_path)
    settings_json = json.load(f)

    settings = Settings(settings_json)

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
        # cProfile.run("run_stage(instance, settings.stage_2_settings, previous_solution=stage_1_solution)")
        if not similarity:
            heuristic_2, stage_2_solution = run_stage_add_similarity(instance, settings.stage_2_settings,
                                                                     previous_solution=stage_1_solution)
        else:
            heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings,
                                                      previous_solution=stage_1_solution)
        plot.objective_value_plot(heuristic_2, folder_name, suppress=True, output_folder=output_folder)
        plot.operator_weight_plot(heuristic_2, folder_name, suppress=True, output_folder=output_folder)
        plot.temperature_plot(heuristic_2, folder_name, suppress=True, output_folder=output_folder)

        return write_output_instance(heuristic_2, feasible=True)


def run_two_stage_one_input_one_output(input_dict):
    """
    Function to execute heuristic
    """

    settings = Settings(input_dict['settings'])

    instance = Instance(settings, input_dict)

    # run stage_1
    heuristic_1, stage_1_solution = run_stage(instance, settings.stage_1_settings)
    # check if first stage feasible

    if heuristic_1.stage_1_feasible:
        # run stage 2
        if not settings.similarity:
            heuristic_2, stage_2_solution = run_stage_add_similarity(instance, settings.stage_2_settings,
                                                                     previous_solution=stage_1_solution)
        else:
            heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings,
                                                      previous_solution=stage_1_solution)

    else:
        heuristic_2 = None

    output_dict = create_output_dict(instance.instance_name, heuristic_1, heuristic_2)
    return output_dict


def run_multiple_files(file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions",
                       settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json",
                       similarity=False):
    output_folder = create_output_folder()
    output = {}
    folders_list = os.listdir(file_path)
    if similarity:
        folders_list = keep_files_with_8_weeks(folders_list)

    for folder_name in [folders_list[0]]:
        output[folder_name] = run_two_stage(settings_file_path, folder_name=folder_name, output_folder=output_folder,
                                            similarity=similarity)

    output['totals'] = collect_total_output(output)

    # save json in output_files folder
    create_json(output_folder, output)


def keep_files_with_8_weeks(folders_list):
    return [folder_name for folder_name in folders_list if folder_name[4] == '8']


def run_one_stage(settings_file_path, stage_number=2):
    settings = Settings(settings_file_path)
    instance = Instance(settings)
    if stage_number == 2:
        heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings)
    else:
        heuristic_2, stage_2_solution = run_stage(instance, settings.stage_1_settings)

    print(stage_2_solution.obj_value)
    print(stage_2_solution.violation_array)
    print(heuristic_2.n_iter)
    return stage_2_solution
