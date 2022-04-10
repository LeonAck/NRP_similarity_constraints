import time
import random
import numpy as np
from Invoke.Operators import change_operator
from solution import Solution
from Check.check_function_feasibility import FeasibilityCheck


class Heuristic:
    """
    Class to create the heuristic
    """
    def __init__(self, scenario):
        self.scenario = scenario
        self.rule_collection = scenario.rule_collection

        # set initial temperature
        # heuristic settings
        self.max_time = 15
        self.initial_temp = 22
        self.cooling_rate = 0.99
        self.no_improve_max = 50

        # introduce objects necessary for algorithm
        self.operators = {"change": change_operator}

        # Weight parameters
        self.reaction_factor = 0.9
        self.score_event_1 = 33
        self.score_event_2 = 9
        self.score_event_3 = 13
        self.score_event_4 = 0
        self.operator_weights = self.calc_initial_weights()

        # updating functions
        self.updating_functions = {"change": Solution().update_solution_change}

        self.frequency_operator = {}

    def run_heuristic(self, starting_solution):
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
        current_solution = Solution(starting_solution)
        # take initial solution as best solution
        best_solution = Solution(starting_solution)
        FeasibilityCheck().check_objective_value(current_solution, self.scenario)
        FeasibilityCheck().check_violation_array(current_solution, self.scenario)
        # Initialize tracking
        # number of iterations
        # number of iterations without improvement
        # create objects for tracking use of operators
        # create objects for tracking performance of operators

        # Set the elapsed time equal to zero
        self.start_time = time.time()

        # Set the temperature for the first iteration
        self.temperature = self.initial_temp

        n_iter = 0
        no_improve_iter = 0
        while time.time() < self.start_time + self.max_time:

            # choose operator
            operator_name = self.roulette_wheel_selection(self.operators)
            self.update_frequency_operator(operator_name)

            change_info = self.operators[operator_name](current_solution, self.scenario)
            no_improve_iter += 1
            if change_info['cost_increment'] <= 0:
                # update solutions accordingly
                current_solution.update_solution_change(change_info)
                # check if best. Then current solution, becomes the best solution
                if current_solution.obj_value < best_solution.obj_value:
                    best_solution = Solution(current_solution)
                    print("new best_solution: {}".format(best_solution.obj_value))
                    no_improve_iter = 0

            else:
                # check if solution is accepted
                accepted = self.acceptance_simulated_annealing(change_info)
                if accepted:
                    # update solutions accordingly
                    current_solution.update_solution_change(change_info)

            if no_improve_iter > self.no_improve_max:
                current_solution = Solution(best_solution)
                no_improve_iter = 0

            # adjust weights
            # TODO operator weights
            #self.update_operator_weights(operator_name)

            self.update_temperature()
            #FeasibilityCheck().check_objective_value(current_solution, self.scenario)
            #FeasibilityCheck().check_violation_array(current_solution, self.scenario)

            print(n_iter)
            #print(current_solution.obj_value)

            n_iter += 1


        # best solution
        return best_solution

    def acceptance_simulated_annealing(self, change_info):
        """
        Accept new solution based on probability.
        New solution is always accepted if the objective value is better than
        the current solution.
        If new solution is not better than the current solution, the solution
        is accepted based on probability.
        :return:
        True if accepted
        False if not accepted
        """
        # new solution is accepted with probability based on objective value
        # of current and new solutino and the temperature

        if random.uniform(0, 1) < np.exp(np.longdouble(
                -change_info['cost_increment'] / self.temperature)):
                        return True
        else:
            return False

    def update_temperature(self):
        """
        Update the SA temperature based on the elapsed time
        """

        # self.temperature = self.initial_temp * (
        #         1 - ((time.time() - self.start_time) / self.max_time) + 1 / 50
        # )
        self.temperature *= self.cooling_rate

    def update_frequency_operator(self, operator_name):
        """
        Add 1 to the frequency of the operator used if the operator is chosen
        """

        try:
            # if operator was used before add 1 to its frequency
            self.frequency_operator[operator_name] += 1
        except KeyError:
            # if not, now it is used for the first time
            self.frequency_operator[operator_name] = 1

    def roulette_wheel_selection(self, operators):
        """
        Random select an operator based on the weights.
        The probability of being chosen for any operator is calculated by
        the weight of the given operator divided by the sum of the weights of
        all of the operators.
        Insert self.used_destroy_ops to select a destroy operator
        Insert self.used_insert_ops to select an insertion operator
        :return:
        Name of selected operator
        """

        # Obtain the total sum of the weights
        total_weights = sum([
            value for key, value in self.operator_weights.items()
            if key in operators.keys()])

        # Pick a random number
        pick = random.uniform(0, total_weights)

        current = 0
        for name in operators.keys():
            current += self.operator_weights[name]

            # Choose the name of operator
            if current > pick:
                return name

    def update_operator_weights(self, operator_name, accepted):
        """
        Calc the weights of both the insertion and destroy operator
        used in this iteration based on their score
        self.operator_score is defined in
        """

        # for each operator calculate the new weight based on the score in
        # this iteration
        self.operator_weights[operator_name] = self.reaction_factor \
                                          * self.operator_weights[operator_name] \
                                          + self.operator_score[operator_name] \
                                          * (1 - self.reaction_factor)

    def calc_operator_score(self, operator_name, accepted):
        """
        Give a score to the operator based on performance in previous iteration.
        -----
        We identify four events for which a score is assigned.
        1. New solution is better than global best solution
        2. New solution is accepted with cost lower than current solution
        3. New solution is accepted with cost higher than current solution
        4. New solution is rejected
        ------
        No return: self.operator_score keeps score of the destroy and insertion
        operator used in the past iteration.
        """

        operator_score = 0
        # Check for both insertion and destroy operator in what event the
        # performance in the iteration is categorized.

        # Event 1
        # Check if best
        #     self.operator_score[operator] = self.score_event_1
        # # Event 2
        # elif self.accepted \
        #         and cost_function(self.new_solution, self.p) < cost_function(
        #     self.current_solution, self.p):
        #     self.operator_score[operator] = self.score_event_2
        # # Event 3
        # elif self.accepted \
        #         and cost_function(self.new_solution, self.p) > cost_function(
        #     self.current_solution, self.p):
        #     self.operator_score[operator] = self.score_event_3
        # # Event 4
        # else:
        #     self.operator_score[operator] = self.score_event_4

    def calc_initial_weights(self):
        """
        Calculate the initial of the operators.
        The weights for destroy operators are:
            1/(number of destroy operators used)
        The weights for insertion operators are:
            1/(number of insertion operators used)
        """

        operator_weights = {}

        # Assign weights to each of the used destroy operators
        for operator_name in self.operators.keys():
            operator_weights[operator_name] = \
                1 / len(self.operators)

        return operator_weights
