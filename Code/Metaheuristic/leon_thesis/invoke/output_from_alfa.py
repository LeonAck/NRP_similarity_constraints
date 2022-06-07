def create_output_dict(instance_name, heuristic_1, heuristic_2=None):
    output_dict = {"instance_name": instance_name,
                  "stage_1": {},
                   "stage_2": {}
    }

    output_dict["stage_1"] = {"iterations": heuristic_1.n_iter,
                              "run_time": heuristic_1.run_time,
                              "feasible": heuristic_1.stage_1_feasible,
                              "violation_array": heuristic_1.final_violation_array}

    if heuristic_1.stage_1_feasible:
        output_dict["stage_2"] = {"iterations": heuristic_2.n_iter,
                                  "run_time": heuristic_2.run_time,
                                  'best_solution': heuristic_2.best_obj_values[-1],
                                  "violation_array": heuristic_2.final_violation_array,
                                  "temperatures": heuristic_2.temperatures,
                                  "obj_values": heuristic_2.obj_values,
                                  "best_obj_values": heuristic_2.best_obj_values,
                                  "operator_weights": heuristic_2.oper_vars}

    return output_dict