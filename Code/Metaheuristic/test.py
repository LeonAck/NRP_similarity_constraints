from run import run_one_stage
settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json"
from Invoke.Operators.swap_operator import check_one_way_swap, get_feasible_swap
from copy import deepcopy
import cProfile
from Domain.settings import Settings
from Domain.scenario import Scenario
from Invoke.Initial_solution.initial_solution import BuildSolution
from Check.check_function_feasibility import FeasibilityCheck
from Heuristic import Heuristic
from Input.input_NRC import Instance
from Invoke.Constraints.Rules.RuleH3 import RuleH3
from run import run_two_stage

k = 7
run_two_stage(settings_file_path)
# sol = run_one_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json")
settings = Settings(settings_file_path)
instance = Instance(settings)
scenario = Scenario(settings.stage_2_settings, instance)
init_solution = BuildSolution(scenario, previous_solution=None)
best_solution = Heuristic(scenario, stage_settings=settings.stage_2_settings).run_heuristic(starting_solution=deepcopy(init_solution))
