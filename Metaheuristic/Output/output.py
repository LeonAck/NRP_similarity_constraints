from datetime import datetime
import os
import numpy as np
import json
from statistics import mean, StatisticsError
from collections import Counter
import Output.create_plots as plot

def write_output_instance(heuristic_run, feasible, tuning=None, similarity=None):
    """
    Function to return the output_files
    """
    instance_output = {}
    instance_output['run_time'] = heuristic_run.run_time
    instance_output['iterations'] = heuristic_run.n_iter
    instance_output['best_solution'] = heuristic_run.best_obj_values[-1]
    instance_output['violations_array'] = beautify_violation_array(heuristic_run)
    instance_output['feasible'] = feasible

    return instance_output


def collect_total_output(output):
    total_output = {}
    # print(output)
    total_output['avg_feasible_perc'] = mean([instance["stage_1"]['feasible'] for instance in output.values()]) * 100
    try:
        total_output['avg_run_time'] = mean(
            [instance['stage_2']['run_time'] for instance in output.values() if instance["stage_1"]['feasible']])
        total_output['avg_iterations'] = mean(
            [instance['stage_2']['iterations'] for instance in output.values() if instance["stage_1"]['feasible']])
        total_output['avg_obj_value'] = mean(
            [instance['stage_2']['best_solution'] for instance in output.values() if instance["stage_1"]['feasible']])
        # total_output['avg_violations'] = mean_violation_array(list(output_files.values())[0]['violations_array'], output_files)
    except StatisticsError:
        total_output['avg_run_time'], total_output['avg_iterations'], total_output['avg_obj_value'] = None, None, None
    return total_output


def create_json(output_folder, output):
    with open("C:/Master_thesis/Code/Metaheuristic/output_files/" + output_folder + "/output_files.json",
              "w") as output_obj:
        json.dump(output, output_obj)


def create_date_time_for_folder():
    now = datetime.now()
    return now.strftime("%d_%m_%Y__%H_%M_%S")


def create_output_folder(path="C:/Master_thesis/Code/Metaheuristic/output_files", folder_name="datetime"):
    if folder_name == "datetime":
        folder_name = create_date_time_for_folder()

    os.mkdir(path + "/" + folder_name)

    # create plots folder
    os.mkdir(path + "/" + folder_name + "/obj_plots")
    os.mkdir(path + "/" + folder_name + "/weight_plots")
    os.mkdir(path + "/" + folder_name + "/temp_plots")

    return folder_name


def prepare_output_all_instances(results, master_output, master_folder, folders_list, metrics, i, date_folder, output_folder):
    # create output dict
    output = {results[j]['folder_name']: results[j] for j in range(len(folders_list))}
    # create plots
    # plot.all_plots(output, date_folder + "/" + output_folder)
    # keys_to_keep = {"iterations", "run_time", "best_solution", "violation_array",
    #                 "feasible", 'best_solution_similarity', 'best_solution_no_similarity'}
    #
    # # remove unnecessary information
    # for result in results:
    #     result["stage_1"] = {k: v for k, v in result["stage_1"].items() if k in keys_to_keep}
    #     if "stage_2" in result:
    #         result["stage_2"] = {k: v for k, v in result["stage_2"].items() if k in keys_to_keep}

    output['totals'] = collect_total_output(output)

    # save json in output_files folder
    with open(master_folder + "/" + str(i) + "/output.json",
              "w") as output_obj:
        json.dump(output, output_obj)

    # update master output
    master_output = update_dict_per_instance_metric(master_output, output, metrics)
    master_output = add_feasibility_master(master_output, output)
    master_output = add_violations_similarity_master(master_output, output)

    return master_output


def beautify_violation_array(heuristic_run):
    violation_dict = {}
    for i, rule_name in enumerate(heuristic_run.rule_collection.soft_rule_collection.collection.keys()):
        violation_dict[rule_name] = heuristic_run.final_violation_array[i]

    return violation_dict


def mean_violation_array(violation_array, output):
    violation_dict = {}

    violation_sums = {key: sum([instance_output['violations_array'][key] for instance_output
                                in output.values()]) for key in violation_array.keys()}
    violations_sums = {k: value / len(output) for k, value in violation_sums.items()}
    return violations_sums


def collect_output_multiple_runs():
    pass
    # calc average per instance
    # get best run


def update_dict_per_instance_metric(master_output, output, metrics):
    for metric in metrics:
        for k in master_output.keys():
            if output[k]['stage_1']['feasible']:
                master_output[k][metric].append(output[k]['stage_2'][metric])
    return master_output


def add_feasibility_master(master_output, output):
    for k in master_output.keys():
        if output[k]['stage_1']['feasible']:
            if "feasible" in master_output[k]:
                master_output[k]['feasible'] += 1
            else:
                master_output[k]['feasible'] = 1
    return master_output


def add_violations_similarity_master(master_output, output):
    """
    Functions to store the violations of the similarity constraints in one place
    """
    for k, v in master_output.items():
        if output[k]['stage_1']['feasible']:
            if "violations" in v:
                for rule_k, violation in output[k]['stage_2']["violation_array"].items():
                    master_output[k]['violations'][rule_k].append(violation)
            else:
                master_output[k]['violations'] = {}
                for rule_k, violation in output[k]['stage_2']['violation_array'].items():
                    master_output[k]['violations'][rule_k] = [violation]

    return master_output


def calc_min(master_output, metrics, frequency):
    for metric in metrics:
        for k, v in master_output.items():
            master_output[k]["avg_" + metric] = mean(v[metric]) if len(v[metric]) > 0 \
                else None

            master_output[k]["best_" + metric] = min(v[metric]) if len(v[metric]) > 0 \
                else None
    for k, v in master_output.items():
        if "feasible" in v:
            master_output[k]["perc_feasible"] = master_output[k]['feasible'] / frequency * 100
        else:
            master_output[k]["perc_feasible"] = 0

    # calc average of violations
    for k, v in master_output.items():
        # check if any of the instances was feasible
        if v['perc_feasible'] > 0:
            master_output[k]["avg_violations"] = {}
            for rule_k in v["violations"]:
                master_output[k]["avg_violations"][rule_k] = mean(v["violations"][rule_k])
    return master_output


def prepare_output_boxplot(paths, metric):
    list_of_data = []

    for path in paths:
        f = open(path)
        master_output = json.load(f)

        # check whether this runs with lists
        metric_all_instances = []

        # collect the metric for all instances in one list
        for k, v in master_output.items():
            if v['perc_feasible'] > 0:
                for number in v[metric]:
                    metric_all_instances.append(number)

        list_of_data.append(metric_all_instances)

    return list_of_data


def prepare_output_boxplot_tuning(path):
    list_of_data = []
    directories = os.listdir(path)
    for directory in [directories[2], directories[1], directories[0]]:
        f = open(path + "/" + directory + "/output_files.json")
        output = json.load(f)

        # check whether this runs with lists
        metric_all_instances = []

        # collect the metric for all instances in one list
        for k, v in output.items():
            if k != "totals":
                if v['stage_1']['feasible']:
                    metric_all_instances.append(v['stage_2']['best_solution'] * 0.9)

        list_of_data.append(metric_all_instances)

    return list_of_data


def combine_output_multiple_runs(paths, metrics):
    master_output = {}
    for path in paths:
        file_list = os.listdir(path)

        for file in file_list:
            # save json in output_files folder
            try:
                with open(path + "/" + file + "/output.json",
                          "r") as output_obj:
                    output = json.loads(output_obj.read())
            except FileNotFoundError:
                pass
            if not master_output:
                master_output = {k: {metric: [] for metric in metrics} for k in output.keys() if
                                 'folder_name' in output[k]}

            # update master output
            master_output = update_dict_per_instance_metric(master_output, output, metrics)
            master_output = add_feasibility_master(master_output, output)
            master_output = add_violations_similarity_master(master_output, output)

    master_output = calc_min(master_output, metrics, frequency=11)
    with open("C:/Master_thesis/Code/Metaheuristic/output_files/" + "summary.json",
              "w") as output_obj:
        json.dump(master_output, output_obj)
