import numpy as np


def create_output_dict(folder_name, instance_name, heuristic_1, heuristic_2=None, tuning=False, similarity=False):
    output_dict = {"folder_name": folder_name, "instance_name": instance_name}

    output_dict["stage_1"] = {"iterations": heuristic_1.n_iter,
                              "run_time": heuristic_1.run_time,
                              "feasible": heuristic_1.stage_1_feasible,
                              "violation_array": beautify_violation_array(heuristic_1),
                              # "temperatures": heuristic_1.temperatures,
                              # "obj_values": heuristic_1.obj_values,
                              # "best_obj_values": heuristic_1.best_obj_values
                              }

    if heuristic_1.stage_1_feasible:
        output_dict["stage_2"] = {"iterations": heuristic_2.n_iter,
                                  "run_time": heuristic_2.run_time,
                                  "violation_array": beautify_violation_array(heuristic_2),
                                  "best_solution": heuristic_2.best_obj_values[-1],
                                  # "temperatures": heuristic_2.temperatures,
                                  "obj_values": heuristic_2.obj_values,
                                  # "best_obj_values": heuristic_2.best_obj_values,
                                  # "operator_weights": heuristic_2.oper_vars
                                  }
        if not tuning:
            if similarity:
                output_dict['stage_2']['best_solution_similarity'] = heuristic_2.best_obj_values[-1]
                output_dict['stage_2']['best_solution_no_similarity'] = calc_objective_value_violations(
                    heuristic_2.final_violation_array[:-3], heuristic_2.rule_collection.penalty_array[:-3])
            else:
                output_dict['stage_2']['best_solution_similarity'] = calc_objective_value_violations(
                    heuristic_2.final_violation_array, heuristic_2.rule_collection.penalty_array)
                output_dict['stage_2']['best_solution_no_similarity'] = heuristic_2.best_obj_values[-1]
    return output_dict


def beautify_violation_array(heuristic_run):
    violation_dict = {}
    for i, rule_name in enumerate(heuristic_run.rule_collection.soft_rule_collection.collection.keys()):
        violation_dict[rule_name] = heuristic_run.final_violation_array[i]

    return violation_dict


def calc_objective_value_violations(violation_array, penalty_array):
    """
    Function to calculate the objective value of a solution based on the
    applied soft constraints
    """
    return np.matmul(violation_array, penalty_array)
