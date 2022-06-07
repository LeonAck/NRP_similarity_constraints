import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def objective_value_plot(n_iter, obj_values, best_obj_values, stage_number, instance_name, suppress=True, output_folder=None):
    """
    Function to create the objective value plot
    """

    if suppress:
        x_axis = np.linspace(0, n_iter, n_iter)[0:-1]
        plt.plot(x_axis, obj_values, x_axis, best_obj_values, linewidth=0.5)
        if stage_number == 2:
            plt.ylim(0, 20000)
        else:
            plt.ylim(0, 1000)

        if output_folder:
            plt.savefig('C:/Master_thesis/Code/Metaheuristic/output_files/' + output_folder + '/obj_plots/obj_{}.png'.format(instance_name))
        plt.close()

def operator_weight_plot(oper_weights, instance_name, output_folder, suppress=True):
    """
    Function to create operator weights plot
    """


    oper_df = pd.DataFrame.from_dict(oper_weights)
    operator_data_perc = oper_df.divide(oper_df.sum(axis=1), axis=0)
    if suppress:
        # Operator weight plot
        operator_data_perc.plot.area(title='100 % stacked area chart for operator weights')
        plt.legend(loc='best')

        if output_folder:
            plt.savefig('C:/Master_thesis/Code/Metaheuristic/output_files/' + output_folder + '/weight_plots/weight_{}.png'.format(instance_name))
        plt.close()

def temperature_plot(n_iter, temperatures, initial_temp, instance_name, output_folder, suppress=True):
    """Function to see temperature over the run time"""
    if suppress:
        x_axis = np.linspace(0, initial_temp, n_iter)[0:-1]
        plt.plot(x_axis, temperatures, linewidth=0.5)

        if output_folder:
            plt.savefig('C:/Master_thesis/Code/Metaheuristic/output_files/' + output_folder + '/temp_plots/temp_{}.png'.format(
                instance_name))
        plt.close()

def all_plots(output_dict, output_folder, input_dict):
    for folder_name, output_info in output_dict.items():
        if output_info['stage_1']['feasible']:
            objective_value_plot(output_info['stage_2']['iterations'], output_info['stage_2']["obj_values"],
                                 output_info['stage_2']["best_obj_values"], 2, folder_name, suppress=True, output_folder=output_folder)
            operator_weight_plot(output_info['stage_2']["obj_values"], folder_name, suppress=True, output_folder=output_folder)
            temperature_plot(output_info['stage_2']['iterations'], output_info['stage_2']['temperatures'],
                             input_dict['stage_2_settings']['initial_temp'], folder_name, suppress=True, output_folder=output_folder)

