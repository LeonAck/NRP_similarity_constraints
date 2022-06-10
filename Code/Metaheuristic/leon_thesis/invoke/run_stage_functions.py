from Domain.scenario import Scenario
from Solutions.initial_solution import BuildSolution
from Solutions.end_solution import EndSolution
from Heuristic import Heuristic
from copy import deepcopy

def run_stage(instance, stage_settings, previous_solution=None):
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