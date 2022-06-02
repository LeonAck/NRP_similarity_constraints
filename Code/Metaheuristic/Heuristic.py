import time
import random
import numpy as np
from Invoke.Operators import change_operator, swap_operator, greedy_change, similarity_operator

from solution import Solution
from Check.check_function_feasibility import FeasibilityCheck
from Invoke.Constraints.Rules.RuleS2Min import RuleS2Min
from copy import deepcopy, copy
import marshal
from pprint import pprint
class Heuristic:
    """
    Class to create the heuristic
    """
    def __init__(self, scenario, stage_settings=None):
        self.scenario = scenario
        self.rule_collection = scenario.rule_collection
        self.stage_number = stage_settings['stage_number']

        heuristic_settings = stage_settings['heuristic_settings']
        # set initial temperature
        # heuristic settings
        self.max_time = heuristic_settings['max_time']
        self.max_iter = heuristic_settings['max_iter']
        self.initial_temp = heuristic_settings['initial_temp']
        self.final_temp = heuristic_settings['final_temp']
        self.cooling_rate = heuristic_settings['cooling_rate']
        self.no_improve_max = heuristic_settings['no_improve_max']
        self.cut_off_ratio = heuristic_settings['cut_off_ratio']

        # introduce objects necessary for algorithm
        self.operator_collection = {"change": change_operator, "swap": swap_operator,
                                    "greedy_change": greedy_change,
                                    "similarity": similarity_operator}

        self.operators_to_use = heuristic_settings['operators']

        # Weight parameters
        self.reaction_factor = heuristic_settings['reaction_factor']
        self.score_event_1 = heuristic_settings['score_event_1']
        self.score_event_2 = heuristic_settings['score_event_2']
        self.score_event_3 = heuristic_settings['score_event_3']
        self.score_event_4 = heuristic_settings['score_event_4']
        self.operator_weights = self.calc_initial_weights()

        # updating functions
        self.updating_functions = {"change": Solution().update_solution_change}

        self.frequency_operator_improvement = self.create_object_improvement()

        # Create objects to save information for plots
        self.obj_values = []
        self.best_obj_values = []
        self.oper_vars = self.create_oper_vars()

        # calculate max_sampled and max accepted
        self.max_sampled = self.max_iter/(np.log(self.final_temp/self.initial_temp)/np.log(self.cooling_rate))
        self.max_accepted = self.max_sampled * self.cut_off_ratio

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
        current_solution = Solution(deepcopy(starting_solution))
        # take initial solution as best solution
        best_solution = Solution(starting_solution)

        # Set the elapsed time equal to zero
        self.start_time = time.time()

        # Set the temperature for the first iteration
        self.temperature = self.initial_temp
        change_counters = {"off_work": 0,
                           "work_off": 0,
                           "work_work": 0}

        n_iter = 1
        no_improve_iter = 0
        while self.temperature >= self.final_temp:
            n_sampled = 0
            n_accepted = 0
            while n_sampled < self.max_sampled and n_accepted < self.max_accepted:
                # print("\nIteration: ", n_iter)
                # if n_iter % 100 == 0:
                #     # print(current_solution.violation_array)
                #     print("\nIteration: ", n_iter)
                # print(current_solution.violation_array)

                # choose operator
                operator_name = self.roulette_wheel_selection(self.operators_to_use)
                # self.update_frequency_operator(operator_name)

                operator_info = self.operator_collection[operator_name](current_solution, self.scenario)

                if not operator_info['feasible']:
                    print("no feasible change")
                    break
                # print("current: {}, new: {}".format(change_info['current_working'], change_info['new_working']))

                if operator_name == "change":
                    change_counters = self.update_change_counter(change_counters, operator_info)
                no_improve_iter += 1
                if operator_info['cost_increment'] <= 0:
                    # update solutions accordingly
                    current_solution.update_solution_operator(operator_name, operator_info)
                    n_accepted += 1
                    # check if best. Then current solution, becomes the best solution
                    if current_solution.obj_value < best_solution.obj_value:
                        best_solution = Solution(deepcopy(current_solution))
                        print("new best_solution: {}".format(best_solution.obj_value))
                        no_improve_iter = 0

                else:
                    # check if solution is accepted
                    accepted = self.acceptance_simulated_annealing(operator_info)
                    if accepted:
                        # update solutions accordingly
                        current_solution.update_solution_operator(operator_name, operator_info)

                        n_accepted += 1
                # # print("current: {}".format(current_solution.obj_value))
                if no_improve_iter > self.no_improve_max:
                    # print("no improvement")
                    current_solution = Solution(deepcopy(best_solution))
                    no_improve_iter = 0
                n_sampled += 1

                # FeasibilityCheck().check_objective_value(current_solution, self.scenario, change_info)
                # if "S2Max" in current_solution.rules:
                #     FeasibilityCheck().work_stretches_info_employee(current_solution, self.scenario, operator_info, operator_name)
                # if "S3Max" in current_solution.rules:
                #     FeasibilityCheck().day_off_stretches_info(current_solution, self.scenario, operator_info)
                # if "S2ShiftMax" in current_solution.rules:
                #     FeasibilityCheck().shift_stretches_info(current_solution, self.scenario, operator_info, operator_name)
                # # FeasibilityCheck().check_number_of_assignments_per_nurse(current_solution, self.scenario, operator_info)
                # FeasibilityCheck().check_working_weekends(current_solution, self.scenario)
                # FeasibilityCheck().check_violation_array(current_solution, self.scenario, operator_info, operator_name)
                # FeasibilityCheck().h2_check_function(current_solution, self.scenario)
                # FeasibilityCheck().check_violation_array(current_solution, self.scenario, operator_info, operator_name)
                # FeasibilityCheck().h2_check_function(current_solution, self.scenario)

                # adjust weight
                self.update_operator_weights(operator_name, operator_info)

                previous_operator_info = operator_info
                n_iter += 1

                self.gather_plot_information(current_solution, best_solution)

            self.update_temperature()

        # best solution
        best_solution.change_counters = change_counters
        self.run_time = time.time() - self.start_time
        self.n_iter = n_iter
        self.final_violation_array = best_solution.violation_array
        return best_solution

    def update_change_counter(self, change_counters, change_info):
        if change_info["current_working"] and change_info['new_working']:
            change_counters["work_work"] += 1
        elif change_info['current_working']:
            change_counters["work_off"] += 1
        else:
            change_counters["off_work"] += 1
        return change_counters

    def stopping_criterion(self, current_solution, n_iter):
        if self.stage_number == 1:
            return self.temperature >= self.final_temp and not np.array_equal(current_solution.violation_array, np.zeros(2))
        #     return time.time() < self.start_time + self.max_time and n_iter < self.max_iter \
        #             and not np.array_equal(current_solution.violation_array, np.zeros(2))
        # else:
        #     return time.time() < self.start_time + self.max_time and n_iter < self.max_iter
        else:
            return self.temperature >= self.final_temp



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

    def update_frequency_operator_improvement(self, operator_name, operator_info):
        if operator_info['cost_increment'] < 0:
            self.frequency_operator_improvement[operator_name] += 1
            self.frequency_operator_improvement['total'] += 1


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
            if key in operators])

        # Pick a random number
        pick = random.uniform(0, total_weights)

        current = 0
        for name in operators:
            current += self.operator_weights[name]

            # Choose the name of operator
            if current > pick:
                return name

    def create_object_improvement(self):
        # create an empty list for every operator
        oper_vars = {}
        for key in self.operators_to_use:
            # create a list for every key with initial weight as first item
            oper_vars[key] = 0

        oper_vars['total'] = 0
        return oper_vars

    def update_operator_weights(self, operator_name, operator_info):
        """
        Calc the weights of both the insertion and destroy operator
        used in this iteration based on their score
        self.operator_score is defined in
        """

        self.update_frequency_operator_improvement(operator_name, operator_info)
        if operator_info['cost_increment'] < 0:
            for operator in self.operators_to_use:
                self.operator_weights[operator] = \
                    np.maximum(self.frequency_operator_improvement[operator] / self.frequency_operator_improvement['total'], 1/len(self.operators_to_use))


    def create_oper_vars(self):
        # create an empty list for every operator
        oper_vars = {}
        for key in self.operators_to_use:
            # create a list for every key with initial weight as first item
            oper_vars[key] = [self.operator_weights[key]]

        return oper_vars

    def update_operator_score(self, operator_info, accepted):
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
        for operator_name in self.operators_to_use:
            operator_weights[operator_name] = \
                1 / len(self.operators_to_use)

        return operator_weights

    def gather_plot_information(self, current_solution, best_solution):
        """
        Function to gather information for objective value plot
        and operator weights plot after every iteration
        """

        # information for objective plot
        self.obj_values.append(current_solution.obj_value)
        self.best_obj_values.append(best_solution.obj_value)

        # gather operator weights information
        # Operator plot. For every iteration, append weights
        for key, value in self.operator_weights.items():
            self.oper_vars[key].append(value)

