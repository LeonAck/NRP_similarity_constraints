from uuid import uuid4
from mip import Model, MINIMIZE, CBC, xsum, OptimizationStatus, LinExpr, INF, CONTINUOUS


class Solver:
    """
    Contains the variables, constraints, and objective; solves the problem that those
    elements form.
    """

    def __init__(self):
        self._solver = None
        self._objective = None
        self.max_value = 18446744073709551615
        self.reset()

        self._variables = {}
        self._slack_variables = {}

    #

    @property
    def infinity(self):
        """
        Returns the infinity value of the solver.
        """
        return self.max_value

    @property
    def objective_value(self):
        """
        Returns the objective value of the solver.
        """
        if not self._solver.objective_value:
            return 0
        return self._solver.objective_value


    def reset(self):
        """
        Reinitializes the solver object.
        """
        self._solver = Model(sense=MINIMIZE, solver_name=CBC)

        self._variables = {}

    def set_initial_solution(self, initial_solution):
        self._solver.start = initial_solution

    def clear(self):
        self._solver.clear()

    def solve(self,
            runtime,
            linear_relaxation,
            emphasis,
            mip_gap,
            preprocess,
            seed,
            logging):
        """
        Finds a solution defined for the solver.
        """

        print('# Variables: {}'.format(self._solver.num_cols))
        print('# Constraints: {}'.format(self._solver.num_rows))

        if self._solver.num_cols == 0:
            return None

        if emphasis:
            self._solver.emphasis = emphasis
        if mip_gap is not None:
            self._solver.max_mip_gap = mip_gap
            self._solver.max_mip_gap_abs = mip_gap

        self._solver.preprocess = preprocess
        self._solver.seed = seed
        self._solver.verbose = logging

        self._solver.store_search_progress_log = True

        result = self._solver.optimize(max_seconds=runtime, relax=linear_relaxation)

        if result == OptimizationStatus.INFEASIBLE:
            result = 0
        elif result == OptimizationStatus.OPTIMAL:
            result = 1
        elif result == OptimizationStatus.NO_SOLUTION_FOUND:
            result = 2
        elif result == OptimizationStatus.FEASIBLE:
            result = 3
        else:
            result = None

        if self._solver.objective_value:
            print('upper bound - lower bound: {} - {}'.format(round(self._solver.objective_value, 2),
                                                          round(self._solver.objective_bound, 2)))
        return result

    def result_is_valid(self, result):
        """
        Returns whether the result is valid and output for an iteration can be fetched.
        """
        return result is not None and result in [1, 3]

    def set_objective_coefficient(self, variable, coefficient):
        """
        Sets the coefficient of the variable in the objective.
        """
        variable.obj = coefficient

    def get_solution_value(self, variable):
        return variable.x

    def find_variable(self, id):
        """
        Looks up a varaible with the specified id and returns it.
        """
        return self._variables.get(id)

    def find_slack_variable_constraint(self, constraint_id):
        return self._variables.get(f"{constraint_id}_slack")

    def positive_slack_var(self, constraint_id):
        slack_var = self.find_slack_variable_constraint(constraint_id)
        if slack_var:
            return slack_var.x > 0
        return False

    def get_violation_costs_slack_var(self, constraint_id):
        slack_var = self.find_slack_variable_constraint(constraint_id)
        return slack_var.obj * slack_var.x

    def find_or_create_variable(self, id, lower_bound, upper_bound):
        """
        Checks whether a variable with the specified id exists. If that is the case, the
        found variable is returned. If that is not the case, it will create an integer
        variable with the specified id, lower_bound, and upper_bound. The created variable
        will then be returned.
        """
        existing_variable = self.find_variable(id)
        if existing_variable:
            return existing_variable
        return self.create_variable(id, lower_bound, upper_bound)

    def create_variable(self, id, lower_bound, upper_bound, obj=0, var_type='I'):
        """
        Creates an integer variable with the specified id, lower_bound, and upper_bound.
        Returns the created variable
        """
        variable = self._solver.add_var(lb=lower_bound, ub=upper_bound, obj=obj, name=id, var_type=var_type)
        self._variables[id] = variable
        return variable

    #
    def get_search_progress_log(self, progress_log_size):
        self._solver.search_progress_log.instance = "technical_kpi"

        progress_log = self._solver.search_progress_log.log
        if len(progress_log) > progress_log_size:
            progress_log = progress_log[-progress_log_size:]

        return progress_log

    def find_constraint(self, id):
        """
        Looks up a constraint with the specified id and returns it.
        """
        return self._solver.constr_by_name(id)

    def create_slacked_constraint(
        self,
        id,
        constraint_lhs=0,
        constraint_sense='==',
        constraint_rhs=0,
        slack_lower_bound=0,
        slack_upper_bound=0,
        slack_constraint_coeff=0,
        slack_objective_coeff=0,
    ):
        slack_variable = 0
        if slack_constraint_coeff != 0:
            slack_variable = self.create_variable(f"{id}_slack", lower_bound=slack_lower_bound, upper_bound=slack_upper_bound, obj=slack_objective_coeff)
            self._slack_variables[id] = slack_variable

        constraint = None
        if constraint_sense == '==':
            constraint = self._solver.add_constr(slack_constraint_coeff * slack_variable + xsum(
                coefficient * variable for coefficient, variable in
                constraint_lhs) == constraint_rhs, name=f"{id}_constraint")
        elif constraint_sense == '<=':
            constraint = self._solver.add_constr(slack_constraint_coeff * slack_variable + xsum(
                coefficient * variable for coefficient, variable in
                constraint_lhs) <= constraint_rhs, name=f"{id}_constraint")
        elif constraint_sense == '>=':
            constraint = self._solver.add_constr(slack_constraint_coeff * slack_variable + xsum(
                coefficient * variable for coefficient, variable in
                constraint_lhs) >= constraint_rhs, name=f"{id}_constraint")

        return constraint, slack_variable

    def add_constr(self, lin_expr: "LinExpr", name):
        self._solver.add_constr(lin_expr, name)

    def add_var(self,
        name = "",
        obj = 0,
        lb = 0,
        ub= INF,
        var_type=CONTINUOUS,
        column = None):
        self._variables[name] = self._solver.add_var(
            name=name,
            lb=lb,
            ub=ub,
            obj=obj,
            var_type=var_type,
            column=column)
        return self._variables[name]

    def var_by_name(self, name):
        if name in self._variables:
            return self._variables[name]
        return None
