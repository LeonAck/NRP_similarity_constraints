import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def objective_value_plot(n_iter, obj_values, best_obj_values, stage_number, instance_name, suppress=True,
                         output_folder=None, run_time=None):
    """
    Function to create the objective value plot
    """

    if suppress:
        if run_time:
            x_axis = np.linspace(0, 550, n_iter)[0:-1]
            # plt.plot(x_axis, obj_values, x_axis, best_obj_values, linewidth=0.5)
            plt.plot(x_axis, obj_values, linewidth=0.5)
            plt.ylabel('Cost')
            plt.xlabel('Run time')
            plt.legend(['Current solution', 'Best solution'], loc='upper right')
        else:
            x_axis = np.linspace(0, n_iter, n_iter)[0:-1]
            plt.plot(x_axis, obj_values, x_axis, best_obj_values, linewidth=0.5)
            plt.ylabel('Cost')
            plt.xlabel('Iterations')
        # if stage_number == 2:
        #     plt.ylim(0, min(obj_values) + 10000)

        if output_folder:
            plt.savefig(
                'C:/Master_thesis/Code/Metaheuristic/output_files/' + output_folder + '/obj_plots/obj_{}.png'.format(
                    instance_name))
        plt.close()


def operator_weight_plot(oper_weights, instance_name, output_folder, suppress=True):
    """
    Function to create operator weights plot
    """

    oper_df = pd.DataFrame.from_dict(oper_weights)
    operator_data_perc = oper_df.divide(oper_df.sum(axis=1), axis=0)
    if suppress:
        # Operator weight plot
        operator_data_perc.plot.area(colormap='coolwarm')
        better_names = {"change": "Change", "swap": "MultiSwap", "greedy_change": "GreedyChange", "similarity": "SimilarityChange"}
        plt.legend([better_names[k] for k in oper_weights.keys()], loc='best')

        if output_folder:
            plt.savefig(
                'C:/Master_thesis/Code/Metaheuristic/output_files/' + output_folder + '/weight_plots/weight_{}.png'.format(
                    instance_name))
        plt.close()


def temperature_plot(n_iter, temperatures, instance_name, output_folder, suppress=True):
    """Function to see temperature over the run time"""
    if suppress:
        x_axis = np.linspace(0, temperatures[0], n_iter)[0:-1]
        plt.plot(x_axis, temperatures, linewidth=0.5)

        if output_folder:
            plt.savefig(
                'C:/Master_thesis/Code/Metaheuristic/output_files/' + output_folder + '/temp_plots/temp_{}.png'.format(
                    instance_name))
        plt.close()


def all_plots(output_dict, output_folder, stage_2=True):
    for folder_name, output_info in output_dict.items():
        if not stage_2:
            objective_value_plot(output_info['stage_1']['iterations'], output_info['stage_1']["obj_values"],
                                 output_info['stage_1']["best_obj_values"], 1, folder_name, suppress=True,
                                 output_folder=output_folder)
            temperature_plot(output_info['stage_1']['iterations'], output_info['stage_1']['temperatures'], folder_name,
                             suppress=True,
                             output_folder=output_folder)
        elif output_info['stage_1']['feasible']:
            # objective_value_plot(output_info['stage_2']['iterations'], output_info['stage_2']["obj_values"],
            #                      output_info['stage_2']["best_obj_values"], 2, folder_name, suppress=True,
            #                      output_folder=output_folder, run_time=output_info['stage_2']['run_time'])
            operator_weight_plot(output_info['stage_2']["operator_weights"], folder_name, suppress=True,
                                 output_folder=output_folder)
            # temperature_plot(output_info['stage_2']['iterations'], output_info['stage_2']['temperatures'], folder_name,
            #                  suppress=True,
            #                  output_folder=output_folder)


def create_box_plot(list_of_data, output_folder=True, file_name="sample",
                    tick_names=["Change", "Change + Swap + Greedy", "Change + Swap"],
                    ylabel='Cost'):
    num_ticks = len(list_of_data)
    plt.figure(figsize=(10, 7))

    plt.boxplot(list_of_data)
    plt.ylabel(ylabel)
    plt.xticks(list(range(1, num_ticks + 1)), tick_names)
    # plt.show()
    if output_folder:
        plt.savefig(
            'C:/Master_thesis/Code/Metaheuristic/output_files/box_plot_{}.png'.format(
                file_name))

    plt.close()


def get_obj_value_multiple_params():
    pass


def create_obj_value_multiple_params(param_dict, instance_name, suppress=False):
    for param, info in param_dict.items():
        x_axis = np.linspace(0, info['run_time'], info['iterations'])[0:-1]
        plt.plot(x_axis, info['obj_values'],  linewidth=0.5)

    plt.legend([r'$N_i = {}$'.format(param) for param in param_dict.keys()])
    if not suppress:
        plt.show()
    else:
        plt.savefig(
            'C:/Master_thesis/Code/Metaheuristic/output_files/tuning/multiple_param_{}.png'.format(
                instance_name))
        plt.close()




