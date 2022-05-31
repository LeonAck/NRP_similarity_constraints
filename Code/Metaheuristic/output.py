from datetime import datetime
import os
import numpy as np
import json
from statistics import mean
os.chdir("C:/Master_thesis/Code/Metaheuristic/output")

def write_output_instance(heuristic_run, feasible, tuning=None, similarity=None):
    """
    Function to return the output
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
    total_output['avg_run_time'] = mean([instance['run_time'] for instance in output.values()])
    total_output['avg_iterations'] = mean([instance['iterations'] for instance in output.values()])
    total_output['avg_obj_value'] = mean([instance['best_solution'] for instance in output.values()])
    total_output['avg_violations'] = list(np.mean(np.array([instance['violations_array'] for instance in output.values()]), axis=0))

    return total_output


def create_json(output_folder, output):
    with open("C:/Master_thesis/Code/Metaheuristic/output/" + output_folder+"/output.json", "w") as output_obj:
        json.dump(output, output_obj)

def format_violation_array(soft_rule_collection, violation_array):
    pass

def create_date_time_for_folder():
    now = datetime.now()
    return now.strftime("%d_%m_%Y__%H_%M_%S")

def create_output_folder():
    folder_name = create_date_time_for_folder()
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output"+"/"+folder_name)

    # create plots folder
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output"+"/"+folder_name+"/obj_plots")
    os.mkdir("C:/Master_thesis/Code/Metaheuristic/output" + "/" + folder_name + "/weight_plots")
    return folder_name

def beautify_violation_array(heuristic_run):
    violation_dict = {}
    for i, rule_name in enumerate(heuristic_run.rule_collection.soft_rule_collection.collection.keys()):
        violation_dict[rule_name] = heuristic_run.violation_array[i]

    return violation_dict

