"""
Set to create initial solution
"""

class InitialSolution:
    """
    Class to create initial solution
    """

    def __init__(self, scenario):

        self.shift_requirement = None


    def assign_skill_requests(self, scenario):
        """
        Function to assign skill request to employees
        """

        # need employees grouped based on skill
        # creation of employee classes
        # skill counter object and way to fill object
        for day_index, request_per_day in enumerate(scenario.skill_requests):
            for skill_index, request_per_day_per_skill in enumerate(request_per_day):
                employees_with_skill = scenario.employees.get_employee_w_skill(scenario.skills[skill_index])
                for s_type_index, request_per_day_per_skill_per_s_type in enumerate(request_per_day_per_skill):
                    print(request_per_day_per_skill_per_s_type)
                    n = request_per_day_per_skill_per_s_type
                    while n > 0:
                        # pick one of available nurses
                        employee_id = employees_with_skill.random_pick()
                        # add shift type to nurse
                        # add assignment to nurse
                        # update skill counter
                        # remove nurse from available nurses

                        # remove skill request
                        n -= 1

        # wil ik hier iets returnen?
        return None
