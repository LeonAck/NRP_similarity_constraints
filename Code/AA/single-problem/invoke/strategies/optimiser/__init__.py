import os
from datetime import datetime, timedelta
from alfa_sdk import AlgorithmClient
from numbers import Number
from strategies.optimiser.solver import Solver
from strategies.optimiser import generate
from strategies.optimiser import output
from config import configuration
from copy import copy

VAR_DEFAULTS = configuration.optimiser.variables

class Optimiser(object):

    def __init__(self, domain, employees=None, shifts=None, supressOutput=False):
        self.domain = domain

        if domain.employees or domain.shifts:
            self.domain = copy(domain)
        if employees:
            self.domain.employees = employees
        self.employees = self.domain.employees
        if shifts:
            self.domain.shifts = shifts
            self.domain.employees.refresh_shift_properties(shifts, self.domain.settings)
        self.shifts = self.domain.shifts
        self.suppressOutput = supressOutput
        self.solver = Solver()

    def find_solution(self, superset_emps=None, superset_shifts=None):
        self._build_problem(superset_emps, superset_shifts)
        self._solve_problem()
        results = self._generate_response()
        # self.create_and_send_kpis(self.domain, results)
        return results

    def _build_problem(self, superset_emps, superset_shifts):

        generate.variables.potential_assignments(self.solver, self.employees)
        generate.variables.set_initial_solution(self.solver, self.domain.initial_solution)
        generate.variables.set_assignment_objectives(self.solver, self.employees, self.domain.settings, self.domain.travel_expenses_matrix)

        print('start constraints: {}'.format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')))
        if self.domain.rules.works_on_variable_required():
            generate.variables.works_on_off(self.solver, self.employees, self.domain.days)
            generate.constraints.works_on_off(self.solver, self.employees, self.domain.days)
        if self.domain.settings.disallow_employee_mix:
            generate.constraints.disallow_employee_mix(self.solver, self.employees)
        print('end constraints: {}'.format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')))

        print('start rules: {}'.format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')))
        self._add_rules(superset_emps, superset_shifts)
        print('end rules: {}'.format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')))

    def _add_rules(self, superset_emps, superset_shifts):
        for rule_id, rules_of_id in self.domain.rules.items():
            for index, rule in enumerate(rules_of_id):
                if rule.penalty != 0 and rule.is_active:
                    try:
                        class_ = getattr(generate.rules, 'Rule' + rule.id)
                        if superset_emps and str(rule.id) in ["60", "62"]:
                            class_(rule).set_rule(self.solver, self.domain, superset_emps, superset_shifts)
                        else:
                            class_(rule).set_rule(self.solver, self.domain)
                    except AttributeError as e:
                        import sys
                        raise type(e)(str(e) +
                                      ' causes an error in rule with id' + rule_id).with_traceback(sys.exc_info()[2])

    def _solve_problem(self):
        start_solving_time = datetime.now()
        print('start solve problem: {}'.format(datetime.strftime(start_solving_time, '%Y-%m-%d %H:%M:%S.%f')))
        self.result = self.solver.solve(
            runtime=self.domain.settings.runtime,
            linear_relaxation=self.domain.settings.linear_relaxation,
            emphasis=self.domain.settings.emphasis,
            mip_gap=self.domain.settings.mip_gap,
            preprocess=self.domain.settings.preprocess,
            seed=self.domain.settings.seed,
            logging=self.domain.settings.logging,
        )
        end_solving_time = datetime.now()
        self.solver_runtime = (end_solving_time - start_solving_time).total_seconds()
        print('end solve problem: {}'.format(datetime.strftime(end_solving_time, '%Y-%m-%d %H:%M:%S.%f')))
        print('Problem solved in {} seconds'.format(self.solver_runtime))

    def _generate_response(self):
        response = {
            'result': self.result,
            'shifts': [],
            'rule_violations': [],
            'lower_bound': self.solver._solver.objective_bound,
            'upper_bound': self.solver._solver.objective_value,
            'goal_score': self.solver._solver.objective_value,
            'technical_kpis': {
                'runtime': self.solver_runtime,
                'lower_bound': self.solver._solver.objective_bound,
                'upper_bound': self.solver._solver.objective_value,
                "use_shifting_window": self.domain.settings.run_shifting_window,
                "use_improvement_heuristic": self.domain.settings.improve_results,
                "progress_log": self.solver.get_search_progress_log(self.domain.settings.search_progress_log_size),
                "mip_gap": -1
            }
        }
        objective_value = None
        if self.solver.result_is_valid(self.result):
            objective_value = round(self.solver.objective_value, 2)

        if objective_value is not None:
            response["shifts"] = output.generate_shifts_output(
                self.solver, self.domain.employees, self.domain.settings,
                self.domain.travel_expenses_matrix)
            response["unassigned_shifts"] = output.generate_unassigned_shifts_output(
                self.solver, self.domain)
            violations = self.get_violations()
            # for rule_id in set([violation.rule_id for violation in violations]):
            #     print(rule_id, " : ", sum([violation.rule_id == rule_id for violation in violations]))
            response["rule_violations"] = [violation.generate_output() for violation in violations]

            # response["violations"] = output.generate_violation_output(self.solver,
            # self.domain.settings, objective, self.domain.employees, self.domain.shifts,
            # self.domain.days, f"{rule_id}.{index}")

            lower_bound = self.solver._solver.objective_bound \
                if self.solver._solver.objective_bound != 0 else 1e-8
            response["technical_kpis"]["mip_gap"] = (self.solver._solver.objective_value - lower_bound
                                                     ) / lower_bound

        return response


    # def create_and_send_kpis(self, filehandler, results):
    #     kpis = self.create_kpis(filehandler, results)
    #     self.send_kpis(kpis)
    #
    # def create_kpis(self, domain, results):
    #     number_of_assigned_shifts = len(results['shifts'])
    #     number_of_unassigned_shifts = len(
    #         [rule_violation for rule_violation in results['rule_violations'] if str(rule_violation['rule_id']) == "1"])
    #     number_of_rule_violations = len(
    #         [rule_violation for rule_violation in results['rule_violations'] if str(rule_violation['rule_id']) != "1"])
    #     total_shift_costs = 0
    #     for shift in results['shifts']:
    #         if 'shift_costs' in shift:
    #             total_shift_costs += shift['shift_costs']
    #     KPIs = filehandler.kpi_properties
    #     KPIs["assigned_shifts"] = number_of_assigned_shifts
    #     KPIs["unassigned_shifts"] = number_of_unassigned_shifts
    #     KPIs["number_of_rule_violations"] = number_of_rule_violations
    #     KPIs["total_costs"] = total_shift_costs
    #     return KPIs
    #
    # def send_kpis(self, kpis):
    #     if os.environ.get('ALFA_CONTEXT'):
    #         client = AlgorithmClient()
    #         client.store_kpi(self.transform_kpis(kpis), self.domain.kpi_properties["entity"])

    def transform_kpis(self, kpis):
        transformed_kpis = []
        for name, value in kpis.items():
            if (isinstance(value, Number)):
                transformed_kpis.append({
                    "name": name,
                    "value": value,
                    'period': self.domain.kpi_properties["period"],
                })
        return transformed_kpis

    def get_violations(self):
        violations = []
        for rule_id, rules_of_id in self.domain.rules.items():
            for index, rule in enumerate(rules_of_id):
                if rule.penalty != 0 and not rule.is_mandatory and rule.is_active:
                    try:
                        class_ = getattr(generate.rules, 'Rule' + rule.id)
                        class_(rule).add_violation_to_output(self.solver, self.domain, violations)
                    except AttributeError as e:
                        import sys
                        raise type(e)(str(e) +
                                      ' causes an error in rule with ID = ' + rule_id).with_traceback(sys.exc_info()[2])
        return violations
