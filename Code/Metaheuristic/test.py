from run import run_one_stage, run_multiple_files
from tuning import run_parameter_tuning_random
import cProfile
from tuning import run_parameter_tuning_random, tuning_single_run_create_plot
from Output.output import prepare_output_boxplot, combine_output_multiple_runs, prepare_output_boxplot_tuning
from Output.create_plots import create_box_plot
from leon_thesis.invoke.main import run
from scipy import stats as st
import statistics

# run_parameter_tuning_random(number_of_instances=2)
run_multiple_files(frequency=1, max_workers=50, similarity=False, reg_run=False)
# tuning_single_run_create_plot(repeat=2, max_workers=20, params=([150, 500, 2000]), param_to_change="no_improve_max")
# cProfile.run("run_multiple_files(frequency=2, max_workers=25, similarity=True, reg_run=True, num_weeks=8)", sort=1)

# combine_output_multiple_runs(paths=[
#     "C:/Master_thesis/Code/Metaheuristic/output_files/om_te_verwerken/20_06_2022_4_week_6_reg_run",
#     "C:/Master_thesis/Code/Metaheuristic/output_files/om_te_verwerken/21_06_2022_4_weeks_6_reg_run_1"
# ],
#     metrics=(["best_solution"]))

# data_list = prepare_output_boxplot_tuning(
#     path="C:/Master_thesis/Code/Metaheuristic/output_files/tuning/22_06_2022_vergelijken_operators")
# data_list = prepare_output_boxplot(paths=["C:/Master_thesis/Code/Metaheuristic/output_files/29_06_2022_4_week_change/summary.json",
#                                           "C:/Master_thesis/Code/Metaheuristic/output_files/29_06_2022_8_week_sum/summary.json",
#                                           "C:/Master_thesis/Code/Metaheuristic/output_files/29_06_2022_4_week_greedy/summary.json"],
#                                    metric="best_solution_no_similarity")
#
# print(statistics.variance(data_list[0]))
# print(statistics.variance(data_list[1]))
# print(statistics.variance(data_list[2]))
# print(st.ttest_ind(data_list[0], data_list[1], equal_var=True))
# print(st.ttest_ind(data_list[2], data_list[1], equal_var=True))
# create_box_plot(list_of_data=data_list, output_folder=True, file_name="operators_2",
#                     tick_names=["Change", "Change + Swap", "Change + Swap + GreedyChange"],
#                     ylabel='Cost')
#
# data_list = prepare_output_boxplot(paths=["C:/Master_thesis/Code/Metaheuristic/output_files/28_06_2022_w_similarity_new/summary.json",
#                                           "C:/Master_thesis/Code/Metaheuristic/output_files/29_06_2022_similarity_ops_2/summary.json"],
#                                    metric="best_solution_similarity")
# data_list[1].append(20000)
# print(statistics.variance(data_list[0]))
# print(statistics.variance(data_list[1]))
# print(st.ttest_ind(data_list[0], data_list[1], equal_var=True))
# create_box_plot(list_of_data=data_list, output_folder=True, file_name="operators_sim",
#                     tick_names=["Change + Swap", "Change + Swap + SimilarityChange"],
#                     ylabel='Cost')

# path = "C:/Master_thesis/Code/Metaheuristic/output_files/om_te_verwerken/22_06_2022_with_sim_operator"
# list_of_data = prepare_output_boxplot(paths=['C:/Master_thesis/Code/Metaheuristic/output_files/om_te_verwerken/19_06_2022_8_week_w_similarity_1/summary.json',
#                                              'C:/Master_thesis/Code/Metaheuristic/output_files/om_te_verwerken/22_06_2022_with_sim_operator/summary.json'], metric='avg_best_solution')
#
# create_box_plot(list_of_data=list_of_data, output_folder=True, file_name="sim_operator",
#                     tick_names=["Change + Swap", "Change + Swap + SimilarityChange"],
#                     ylabel='Cost')