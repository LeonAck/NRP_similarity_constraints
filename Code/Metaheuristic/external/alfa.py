from alfa_sdk.common.session import Session
from leon_thesis.invoke.Domain.scenario import Scenario
from leon_thesis.invoke.Solutions.initial_solution import BuildSolution
from leon_thesis.invoke.Solutions.end_solution import EndSolution
from leon_thesis.invoke.Heuristic import Heuristic
from copy import deepcopy
from leon_thesis.invoke.utils.session import init_session

def execute_heuristic(problem, algorithm_id="fde9e297-7579-4ac3-ab2a-078fb74e4040",
                      environment="thesis_env"):
    session = Session(keepalive=True)
    result = session.invoke_algorithm(
        algorithm_id,
        environment,
        problem
    )
    print("single run done")
    print(result)
    return result


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
