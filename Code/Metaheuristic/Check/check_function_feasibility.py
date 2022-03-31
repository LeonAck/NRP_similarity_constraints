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
        for d_index, request_per_day in enumerate(scenario.skill_requests):
            for sk_index, request_per_day_per_skill in enumerate(request_per_day):
                for s_type_index, request_per_day_per_skill_per_s_type in enumerate(request_per_day_per_skill):
                    flag = self.check_understaffing(solution, scenario,
                                                    d_index, s_type_index, sk_index,
                                                    request_per_day_per_skill_per_s_type)

        return flag

    def check_understaffing(self, solution, scenario, d_index, s_index, sk_index, skill_request):
        """
        Function to check understaffing in skill counter for one skill request
        :return:
        True or False
        """
        flag = 0
        #skill_id = scenario.skill_collection.index_to_id(skill_index)
        # sum assigned number of assigned nurse for day, skill and shift_type
        # total_skill_counter = np.sum(solution.skill_counter[day_index,
        #                                                     s_type_index,
        #                                                     scenario.skill_collection.collection[
        #                                                         skill_id].indices_in_skill_counter])

        total_assigned = sum([np.array_equal(shift_assignment[d_index], np.array([s_index, sk_index])) for shift_assignment in solution.shift_assignments.values()])
        # compare if equal to skill request
        if skill_request > total_assigned:
            flag = False
            raise ValueError('request {} is not equal to assigned {}'.format(
               skill_request, total_assigned))

        return flag

    def assignments_equals_skill_counter(self, solution, scenario):
        """
        Function to check whether number of assignments to a shift
        equals the number of assigned in the skill_counter
        """
        flag = True
        for d_index, day_counts in enumerate(solution.skill_counter):
            tot_day = np.sum(day_counts)
            tot_assigned = 0
            for shift_assignments in solution.shift_assignments.values():
                if shift_assignments[d_index] > 0:
                    tot_assigned += 1
            if tot_day != tot_assigned:
                flag = False
                raise ValueError('tot daily counter {} is not equal to assigned to nurses{}'.format(
                    tot_day, tot_assigned))

        return flag

    def assignment_equals_tracked_info(self, solution, scenario):
        """
        Function to check whether the cumulative shift assignments
        per (day, skill, shift)-combination equals the number in diff_min_req
        and diff_opt_req
        :return:
        True if information is correct else False
        """
        flag = True
        real_assignments = scenario.skill_requests + solution.diff_min_request

        # create dict with total numbers of assignments
        cumulative_assignments = []
        for d_index in range(scenario.num_days_in_horizon):
            for s_index in scenario.shift_collection.shift_types_indices:
                for sk_index in scenario.skill_collection.skill_indices:
                    assignment_count = 0
                    for employee in solution.shift_assignments.values():
                        if np.array_equal(employee[d_index], np.array([s_index, sk_index])):
                            assignment_count += 1
                    if assignment_count != real_assignments[(d_index, sk_index, s_index)]:
                        print(assignment_count)
                        print(real_assignments[(d_index, sk_index, s_index)])
                        print("info is incorrect")
                        break


