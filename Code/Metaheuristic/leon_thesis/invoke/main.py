# from external import alfa
# from utils.concurrency import parallel
# from Invoke.utils.session import init_session
# from tuning import run_parameter_tuning_random, get_list_random_folders, create_output_folder_no_date, run_two_stage_tuning
# import Input.setting_files as settings_file
# from output_files import create_json, collect_total_output, create_date_time_for_folder, write_output_instance
# import os

def run(x=4):

    return x * 2
def run(instance, stage_settings, previous_solution=None):
    scenario = Scenario(stage_settings, instance)

    init_solution = BuildSolution(scenario, previous_solution)
    heuristic = Heuristic(scenario, stage_settings=stage_settings)
    best_solution = heuristic.run_heuristic(starting_solution=deepcopy(init_solution))

    return heuristic, best_solution


def run_stage_add_similarity(instance, stage_settings, previous_solution=None):
    scenario = Scenario(stage_settings, instance)

    init_solution = BuildSolution(scenario, previous_solution)
    heuristic = Heuristic(scenario, stage_settings=stage_settings)
    best_solution = heuristic.run_heuristic(starting_solution=deepcopy(init_solution))

    heuristic.final_violation_array = EndSolution(scenario, previous_solution=best_solution).violation_array
    return heuristic, best_solution
def run(number_of_instances, params=(18, 14),
                                week_range=(4, 10), nurse_range=(30, 120),
                                similarity=False,
                                file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                                settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
    tuning_folder = create_date_time_for_folder()
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output_files/tuning/" + tuning_folder)

    for param in params:
        output_folder = "tuning/" + tuning_folder + "/" + str(param)
        create_output_folder_no_date("C:/Master_thesis/Code/Metaheuristic/output_files/tuning/" + tuning_folder + "/" + str(param))
        output = {}

        folder_list = get_list_random_folders(number_of_instances, file_path, week_range, nurse_range)

        arguments = [[folder_name, output_folder, param] for folder_name in folder_list]

        results = parallel(run_two_stage_tuning, arguments, max_workers=40)
        results = {key: value for key, value in results}
        output['totals'] = collect_total_output(results)

        # save json in output_files folder
        create_json(output_folder, output)
