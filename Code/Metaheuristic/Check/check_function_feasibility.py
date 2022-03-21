import numpy as np
class FeasibilityCheck:
    """
    Class to store feasiblity function of the solution
    """
    def __init__(self):
        pass

    def h2_check_function(self, solution, scenario):
        """
        Function to check whether there is understaffing
        """
        flag = 0
        for day_index, request_per_day in enumerate(scenario.skill_requests):
            for skill_index, request_per_day_per_skill in enumerate(request_per_day):
                for s_type_index, request_per_day_per_skill_per_s_type in enumerate(request_per_day_per_skill):
                    flag = self.check_understaffing(solution, scenario,
                                                    day_index, s_type_index, skill_index,
                                                    request_per_day_per_skill_per_s_type)

        return flag

    def check_understaffing(self, solution, scenario, day_index, s_type_index, skill_index, skill_request):
        """
        Function to check understaffing in skill counter for one skill request
        :return:
        True or False
        """
        flag = 0
        skill_id = scenario.skill_collection.index_to_id(skill_index)
        # sum assigned number of assigned nurse for day, skill and shift_type
        total_skill_counter = np.sum(solution.skill_counter[day_index,
                                                            s_type_index,
                                                            scenario.skill_collection.collection[
                                                                skill_id].indices_in_skill_counter])
        # compare if equal to skill request
        if skill_request != total_skill_counter:
            flag += 1
            raise ValueError('request {} is not equal to assigned {}'.format(
               skill_request, total_skill_counter))

        return flag

    def assignments_equals_skill_counter(self, solution, scenario):
        return None


