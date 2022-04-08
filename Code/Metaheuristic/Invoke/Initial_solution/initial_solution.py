"""
Set to create initial solution
"""
import numpy as np

from solution import Solution
from Domain.employee import EmployeeCollection
from Check.check_function_feasibility import FeasibilityCheck
from Invoke.Constraints.Rules.RuleS6 import RuleS6


class InitialSolution(Solution):
    """
    Class to create initial solution
    """

    def __init__(self, scenario):
        # inherit from parent class
        super().__init__()

        self.scenario = scenario

        # initialize shift assignment objects
        self.shift_assignments = self.create_shift_assignments()

        # assign skill requests based on H1, H2 and H4
        self.assign_skill_requests()

        # create array to keep track of difference between optimal skill_requests and actual skill assignment
        self.diff_min_request = self.initialize_diff_min_request(self.scenario)
        # create array to keep track of difference between optimal skill_requests and actual skill assignment
        self.diff_opt_request = self.initialize_diff_opt_request(self.scenario)

        # collect number of assignments per nurse
        self.num_assignments_per_nurse = self.get_num_assignments_per_nurse()

        # collect number of working weekends per nurse
        self.num_working_weekends = RuleS6().count_working_weekends_employee(solution=self, scenario=self.scenario)

        # calc objective value
        self.obj_value = self.calc_objective_value(solution=self, rule_collection=self.scenario.rule_collection)

    def assign_skill_requests(self):
        """
        Function to assign skill request to employees
        """
        # get requests per day
        for day_index, request_per_day in enumerate(self.scenario.skill_requests):
            # create collection of nurses available on day
            employees_available_on_day = EmployeeCollection().initialize_employees(self.scenario, self.scenario.employees_specs)

            #  loop through requests per day and per skill
            for skill_index, request_per_day_per_skill in enumerate(request_per_day):

                # create set of employees with skill that are available on that day
                employees_with_skill = employees_available_on_day.get_employee_w_skill(self.scenario.skills[skill_index])

                for s_type_index, request_per_day_per_skill_per_s_type in enumerate(request_per_day_per_skill):
                    n = request_per_day_per_skill_per_s_type
                    while n > 0:
                        # pick one of available nurses
                        employee_id = employees_with_skill.random_pick()
                        # add shift type to nurse
                        self.replace_shift_assignment(employee_id, day_index, s_type_index, skill_index)
                        # TODO update other nurses information
                        # remove nurse from available nurses for day
                        employees_available_on_day = employees_available_on_day.exclude_employee(employee_id)
                        # remove nurse from available nurses for skills
                        employees_with_skill = employees_with_skill.exclude_employee(employee_id)

                        # remove skill request
                        n -= 1
                    FeasibilityCheck().check_understaffing(solution=self,
                                                           scenario=self.scenario,
                                                           d_index=day_index,
                                                           s_index=s_type_index,
                                                           sk_index=skill_index,
                                                           skill_request=request_per_day_per_skill_per_s_type)

    def initialize_diff_opt_request(self, scenario):
        """
        Initialize object that calculates shortage/surplus between optimal skill requests
        and number of assignments to that request
        :return:
        array
        """
        # subtract minimal level from optimal level
        return scenario.skill_requests - scenario.optimal_coverage

    def initialize_diff_min_request(self, scenario):
        """
        Initialize object that calculates shortage/surplus between minimum skill requests
        and number of assignments to that request
        :return:
        array
        """
        # subtract minimal level from optimal level
        return np.zeros((scenario.num_days_in_horizon,
                                  scenario.skill_collection.num_skills,
                                  scenario.num_shift_types))

    def create_shift_assignments(self):
        """
        Create dict to store employee shift assignments
        Each array has as length the number of days
        Each element in the array store the assignment of the nurse on that day
        0 --> off
        1 --> s_type_1
        2 --> s_type_2
        etc.
        :return:
        dict with key: employee_id, value: array of zeros
        """
        shift_assignments = {}
        for employee_id in self.scenario.employees._collection.keys():
            # shift_assignments[id] = np.array([{'s_type': 0, 'sk_type': 0}] * self.scenario.num_days_in_horizon)
            shift_assignments[employee_id] = np.full((self.scenario.num_days_in_horizon, 2), -1, dtype=int)
        # two dimensioal array
        return shift_assignments

    def get_num_assignments_per_nurse(self):
        """
        Function to calculate for each nurse the number of assignments
        """
        num_assignments = {}
        # for each employee sum the number of assignments
        for employee_id in self.scenario.employees._collection.keys():
            # employee is unassigned if shift type is -1
            num_assignments[employee_id] = sum([assignment[0] != -1 for assignment in
                                                self.shift_assignments[employee_id]])

        return num_assignments

    def get_num_working_weekends(self):
        """
        Function to calculate the working weekends for each employee
        """






    def calc_objective_value(self, solution, rule_collection):
        """
        Function to calculate the objective value of a solution based on the
        applied soft constraints
        """
        violation_array = np.zeros(len(rule_collection.soft_rule_collection.collection))
        for i, rule in enumerate(rule_collection.soft_rule_collection.collection.values()):
            violation_array[i] = rule.count_violations(solution, self.scenario)

        return np.matmul(violation_array, rule_collection.penalty_array)


