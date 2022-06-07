# from external import alfa
from utils.concurrency import parallel
# from Invoke.utils.session import init_session
from tuning import run_parameter_tuning_random, get_random_folder, keep_files_within_selection, create_output_folder_no_date, run_two_stage_tuning
import Input.setting_files as settings_file
from output import create_json, collect_total_output, create_date_time_for_folder, write_output_instance
import os

def run(x=4 ,settings_file="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):

    return x * 2
# def run(problems, options={}):
#     session = init_session()
#     concurrency = options.get("autoAssign", {}).get(
#         "concurrency", settings.REQUEST.DEFAULT_CONCURRENCY
#     )
#
#     arguments = [[session, _id, problem, options] for _id, problem in problems.items()]
#     results = parallel(solve, arguments, max_workers=concurrency)
#     results = {key: value for key, value in results}
#     if "mergePolicy" not in options or len(results.keys()) <= 1:
#         return results
#
#     return None

def run(number_of_instances, params=18,
                                week_range=(4, 10), nurse_range=(30, 120),
                                similarity=False,
                                file_path="C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/Datasets/JSON",
                                settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"):
    tuning_folder = create_date_time_for_folder()
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output/tuning/" + tuning_folder)

    folders_list = os.listdir(file_path)
    # make selection of folders
    folders_list = keep_files_within_selection(folders_list, week_range, nurse_range)
    tuning_list = []
    for i in range(0, number_of_instances):
        tuning_list.append(get_random_folder(folders_list, file_path))

    for param in [params]:
        output_folder = "tuning/" + tuning_folder + "/" + str(param)
        create_output_folder_no_date("C:/Master_thesis/Code/Metaheuristic/output/tuning/" + tuning_folder + "/" + str(param))
        output = {}

        output[folder_name] = run_two_stage_tuning(settings_file_path,
                                                   folder_name=folder_name,  output_folder=output_folder,
                                             similarity=similarity, param=param)
        results = parallel(run_two_stage_tuning, arguments, max_workers=concurrency)

        output['totals'] = collect_total_output(output)

        # save json in output folder
        create_json(output_folder, output)
