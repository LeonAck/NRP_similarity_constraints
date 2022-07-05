settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json"
from leon_thesis.invoke.Operators import get_feasible_swap, stretches_in_range
from copy import deepcopy
from Domain.settings import Settings
from Domain.scenario import Scenario
from Invoke.Initial_solution.initial_solution import BuildSolution
from Input.input_NRC import Instance

k = 7
# sol = run_one_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json")
settings = Settings(settings_file_path)
instance = Instance(settings)
scenario = Scenario(settings.stage_2_settings, instance)
init_solution = BuildSolution(scenario, previous_solution=None)
# best_solution = Heuristic(scenario, stage_settings=settings.stage_2_settings).run_heuristic(starting_solution=deepcopy(init_solution))

swap_info = get_feasible_swap(init_solution, scenario, k)

day_range = range(swap_info['start_index'], swap_info['end_index']+1)
solution = init_solution
stretch_object = solution.work_stretches
object_name = "work_stretches"

swap_info = stretches_in_range(solution, swap_info, solution.work_stretches, "work_stretches")
stretch_object_copy = deepcopy(stretch_object)

# swap_info['work_stretches_new'] = RuleS2Max().collect_new_stretches(solution, solution.work_stretches,
#                                                                     swap_info)