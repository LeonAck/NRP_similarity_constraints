from run import run_one_stage

settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json"
from Invoke.Operators.swap_operator import check_one_way_swap, get_feasible_swap
from copy import deepcopy
import cProfile
from Domain.settings import Settings
from Domain.scenario import Scenario
from Invoke.Initial_solution.initial_solution import BuildSolution
from Check.check_function_feasibility import FeasibilityCheck
from Heuristic import Heuristic
from Input.input_NRC import Instance
from run import run_two_stage, run_stage
import marshal, pickle
import create_plots as plot
# cProfile.run("run_two_stage(settings_file_path)", sort=1)
# path = "C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions/030-4-1-6-2-9-1/sol-0.out"
# # stage_two_solution = run_two_stage(settings_file_path)
# with open("C:/Master_thesis/Code/Metaheuristic/Input/ref_assignments_12.txt", "wb") as ref_shift_assignments_file:
#     pickle.dump(stage_two_solution.shift_assignments, ref_shift_assignments_file)
# sol = run_one_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json")
settings = Settings(settings_file_path)
instance = Instance(settings)
scenario = Scenario(settings.stage_2_settings, instance)
init_solution = BuildSolution(scenario, previous_solution=None)

heuristic = Heuristic(scenario, stage_settings=settings.stage_2_settings)
best_solution = heuristic.run_heuristic(
    starting_solution=deepcopy(init_solution))

plot.objective_value_plot(heuristic)