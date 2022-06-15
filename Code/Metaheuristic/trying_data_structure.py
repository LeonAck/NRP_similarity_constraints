from Output.create_plots import create_box_plot

import numpy as np

np.random.seed(10)
x = np.random.normal(8000, 1000, 1000)
z = np.random.normal(6000, 1000, 1000)
y = np.random.normal(4000, 1000, 1000)
list_of_data = [x[x > 2500], z[z > 2500], y[y > 2500]]


