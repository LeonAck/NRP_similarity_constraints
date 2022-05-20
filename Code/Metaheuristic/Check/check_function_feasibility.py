import numpy as np
from deepdiff import DeepDiff
import pprint
from Invoke.Initial_solution.initial_solution import BuildSolution
from Invoke.Constraints.Rules.RuleH3 import RuleH3
from Invoke.Constraints.Rules.RuleS5Max import RuleS5Max
from Invoke.Constraints.Rules.RuleS6 import RuleS6

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

    def h3_check_function(self, solution, scenario):
        """
        Function to check the number of forbidden shift type successions
        """
        violation_counter = 0
        for employee_id in scenario.employees._collection.keys():
            for d_index in range(0, scenario.num_days_in_horizon):
                allowed_shift_types = RuleH3().get_allowed_shift_types(solution, scenario, employee_id, d_index)
                if solution.shift_assignments[employee_id][d_index][0] != - 1 \
                        and solution.shift_assignments[employee_id][d_index][0] not in allowed_shift_types:
                    violation_counter += 1

        return violation_counter

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
                        print([[employee_id, solution.shift_assignments[employee_id][d_index]] == np.array(s_index, sk_index) for employee_id in solution.shift_assignments.keys()])
                        print("info is incorrect")
                        break

    def work_stretches_info(self, solution, scenario, operator_info):
        """
        Function to find differences in the work stretch information
        """
        flag = True
        collected_work_stretches = BuildSolution(scenario).collect_work_stretches(solution)
        if collected_work_stretches != solution.work_stretches:
            print("stretches is false")
            flag = False

        if not flag:
            deepdiff = DeepDiff(collected_work_stretches, solution.work_stretches)
            try:
                employee_id = list(deepdiff['values_changed'].keys())[0].split("['", 1)[1].split("']")[0]
            except KeyError:
                try:
                    employee_id = deepdiff['dictionary_item_added'][0].split("['", 1)[1].split("']")[0]
                except KeyError:
                    employee_id = deepdiff['dictionary_item_removed'][0].split("['", 1)[1].split("']")[0]
            pprint.pprint(deepdiff)

            if "work_stretches_1" in operator_info:
                print("start", operator_info['start_index'])
                print("end", operator_info['end_index'])
                print("employee_1", operator_info['employee_id_1'])
                print("employee_2", operator_info['employee_id_2'])
                print("work_stretches_1", operator_info['work_stretches_1'])
                print("work_stretches_2", operator_info['work_stretches_2'])
                print("\nedge", operator_info['edge_work_stretches'])
                print("overlapping", operator_info['overlapping_work_stretches'])
                print("\nTimeline__", np.array(range(0, len(solution.day_collection.num_days_in_horizon))))
                print("employee_1",solution.shift_assignments[operator_info['employee_id_1']][:, 0])
                print("employee_2",solution.shift_assignments[operator_info['employee_id_2']][:, 0])
            elif "current_working" in operator_info:
                print("d_index", operator_info['d_index'])
            print("hi")

        return flag

    def check_number_of_work_stretches(self, solution, scenario):
        flag = True
        collected_work_stretches = BuildSolution(scenario).collect_work_stretches(solution)
        for employee_id, employee_work_stretches in solution.work_stretches.items():
            if len(employee_work_stretches) != len(collected_work_stretches[employee_id]):
                print("different number of work stretches")
                flag = False
                break

        return flag

    def day_off_stretches_info(self, solution, scenario, change_info):
        """
        Function to find differences in the day off stretch information
        """
        flag = True

        collected_day_off_stretches = BuildSolution(scenario).collect_day_off_stretches(solution)

        if collected_day_off_stretches != solution.day_off_stretches :
            print("stretches is false")
            flag = False

        if not flag:
            deepdiff = DeepDiff(collected_day_off_stretches, solution.day_off_stretches)
            try:
                employee_id = list(deepdiff['values_changed'].keys())[0].split("['", 1)[1].split("']")[0]
            except KeyError:
                try:
                    employee_id = deepdiff['dictionary_item_added'][0].split("['", 1)[1].split("']")[0]
                except KeyError:
                    employee_id = deepdiff['dictionary_item_removed'][0].split("['", 1)[1].split("']")[0]
            # print("on {} for employee {}".format(change_info['d_index'], change_info['employee_id']))
            # print("current working: {}, new working: {}".format(change_info['current_working'],
            #                                                     change_info['new_working']))

            pprint.pprint(deepdiff)
            print("true", collected_day_off_stretches[employee_id])
            print("saved", solution.day_off_stretches[employee_id])
            print("shift_assignment", solution.shift_assignments[employee_id][:, 0])

            print("hi")

        return flag

    def shift_stretches_info(self, solution, scenario, operator_info, operator_name):
        if operator_name == "change":
            return self.shift_stretches_info_change(solution, scenario, operator_info)
        elif operator_name == "swap":
            return self.shift_stretches_info_swap(solution, scenario, operator_info)

    def shift_stretches_info_swap(self, solution, scenario, operator_info):
        """
        Function to find differences in the day off stretch information
        """
        flag = True
        collected_shift_stretches = BuildSolution(scenario).collect_shift_stretches(solution)
        if collected_shift_stretches != solution.shift_stretches:
            print("stretches is false")
            flag = False

        if not flag:
            deepdiff = DeepDiff(collected_shift_stretches, solution.shift_stretches)
            try:
                employee_id = list(deepdiff['values_changed'].keys())[0].split("['", 1)[1].split("']")[0]
            except KeyError:
                try:
                    employee_id = deepdiff['dictionary_item_added'][0].split("['", 1)[1].split("']")[0]
                except KeyError:
                    employee_id = deepdiff['dictionary_item_removed'][0].split("['", 1)[1].split("']")[0]

            pprint.pprint(deepdiff)
            print("hi")

        return flag

    def shift_stretches_info_change(self, solution, scenario, operator_info):
        """
        Function to find differences in the day off stretch information
        """
        flag = True
        collected_shift_stretches = BuildSolution(scenario).collect_shift_stretches(solution)
        if collected_shift_stretches != solution.shift_stretches:
            print("stretches is false")
            flag = False

        if not flag:
            deepdiff = DeepDiff(collected_shift_stretches, solution.shift_stretches)
            try:
                employee_id = list(deepdiff['values_changed'].keys())[0].split("['", 1)[1].split("']")[0]
            except KeyError:
                try:
                    employee_id = deepdiff['dictionary_item_added'][0].split("['", 1)[1].split("']")[0]
                except KeyError:
                    employee_id = deepdiff['dictionary_item_removed'][0].split("['", 1)[1].split("']")[0]
            print("on {} for employee {}".format(operator_info['d_index'], operator_info['employee_id']))
            print("current working: {}, new working: {}".format(operator_info['current_working'],
                                                                operator_info['new_working']))

            pprint.pprint(deepdiff)
            if operator_info['current_working']:
                print('\ncurrent s_type', operator_info['curr_s_type'])
                print("true current", collected_shift_stretches[operator_info['curr_s_type']][employee_id])
                print("saved current", solution.shift_stretches[operator_info['curr_s_type']][employee_id])
            if operator_info['new_working']:
                print('\nnew s_type', operator_info['new_s_type'])
                print("true new", collected_shift_stretches[operator_info['new_s_type']][employee_id])
                print("saved new", solution.shift_stretches[operator_info['new_s_type']][employee_id])

            print("shift_assignment", solution.shift_assignments[employee_id][:, 0])
            print("hi", flag)

        return flag


    def check_objective_value(self, solution, scenario, change_info):
        """
        Check whether calculated objective value equals actual objective value
        """
        flag = True
        equal = solution.obj_value == solution.calc_objective_value(scenario, rule_collection=scenario.rule_collection)

        if not equal:
            print("on {} for employee {}".format(change_info['d_index'], change_info['employee_id']))
            print("current working: {}, new working: {}".format(change_info['current_working'],
                                                                change_info['new_working']))
            print("tracked_violations", solution.violation_array)
            print("true_violations", solution.get_violations(scenario, scenario.rule_collection))
            print("tracked obj value is {} while calculated is {}".format(solution.obj_value, solution.calc_objective_value(scenario, rule_collection=scenario.rule_collection)))
            flag = False

        return flag
    def check_violation_array(self, solution, scenario, operator_info, operator_name):
        if operator_name == "change":
            return self.check_violation_array_change(solution, scenario, operator_info)
        elif operator_name == "swap":
            return self.check_violation_array_swap(solution, scenario, operator_info)

    def check_violation_array_change(self, solution, scenario, change_info):
        """
        Check whether tracked violations are different from calculated
        """
        flag = True
        calc_violations = solution.get_violations(scenario, scenario.rule_collection)
        for i, violation in enumerate(solution.violation_array):
            if calc_violations[i] != violation:
                # print("on {} for employee {}".format(change_info['d_index'], change_info['employee_id']))
                # print("current working: {}, new working: {}".format(change_info['current_working'],
                #                                                     change_info['new_working']))

                print("number of violation for soft constraint {} is tracked {} and calc {}".format(
                    i, violation, calc_violations[i]
                ))
                # if change_info['current_working']:
                #     print("current shift type", change_info['curr_s_type'])
                # if change_info['new_working']:
                #     print("new shift type", change_info['new_s_type'])
                # print("past: {}, present: {}, future: {}".format(
                #     solution.shift_assignments[change_info['employee_id']][change_info['d_index']-1][0],
                #     solution.shift_assignments[change_info['employee_id']][change_info['d_index']][0],
                #     solution.shift_assignments[change_info['employee_id']][change_info['d_index']+1][0] if change_info['d_index'] < solution.day_collection.num_days_in_horizon-1 else "-"))

                # print("violation per d, s, sk after change",
                #       RuleS1().count_violations_day_shift_skill(solution, scenario, change_info["d_index"],
                #                                                 change_info["new_s_type"], change_info["new_sk_type"]))
                # print("optimal request", solution.diff_opt_request[
                #     (change_info["d_index"], change_info["new_sk_type"], change_info["new_s_type"],)]+scenario.skill_requests[
                #     (change_info["d_index"], change_info["new_sk_type"], change_info["new_s_type"],)])
                # print("actual assignments: ",
                #       RuleS1().count_assignments_day_shift_skill(solution, change_info["d_index"],
                #                                                  change_info["new_s_type"], change_info["new_sk_type"]))
                # print(solution.shift_assignments[change_info['employee_id']][:, 0])

                flag = False

        return flag

    def check_violation_array_swap(self, solution, scenario, swap_info):
        flag = True
        calc_violations = solution.get_violations(scenario, scenario.rule_collection)
        for i, violation in enumerate(solution.violation_array):
            if calc_violations[i] != violation:
                # print("on {} for employee {}".format(change_info['d_index'], change_info['employee_id']))
                # print("current working: {}, new working: {}".format(change_info['current_working'],
                #                                                     change_info['new_working']))

                print("number of violation for soft constraint {} is tracked {} and calc {}".format(
                    i, violation, calc_violations[i]
                ))
                print("start", swap_info['start_index'])
                print("end", swap_info['end_index'])
                # print("working_1:", solution.num_working_weekends[swap_info['employee_id_1']])
                # print("change_weekends_1: ", swap_info['change_working_weekends'][swap_info['employee_id_1']])
                # print("parameter_1: ", solution.rule_collection.collection['S6'].parameter_per_employee[swap_info['employee_id_1']])
                # print("working_2: ", solution.num_working_weekends[swap_info['employee_id_2']])
                # print("change_weekends_2: ", swap_info['change_working_weekends'][swap_info['employee_id_2']])
                # print("parameter_2: ",
                #       solution.rule_collection.collection['S6'].parameter_per_employee[swap_info['employee_id_2']])
                # pprint.pprint(solution.day_collection.weekends)
                print(solution.forbidden_shift_type_successions)
                print("employee_1, start-1: {}, start: {},  end: {}, end + 1: {}".format(
                    solution.shift_assignments[swap_info['employee_id_1']][swap_info['start_index']-1][0],
                solution.shift_assignments[swap_info['employee_id_1']][swap_info['start_index']][0],
                solution.shift_assignments[swap_info['employee_id_1']][swap_info['end_index']][0],
                solution.shift_assignments[swap_info['employee_id_1']][swap_info['end_index']+1][0]))
                print("employee_2, start-1: {}, start: {},  end: {}, end + 1: {}".format(
                    solution.shift_assignments[swap_info['employee_id_2']][swap_info['start_index'] - 1][0],
                    solution.shift_assignments[swap_info['employee_id_2']][swap_info['start_index']][0],
                    solution.shift_assignments[swap_info['employee_id_2']][swap_info['end_index']][0],
                    solution.shift_assignments[swap_info['employee_id_2']][swap_info['end_index'] + 1][0]))
                print(solution.shift_assignments[swap_info['employee_id_1']][:,0])
                print(solution.shift_assignments[swap_info['employee_id_2']][:,0])
                print("hi")

                flag = False
                a = 5

        return flag

    def check_working_weekends(self, solution, scenario):
        for employee_id in scenario.employees._collection.keys():
            working_weekends = 0
            for weekend in scenario.day_collection.weekends.values():
                # a weekend is a working weekend if one of the two days is assigned
                if solution.check_if_working_day(employee_id, weekend[0]) or \
                        solution.check_if_working_day(employee_id, weekend[1]):
                    working_weekends += 1

            if solution.num_working_weekends[employee_id] != working_weekends:
                print("\nworking weekends are off")
                print(employee_id)
                print("actual: {}, tracked: {}".format(working_weekends, solution.num_working_weekends[employee_id]))
                print(solution.shift_assignments[employee_id][:,0])

                print(employee_id)



    def check_day_comparison_info(self, solution, scenario, change_info):
        flag = True
        collected_day_comparison = BuildSolution(scenario).collect_ref_day_comparison(solution)

        deepdiff = DeepDiff(collected_day_comparison, solution.day_comparison)

        if deepdiff:
            pprint.pprint(deepdiff)
            flag = False
            try:
                employee_id = list(deepdiff['values_changed'].keys())[0].split("['", 1)[1].split("']")[0]
            except KeyError:
                try:
                    employee_id = deepdiff['dictionary_item_added'][0].split("['", 1)[1].split("']")[0]
                except KeyError:
                    employee_id = deepdiff['dictionary_item_removed'][0].split("['", 1)[1].split("']")[0]
            print("on {} for employee {}".format(change_info['d_index'], employee_id))
            print("current working: {}, new working: {}".format(change_info['current_working'],
                                                                change_info['new_working']))
            print("\n working this day: {}".format(solution.check_if_working_day(employee_id, change_info['d_index'])))
            print("working ref day: {}".format(solution.check_if_working_day(employee_id, change_info['d_index']-4)))
            print("hi")

        return flag

    def check_shift_comparison_info(self, solution, scenario, change_info):
        flag = True
        collected_shift_comparison = BuildSolution(scenario).collect_ref_shift_comparison(solution)

        deepdiff = DeepDiff(collected_shift_comparison, solution.shift_comparison)

        if deepdiff:
            pprint.pprint(deepdiff)
            flag = False
            try:
                employee_id = list(deepdiff['values_changed'].keys())[0].split("['", 1)[1].split("']")[0]
            except KeyError:
                try:
                    employee_id = deepdiff['dictionary_item_added'][0].split("['", 1)[1].split("']")[0]
                except KeyError:
                    employee_id = deepdiff['dictionary_item_removed'][0].split("['", 1)[1].split("']")[0]
            print("on {} for employee {}".format(change_info['d_index'], employee_id))
            print("current working: {}, new working: {}".format(change_info['current_working'],
                                                                change_info['new_working']))
            print("\n working this day: {}".format(solution.check_if_working_day(employee_id, change_info['d_index'])))
            print("working ref day: {}".format(solution.check_if_working_day(employee_id, change_info['d_index'] - 4)))
            print("hi")

        return flag

    def check_number_of_assignments_per_nurse(self, solution, scenario, operator_info):
        flag = True
        calc_num_assignments = {}
        for employee_id in scenario.employees._collection.keys():
            calc_num_assignments[employee_id] = RuleS5Max().count_assignments_in_stretch(solution, employee_id,
                                                                                         0, scenario.num_days_in_horizon-1)
        deepdiff = DeepDiff(calc_num_assignments, solution.num_assignments_per_nurse)

        if deepdiff:
            pprint.pprint(operator_info)
            pprint.pprint(deepdiff)
            flag = False

        return flag

    def check_working_days(self, solution, scenario):
        flag = True

        for employee_id in scenario.employees._collection.keys():
            for d_index in range(0, scenario.num_days_in_horizon):
                if (not solution.check_if_working_day(employee_id, d_index)
                        and d_index in solution.working_days[employee_id])\
                        or (solution.check_if_working_day(employee_id, d_index)
                            and not d_index in solution.working_days[employee_id]):
                    print("working days wrong")
                    print(solution.working_days[employee_id])
                    print(solution.shift_assignments[employee_id][:, 0])
                    flag = False

        return flag



