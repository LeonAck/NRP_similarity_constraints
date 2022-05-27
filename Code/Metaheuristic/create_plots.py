import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def objective_value_plot(Heuristic, suppress=False):
    """
    Function to create the objective value plot
    """
    # instance = instance.removesuffix(".txt")
    # to_remove = dirname + "\\"
    # instance = instance.removeprefix(to_remove)

    x_axis = np.linspace(0, Heuristic.max_time, Heuristic.n_iter)[0:-1]
    plt.plot(x_axis, Heuristic.obj_values, x_axis, Heuristic.best_obj_values, linewidth=0.5)
    plt.ylim(0, 15000)
    if suppress:
        plt.savefig('output 2/plots/obj_{}.png'.format("bla"))
        plt.close()
    else:
        plt.show()

def operator_weight_plot(heuristic, suppress=False):
    """
    Function to create operator weights plot
    """
    # instance = instance.removesuffix(".txt")
    # to_remove = dirname + "\\"
    # instance = instance.removeprefix(to_remove)

    oper_df = pd.DataFrame.from_dict(heuristic.oper_vars)
    operator_data_perc = oper_df.divide(oper_df.sum(axis=1), axis=0)

    # Operator weight plot
    operator_data_perc.plot.area(title='100 % stacked area chart for operator weights')
    plt.legend(loc='best')

    if suppress:
        plt.savefig('output 2/plots/oper_weight_{}.png'.format("bla"))
        plt.close()
    else:
        plt.show()