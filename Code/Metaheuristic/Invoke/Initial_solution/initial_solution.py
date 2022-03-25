"""
Set to create initial solution
"""
import numpy as np

from solution import Solution
from Domain.employee import EmployeeCollection
from Check.check_function_feasibility import FeasibilityCheck


class InitialSolution(Solution):
    """
    Class to create initial solution
    """

    def __init__(self, scenario):
        # inherit from parent class
        super().__init__(scenario)
        self.scenario = scenario

        self.shift_requirement = None

        # assign skill requests based on H1, H2 and H4
        self.assign_skill_requests()

        # create array to keep track of difference between optimal skill_requests and actual skill assignment
        self.diff_min_request = self.initialize_diff_min_request(self.scenario)
        # create array to keep track of difference between optimal skill_requests and actual skill assignment
        self.diff_opt_request = self.initialize_diff_opt_request(self.scenario)

    def assign_skill_requests(self):
        """
        Function to assign skill request to employees
        """
        # get requests per day
        for day_index, request_per_day in enumerate(self.scenario.skill_requests):
            # create collection of nurses available on day
            employees_available_on_day = EmployeeCollection().initialize_employees(self.scenario, self.scenario.employees_spec)

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
                        # TODO update other nurses information #########
                        # remove nurse from available nurses for day
                        employees_available_on_day = employees_available_on_day.exclude_employee(employee_id)
                        # remove nurse from available nurses for skills
                        employees_with_skill = employees_with_skill.exclude_employee(employee_id)

                        # remove skill request
                        n -= 1
                    FeasibilityCheck().check_understaffing(solution=self,
                                                           scenario=self.scenario,
                                                           day_index=day_index,
                                                           s_type_index=s_type_index,
                                                           skill_index=skill_index,
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


