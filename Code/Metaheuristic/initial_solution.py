"""
Set to create initial solution
"""
from solution import Solution


class InitialSolution(Solution):
    """
    Class to create initial solution
    """

    def __init__(self, scenario):
        # inherit from parent class
        Solution.__init__(self, scenario)

        self.shift_requirement = None
        #self.solution = Solution

    def assign_skill_requests(self, scenario):
        """
        Function to assign skill request to employees
        """

        # need employees grouped based on skill
        # creation of employee classes
        # skill counter object and way to fill object
        for day_index, request_per_day in enumerate(scenario.skill_requests):
            # create collection of nurses available on day
            for skill_index, request_per_day_per_skill in enumerate(request_per_day):
                # update to remove employees that are assigned on that day
                employees_with_skill = scenario.employees.get_employee_w_skill(scenario.skills[skill_index])
                for s_type_index, request_per_day_per_skill_per_s_type in enumerate(request_per_day_per_skill):
                    print(request_per_day_per_skill_per_s_type)
                    n = request_per_day_per_skill_per_s_type
                    while n > 0:
                        # pick one of available nurses
                        employee_id = employees_with_skill.random_pick()
                        # add shift type to nurse
                        scenario.employees._collection[employee_id].update_shift_assignment(
                            day_index, s_type_index)
                        # TODO update other nurses information #########
                        # update skill counter

                        # remove nurse from available nurses for skills
                        # remove nurse from available nurses for day

                        # remove skill request
                        n -= 1

        # wil ik hier iets returnen?
        return None
