from run import run_one_stage, run_multiple_files
from tuning import run_parameter_tuning_random
settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"
import cProfile

from tuning import run_parameter_tuning_random

similarity = False
tuning = True
if similarity:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json"
elif tuning:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"
else:
    settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"

# run_one_stage(settings_file_path, stage_number=2)
# cProfile.run("run_multiple_files('C:/Master_thesis/Code
# /Metaheuristic/Input/sceschia-nurserostering/StaticSolutions', settings_file_path=settings_file_path, similarity=similarity)", sort=1)
run_parameter_tuning_random(number_of_instances=2)
# run_multiple_files(frequency=10, max_workers=20, similarity=True)