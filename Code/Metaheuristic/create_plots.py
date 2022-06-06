import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def objective_value_plot(heuristic, instance_name, suppress=True, output_folder=None):
    """
    Function to create the objective value plot
    """

    if suppress:
        x_axis = np.linspace(0, heuristic.max_time, heuristic.n_iter)[0:-1]
        plt.plot(x_axis, heuristic.obj_values, x_axis, heuristic.best_obj_values, linewidth=0.5)
        if heuristic.stage_number == 2:
            plt.ylim(0, 20000)
        else:
            plt.ylim(0, 1000)

        if output_folder:
            plt.savefig('C:/Master_thesis/Code/Metaheuristic/output/' + output_folder + '/obj_plots/obj_{}.png'.format(instance_name))
        plt.close()

def operator_weight_plot(heuristic, instance_name, output_folder, suppress=True):
    """
    Function to create operator weights plot
    """


    oper_df = pd.DataFrame.from_dict(heuristic.oper_vars)
    operator_data_perc = oper_df.divide(oper_df.sum(axis=1), axis=0)
    if suppress:
        # Operator weight plot
        operator_data_perc.plot.area(title='100 % stacked area chart for operator weights')
        plt.legend(loc='best')

        if output_folder:
            plt.savefig('C:/Master_thesis/Code/Metaheuristic/output/' + output_folder + '/weight_plots/weight_{}.png'.format(instance_name))
        plt.close()

def temperature_plot(heuristic, instance_name, output_folder, suppress=True):
    """Function to see temperature over the run time"""
    if suppress:

        plt.plot(range(0, heuristic.initial_temp), heuristic.temperatures, linewidth=0.5)

        if output_folder:
            plt.savefig('C:/Master_thesis/Code/Metaheuristic/output/' + output_folder + 'temp_plots/obj_{}.png'.format(
                instance_name))
        plt.close()

