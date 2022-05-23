from copy import deepcopy
import cProfile
from Domain.settings import Settings
from Domain.scenario import Scenario
from Invoke.Initial_solution.initial_solution import BuildSolution
from Check.check_function_feasibility import FeasibilityCheck
from Heuristic import Heuristic
from Input.input_NRC import Instance

settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/two_stage_005.json"
two_stage = True
def run_stage(instance, stage_settings, previous_solution=None):
    scenario = Scenario(stage_settings, instance)

    init_solution = BuildSolution(scenario, previous_solution)
    best_solution = Heuristic(scenario, stage_settings=stage_settings).run_heuristic(starting_solution=deepcopy(init_solution))

    return best_solution

def run_two_stage(settings_file_path):
    """
    Function to execute heuristic
    """
    settings = Settings(settings_file_path)
    instance = Instance(settings)

    # run stage_1
    stage_1_solution = run_stage(instance, settings.stage_1_settings)

    # run stage 2
    # cProfile.run("run_stage(instance, settings.stage_2_settings, previous_solution=stage_1_solution)")
    stage_2_solution = run_stage(instance, settings.stage_2_settings, previous_solution=stage_1_solution)
    print(stage_1_solution.violation_array)
    print(stage_1_solution.change_counters)
    print(stage_2_solution.obj_value)
    print(stage_2_solution.violation_array)
    print(stage_2_solution.change_counters)
    return stage_2_solution


def run_one_stage(settings_file_path, stage_number=2):
    settings = Settings(settings_file_path)
    instance = Instance(settings)
    if stage_number == 2:
        stage_2_solution = run_stage(instance, settings.stage_2_settings)
    else:
        stage_2_solution = run_stage(instance, settings.stage_1_settings)

    print(stage_2_solution.obj_value)
    print(stage_2_solution.violation_array)
    print(stage_2_solution.change_counters)

    return stage_2_solution


# settings = Settings(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/two_stage_005.json")
# instance = Instance(settings)
# scenario = Scenario(settings.stage_1_settings, instance)
# init_solution = BuildSolution(scenario)
# stage_1_solution = Heuristic(scenario).run_heuristic(starting_solution=deepcopy(init_solution))
if __name__ == '__main__':
    if two_stage:
        run_two_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/two_stage_005.json")
    else:
        run_one_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/two_stage_005.json")

#cProfile.run("Heuristic(scenario).run_heuristic(starting_solution=deepcopy(init_solution))", sort=1)


