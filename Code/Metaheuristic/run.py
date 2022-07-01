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
    update_dict_per_instance_metric, calc_min, add_feasibility_master, \
    add_violations_similarity_master, prepare_output_all_instances
from leon_thesis.invoke.output_from_alfa import create_output_dict
from external.alfa import execute_heuristic, execute_heuristic_2
from leon_thesis.invoke.utils.concurrency import parallel
from leon_thesis.invoke.main import run
from Input.prepare_input import folder_to_json


def run_multiple_files(frequency,
                       max_workers,
                       metrics=("best_solution", "best_solution_similarity", "best_solution_no_similarity"),
                       file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions",
                       similarity=False, reg_run=False, num_weeks=8):
    date_folder = create_date_time_for_folder()
    master_folder = "C:/Master_thesis/Code/Metaheuristic/output_files" + "/" + date_folder
    os.mkdir(master_folder)

    folders_list = os.listdir(file_path)

    if reg_run:
        folders_list = keep_files_with_weeks(folders_list, num_weeks)
        settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
    elif similarity:
        folders_list = keep_files_with_weeks(folders_list, 8)
        settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json"
    else:
        folders_list = keep_files_with_weeks(folders_list, 8)
        settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
    master_output = {k: {metric: [] for metric in metrics} for k in folders_list}
    for i in range(frequency):
        output_folder = create_output_folder(path=master_folder, folder_name=str(i))
        input_dicts = []

        for folder_name in folders_list:
            input_dicts.append(folder_to_json(
                path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                solution_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions",
                folder_name=folder_name, similarity=similarity,
                settings_file_path=settings_file_path,
                param=None, param_to_change=None, reg_run=reg_run)
            )



        # for argument in arguments:
        #     results.append(run(deepcopy(argument)))
        # run parallel
        arguments = [[{"input_dict": input_dict}] for input_dict in input_dicts]
        # result = execute_heuristic_2(arguments[0][0])
        results = parallel(execute_heuristic_2, deepcopy(arguments), max_workers=max_workers)
        # arguments = [[input_dict] for input_dict in input_dicts]
        # results = parallel(run, deepcopy(arguments), max_workers=max_workers)
        # results = run(arguments[0][0]['input_dict'])

        #
        print("done")

        master_output = prepare_output_all_instances(results, master_output, master_folder, folders_list, metrics, i, date_folder, output_folder)

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


def keep_files_with_weeks(folders_list, num_weeks):
    return [folder_name for folder_name in folders_list if folder_name[4] == str(num_weeks)]


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
