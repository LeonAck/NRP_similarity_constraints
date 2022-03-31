import time

class Heuristic:
    """
    Class to create the heuristic
    """
    def __init__(self, scenario, init_solution):
        self.scenario = scenario
        self.init_solution = init_solution

        # set initial temperature
        # heuristic settings
        self.max_time = 10

    def run_heuristic(self):
        """
           Execute the ALNS algorithm.
           Repeat iteration until max_time is reached or no_impr_max iterations is
           reached.
           Except new solution if better or otherwise based on Simulated Annealing
           Choose destroy and repair operators based on past performance.
           Weights are updated in this function.
           :return:
           solution
           running information
        """

        # take initial solution as current solution

        # take initial solution as best solution

        # Initialize tracking
        # number of iterations
        # number of iterations without improvement
        # create objects for tracking use of operators
        # create objects for tracking performance of operators

        # Set the elapsed time equal to zero
        start_time = time.time()

        while time.time() < start_time + self.max_time:
            pass
            # choose operator
