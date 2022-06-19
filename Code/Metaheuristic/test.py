from run import run_one_stage, run_multiple_files
from tuning import run_parameter_tuning_random
import cProfile
from tuning import run_parameter_tuning_random, tuning_single_run_create_plot
from Output.output import prepare_output_boxplot
from Output.create_plots import create_box_plot


# similarity = False
# tuning = True
# if similarity:
#     settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/similarity_settings.json"
# elif tuning:
#     settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/tuning_settings.json"
# else:
#     settings_file_path = "C:/Master_thesis/Code/Metaheuristic/Input/setting_files/no_similarity.json"

# run_one_stage(settings_file_path, stage_number=2)
# cProfile.run("run_multiple_files('C:/Master_thesis/Code
# /Metaheuristic/Input/sceschia-nurserostering/StaticSolutions', settings_file_path=settings_file_path, similarity=similarity)", sort=1)
# run_parameter_tuning_random(number_of_instances=2)
run_multiple_files(frequency=2, max_workers=25, similarity=False, reg_run=False)
# tuning_single_run_create_plot(repeat=2, params=(13, 16, 19), param_to_change="initial_temp")
