from copy import deepcopy
import cProfile
from leon_thesis.invoke.Domain.settings import Settings
from external.alfa import run_stage, run_stage_add_similarity
from leon_thesis.invoke.Domain.input_NRC import Instance
import Output.create_plots as plot
import os
import json
from Output.output import write_output_instance, collect_total_output, \
    create_output_folder, create_json, create_date_time_for_folder, \
    update_dict_per_instance_metric, calc_min, add_feasibility_master
from leon_thesis.invoke.output_from_alfa import create_output_dict
from external.alfa import execute_heuristic
from leon_thesis.invoke.utils.concurrency import parallel
from leon_thesis.invoke.main import run
from Input.prepare_input import folder_to_json


def run_multiple_files(frequency,
                       max_workers,
                       metrics=("best_solution", "best_solution_similarity", "best_solution_no_similarity"),
                       file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions",
                       similarity=False):
    date_folder = create_date_time_for_folder()
    master_folder = "C:/Master_thesis/Code/Metaheuristic/output_files" + "/" + date_folder
    os.mkdir(master_folder)


    folders_list = os.listdir(file_path)
    if similarity:
        folders_list = keep_files_with_8_weeks(folders_list)
        settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json"
    else:
        settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
    input_dicts = []

    master_output = {k: {metric: [] for metric in metrics} for k in folders_list}
    for i in range(frequency):
        output = {}
        output_folder = create_output_folder(path=master_folder, folder_name=str(i))

        for folder_name in folders_list:
            input_dicts.append(folder_to_json(
                path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                solution_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions",
                folder_name=folder_name, similarity=similarity,
                settings_file_path=settings_file_path,
                param=None, param_to_change=None)
                              )

        results = []
        # arguments = [[input_dict] for input_dict in input_dicts]
        # with open("C:/Master_thesis/Code/Metaheuristic/leon_thesis/input.json",
        #           "w") as output_obj:
        #     json.dump(input_dicts[0], output_obj)
        # for argument in arguments:
        #     results.append(run(deepcopy(argument)))
        # run parallel
        arguments = [[{"input_dict": input_dict}] for input_dict in input_dicts]
        results = parallel(execute_heuristic, deepcopy(arguments), max_workers=max_workers)

        # create output dict
        output = {folders_list[j]: results[i] for j in range(len(folders_list))}
        # create plots
        plot.all_plots(output, date_folder+"/" + output_folder)
        keys_to_keep = {"iterations", "run_time", "best_solution", "violation_array",
                        "feasible", 'best_solution_similarity', 'best_solution_no_similarity'}

        # remove unnecessary information
        for result in results:
            result["stage_1"] = {k: v for k, v in result["stage_1"].items() if k in keys_to_keep}
            if "stage_2" in result:
                result["stage_2"] = {k: v for k, v in result["stage_2"].items() if k in keys_to_keep}


        output['totals'] = collect_total_output(output)

        # save json in output_files folder
        with open(master_folder+"/"+str(i)+"/output.json",
                  "w") as output_obj:
            json.dump(output, output_obj)

        # update master output
        master_output = update_dict_per_instance_metric(master_output, output, metrics)
        master_output = add_feasibility_master(master_output, output)
        # print(master_output)
    # store master file
    master_output = calc_min(master_output, metrics, frequency)
    with open(master_folder + "/summary.json",
              "w") as output_obj:
        json.dump(master_output, output_obj)


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

# def run_two_stage_one_input_one_output(input_dict):
#     """
#     Function to execute heuristic
#     """
#
#     settings = Settings(input_dict['settings'])
#
#     instance = Instance(settings, input_dict)
#
#     # run stage_1
#     heuristic_1, stage_1_solution = run_stage(instance, settings.stage_1_settings)
#     # check if first stage feasible
#
#     if heuristic_1.stage_1_feasible:
#         # run stage 2
#         if not settings.similarity:
#             heuristic_2, stage_2_solution = run_stage_add_similarity(instance, settings.stage_2_settings,
#                                                                      previous_solution=stage_1_solution)
#         else:
#             heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings,
#                                                       previous_solution=stage_1_solution)
#
#     else:
#         heuristic_2 = None
#
#     output_dict = create_output_dict(instance.instance_name, heuristic_1, heuristic_2)
#     return output_dict
