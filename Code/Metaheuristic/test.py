from run import run_one_stage
from Input.load_instances import getListOfDirs
settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
import cProfile
from Invoke.Initial_solution.initial_solution import BuildSolution
from Input.input_NRC import Instance
import create_plots as plot
from tuning import run_parameter_tuning_random

similarity = False
tuning = True
if similarity:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json"
elif tuning:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"
else:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
# cProfile.run("run_two_stage(settings_file_path)", sort=1)
# path = "C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions/030-4-1-6-2-9-1/sol-0.out"
# # stage_two_solution = run_two_stage(settings_file_path)
# with open("C:/Master_thesis/Code/Metaheuristic/Input/ref_assignments_12.txt", "wb") as ref_shift_assignments_file:
#     pickle.dump(stage_two_solution.shift_assignments, ref_shift_assignments_file)
# sol = run_one_stage(settings_file_path="C:/Master_thesis/Code/Metaheuristic/Input/setting_files/test_swap.json")

# run_one_stage(settings_file_path, stage_number=2)
# cProfile.run("run_multiple_files('C:/Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering/StaticSolutions', settings_file_path=settings_file_path, similarity=similarity)", sort=1)
run_parameter_tuning_random(number_of_instances=15)