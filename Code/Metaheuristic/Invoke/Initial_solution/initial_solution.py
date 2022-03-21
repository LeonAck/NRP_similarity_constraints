"""
Set to create initial solution
"""
from solution import Solution
from Domain.employee import EmployeeCollection
from Check.check_function_feasibility import FeasibilityCheck


class InitialSolution(Solution):
    """
    Class to create initial solution
    """

    def __init__(self, scenario):
        # inherit from parent class
        Solution.__init__(self, scenario)

        self.shift_requirement = None
        #self.solution = Solution
        self.assign_skill_requests()

    def assign_skill_requests(self):
        """
        Function to assign skill request to employees
        """

        # need employees grouped based on skill
        # creation of employee classes
        # skill counter object and way to fill object
        for day_index, request_per_day in enumerate(self.scenario.skill_requests):
            # create collection of nurses available on day
            employees_available_on_day = EmployeeCollection().initialize_employees(self.scenario, self.scenario.employees_spec)

            for skill_index, request_per_day_per_skill in enumerate(request_per_day):

                # create set of employees with skill that are available on that day
                employees_with_skill = employees_available_on_day.get_employee_w_skill(self.scenario.skills[skill_index])
                for s_type_index, request_per_day_per_skill_per_s_type in enumerate(request_per_day_per_skill):
                    n = request_per_day_per_skill_per_s_type
                    while n > 0:
                        # pick one of available nurses
                        employee_id = employees_with_skill.random_pick()
                        # add shift type to nurse
                        self.replace_shift_assignment(employee_id, day_index, s_type_index)
                        # TODO update other nurses information #########
                        # update skill counter
                        self.update_skill_counter(day_index, s_type_index,
                                                  skill_index,
                                                  self.scenario.employees._collection[employee_id].skill_set_id)
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
        # wil ik hier iets returnen?
        return None
