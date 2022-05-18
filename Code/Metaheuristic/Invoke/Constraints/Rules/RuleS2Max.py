from Invoke.Constraints.initialize_rules import Rule
import numpy as np
from copy import deepcopy
import pprint

class RuleS2Max(Rule):
    """
        Rule that checks for optimal coverage per skill request
        Compares optimal skill request to number of nurses with that skill assigned to shift
    """

    def __init__(self, employees=None, rule_spec=None):
        super().__init__(employees, rule_spec)

    def count_violations(self, solution, scenario):
        """
        Function to count violations in the entire solution
        """
        return sum([self.count_violations_employee(solution.work_stretches[employee_id], employee_id)
                    for employee_id in scenario.employees._collection.keys()])

    def count_violations_employee(self, stretch_object_employee, employee_id):
        """
        Function to count violations for an employee
        """
        return sum([work_stretch['length'] - self.parameter_per_employee[employee_id]
                    for work_stretch in stretch_object_employee.values()
                    if work_stretch['length'] > self.parameter_per_employee[employee_id]])

    def update_information_off_to_assigned(self, solution, change_info):
        """
        Function to update solution information after change from off to assigned
        """
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1) \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index_1 = self.find_work_stretch_end(solution, employee_id, d_index - 1)

            solution.work_stretches[employee_id] = \
                self.merge_stretches(solution.work_stretches[employee_id],
                                     start_index_1=start_index_1,
                                     start_index_2=d_index + 1)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                solution.work_stretches[employee_id] \
                    = self.extend_stretch_pre(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    old_start=d_index + 1,
                    new_start=-solution.historical_work_stretch[employee_id])

            else:
                solution.work_stretches[employee_id] \
                    = self.extend_stretch_pre(stretch_object_employee=solution.work_stretches[employee_id],
                                              old_start=d_index + 1,
                                              new_start=d_index)


        elif not solution.check_if_first_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index - 1)
            # change end index by one
            solution.work_stretches[
                employee_id][start_index]['end_index'] += 1

            solution.work_stretches[
                employee_id][start_index]['length'] += 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                start_index = -solution.historical_work_stretch[employee_id]

                # change end index by one
                solution.work_stretches[
                    employee_id][start_index]['end_index'] += 1

                solution.work_stretches[
                    employee_id][start_index]['length'] += 1
            else:
                # create index of single length
                solution.work_stretches[employee_id][d_index] \
                    = {'end_index': d_index,
                       'length': 1}

        return solution

    def update_information_assigned_to_off(self, solution, change_info):
        """
        Function to update solution information after change from assigned to off
        """
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        # check if not the last or first day and in a work stretch
        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1) \
                and solution.check_if_working_day(employee_id, d_index - 1):

            start_index = self.find_work_stretch_middle(solution, employee_id, d_index)

            solution.work_stretches[employee_id] \
                = RuleS2Max().split_stretch(
                solution.work_stretches[employee_id],
                start_index_1=start_index,
                d_index=d_index)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                # shorten existing stretch
                solution.work_stretches[employee_id] = self.shorten_stretch_pre(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    old_start=-solution.historical_work_stretch[employee_id],
                    new_start=d_index + 1)

                # create new stretch for historical stretch
                solution.work_stretches[employee_id] = solution.create_stretch(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    start_index=-solution.historical_work_stretch[employee_id],
                    end_index=-1)
            else:
                solution.work_stretches[employee_id] = self.shorten_stretch_pre(
                    stretch_object_employee=solution.work_stretches[employee_id],
                    old_start=d_index,
                    new_start=d_index + 1)

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index)
            solution.work_stretches[employee_id][start_index]['end_index'] \
                -= 1
            solution.work_stretches[employee_id][start_index]['length'] \
                -= 1

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                start_index = -solution.historical_work_stretch[employee_id]
                solution.work_stretches[employee_id][start_index]['end_index'] \
                    -= 1
                solution.work_stretches[employee_id][start_index]['length'] \
                    -= 1
            else:
                try:
                    del solution.work_stretches[
                        employee_id][d_index]
                except KeyError:
                    print("hi")

        return solution

    def incremental_violations_change(self, solution, change_info, scenario=None):
        """
        Calculate the difference in violations after using the change opeator
        :return:
        delta number_of_violations
        """

        # check if moving from off to assigned
        if not change_info['current_working']:
            return self.incremental_violations_off_to_assigned(solution, change_info)
        # check if moving from assigned to off
        elif not change_info['new_working']:
            return self.incremental_violations_assigned_to_off(solution, change_info)
        else:
            return 0

    def incremental_violations_off_to_assigned(self, solution, change_info):
        employee_id = change_info['employee_id']
        d_index = change_info['d_index']
        employee_parameter = self.parameter_per_employee[employee_id]

        if solution.check_if_middle_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1) \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index - 1)

            return self.calc_incremental_violations_merge_stretch(solution.work_stretches[employee_id],
                                                                  rule_parameter=employee_parameter,
                                                                  start_index_1=start_index, start_index_2=d_index + 1)

        # check if not the last day and the day after working
        elif not solution.check_if_last_day(d_index) \
                and solution.check_if_working_day(employee_id, d_index + 1):
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:

                # return new_violations - previous_violations
                return self.calc_incremental_violations_merge_stretch(solution.work_stretches[employee_id],
                                                                      rule_parameter=employee_parameter,
                                                                      start_index_1=-solution.historical_work_stretch[
                                                                          employee_id], start_index_2=d_index + 1)
            else:
                return 1 if solution.work_stretches[employee_id][
                                d_index + 1]['length'] >= employee_parameter \
                    else 0

        # check if not the first day and the day before working
        elif not d_index == 0 \
                and solution.check_if_working_day(employee_id, d_index - 1):
            start_index = self.find_work_stretch_end(solution, employee_id, d_index - 1)
            # check if the length of the new work stretch is too long
            return 1 if solution.work_stretches[employee_id][start_index]['length'] >= employee_parameter \
                else 0

        # if single day
        else:
            # check if d_index is the end of the stretch starting in the history
            if d_index == 0 and solution.historical_work_stretch[employee_id] > 0:
                start_index = -solution.historical_work_stretch[employee_id]
                # check if the length of the new work stretch is too long
                return 1 if solution.work_stretches[employee_id][start_index][
                                'length'] >= employee_parameter \
                    else 0
            else:
                return 0

    def incremental_violations_assigned_to_off(self, solution, change_info):
        employee_parameter = self.parameter_per_employee[change_info['employee_id']]

        # find in what work stretch the d_index is
        for start_index, work_stretch in solution.work_stretches[change_info['employee_id']].items():
            if change_info['d_index'] in range(start_index, work_stretch["end_index"] + 1):
                split_1 = change_info['d_index'] - start_index
                split_2 = work_stretch['end_index'] - change_info['d_index']

                # calculate new violations based on history
                new_violations_1 = np.maximum(split_1 - employee_parameter, 0)

                return -(np.maximum(work_stretch['length'] - employee_parameter, 0)
                         - new_violations_1
                         - np.maximum(split_2 - employee_parameter, 0))

    def calc_incremental_violations_merge_stretch(self, stretch_object_employee, rule_parameter, start_index_1,
                                                  start_index_2):

        previous_violations = np.maximum(
            stretch_object_employee[
                start_index_2]['length'] - rule_parameter, 0) \
                              + np.maximum(
            stretch_object_employee[start_index_1]['length'] - rule_parameter, 0)

        new_violations = np.maximum((stretch_object_employee[
                                         start_index_2]['length']
                                     + stretch_object_employee[start_index_1][
                                         'length'] + 1) - rule_parameter, 0)
        return new_violations - previous_violations

    def find_stretch(self, stretch_object_employee, d_index):
        s_index_to_return = None
        for s_index, work_stretch in stretch_object_employee.items():
            if d_index in range(s_index, work_stretch['end_index'] + 1):
                s_index_to_return = s_index

        return s_index_to_return

    def update_information_swap(self, solution, swap_info, stretch_name):
        """
        function to update the information collected
        """
        solution.work_stretches = swap_info['{}_new'.format(stretch_name)]

        return solution

    def collect_new_stretches(self, solution, stretch_object, swap_info, stretch_name):
        # adjust stretches for edges
        stretch_object_copy = self.update_edge_stretches(solution,
                                                         stretch_object,
                                                         swap_info, stretch_name)
        # swap stretches inside
        stretch_object_copy = self.swap_stretches(swap_info, stretch_object_copy, stretch_name)
        pprint.pprint(stretch_object_copy)
        return stretch_object_copy

    def incremental_violations_swap(self, solution, swap_info, rule_id):
        """
        Function to calculate the incremental violations after a swap operation
        """
        if rule_id == "S2Max":
            stretch_name = 'work_stretches'
            stretch_object = solution.work_stretches
        incremental_violations = -1
        # for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
        #     old_violations = self.count_violations_employee(stretch_object[employee_id], employee_id)
        #     new_violations = self.count_violations_employee(swap_info['{}_new'.format(stretch_name)][employee_id],
        #                                                     employee_id)
        #     incremental_violations += new_violations - old_violations
        return incremental_violations

    def swap_stretches(self, swap_info, stretch_object, stretch_name):
        """
        Function to swap the information of the stretches between two employees
        that are affected by the swap operation
        """
        # TODO change such that effected stretches are not affected again
        for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
            # remove the keys that are in the swapped days
            stretch_object[employee_id] = {k: stretch_object[employee_id][k] for k in
                                           set(stretch_object[employee_id]) - set(
                                               swap_info["{}_{}".format(stretch_name, i + 1)])}

            # add key, value pairs that are in the day range of the other nurses
            stretch_object[employee_id].update(swap_info["{}_{}".format(stretch_name, 2 - i)])

        return stretch_object

    def update_edge_stretches(self, solution, stretch_object, swap_info, stretch_name):
        stretch_object_copy = deepcopy(stretch_object)
        employee_id_1 = swap_info['employee_id_1']
        employee_id_2 = swap_info['employee_id_2']
        overlapping = swap_info['overlapping_{}'.format(stretch_name)]
        if not overlapping[employee_id_1] and not overlapping[employee_id_2]:
            stretch_object_copy = self.update_none_overlapping(solution, stretch_object_copy, employee_id_1,
                                                               employee_id_2,
                                                               swap_info['edge_{}'.format(stretch_name)][employee_id_1],
                                                               swap_info['edge_{}'.format(stretch_name)][employee_id_2],
                                                               start_index=swap_info['start_index'],
                                                               end_index=swap_info['end_index'])
        elif overlapping[employee_id_1] and not overlapping[employee_id_2]:
            stretch_object_copy = self.update_overlapping_non_overlapping(solution, stretch_object_copy,
                                                                          overlapping_employee=employee_id_1,
                                                                          other_employee=employee_id_2,
                                                                          overlapping_stretch=overlapping[
                                                                              employee_id_1],
                                                                          edge_stretches_other=
                                                                          swap_info['edge_{}'.format(stretch_name)][
                                                                              employee_id_2],
                                                                          start_index=swap_info['start_index'],
                                                                          end_index=swap_info['end_index'])
        elif not overlapping[employee_id_1] and overlapping[employee_id_2]:
            stretch_object_copy = self.update_overlapping_non_overlapping(solution, stretch_object_copy,
                                                                          overlapping_employee=employee_id_2,
                                                                          other_employee=employee_id_1,
                                                                          overlapping_stretch=overlapping[
                                                                              employee_id_2],
                                                                          edge_stretches_other=
                                                                          swap_info['edge_{}'.format(stretch_name)][
                                                                              employee_id_1],
                                                                          start_index=swap_info['start_index'],
                                                                          end_index=swap_info['end_index'])
        # both overlapping
        else:
            pass
        pprint.pprint(stretch_object_copy)
        return stretch_object_copy

    def update_none_overlapping(self, solution, stretch_object_copy, employee_1,
                                employee_2,
                                edge_stretches_1,
                                edge_stretches_2,
                                start_index,
                                end_index):
        print(stretch_object_copy)
        stretch_object_copy = self.update_none_overlapping_start(solution, stretch_object_copy, employee_1,
                                                                 employee_2,
                                                                 edge_stretches_1['start'],
                                                                 edge_stretches_2['start'],
                                                                 start_index)

        stretch_object_copy = self.update_none_overlapping_end(solution,
                                                               stretch_object_copy,
                                                               employee_1,
                                                               employee_2,
                                                               edge_stretches_1['end'],
                                                               edge_stretches_2['end'],
                                                               end_index)
        pprint.pprint(stretch_object_copy)
        return stretch_object_copy

    def update_none_overlapping_end(self, solution, stretch_object_copy, employee_1,
                                    employee_2,
                                    edge_stretch_end_1,
                                    edge_stretch_end_2,
                                    end_index):
        if edge_stretch_end_1 and edge_stretch_end_2:
            if edge_stretch_end_1['start_index'] != edge_stretch_end_2['start_index']:
                stretch_object_copy[employee_1] = self.shorten_stretch_pre(stretch_object_copy[employee_1],
                                                                           old_start=edge_stretch_end_1['start_index'],
                                                                           new_start=edge_stretch_end_2['start_index'])
                stretch_object_copy[employee_2] = self.shorten_stretch_pre(stretch_object_copy[employee_2],
                                                                           old_start=edge_stretch_end_2['start_index'],
                                                                           new_start=edge_stretch_end_1['start_index'])
        elif edge_stretch_end_1:
            stretch_object_copy = self.update_none_overlapping_end_one_edge(solution,
                                                                            stretch_object_copy,
                                                                            employee_1,
                                                                            employee_2,
                                                                            edge_stretch_end_1,
                                                                            end_index)
        elif edge_stretch_end_2:
            stretch_object_copy = self.update_none_overlapping_end_one_edge(solution,
                                                                            stretch_object_copy,
                                                                            employee_2,
                                                                            employee_1,
                                                                            edge_stretch_end_2,
                                                                            end_index)
            for key in stretch_object_copy[employee_1].keys():
                print(key)
        return stretch_object_copy

    def update_none_overlapping_end_one_edge(self, solution, stretch_object_copy,
                                             employee,
                                             other_employee,
                                             edge_stretch_end,
                                             end_index
                                             ):
        stretch_object_copy[employee] = self.shorten_stretch_pre(stretch_object_copy[employee],
                                                                 old_start=edge_stretch_end['start_index'],
                                                                 new_start=end_index + 1)
        for key in stretch_object_copy[other_employee].keys():
            print(key)

        if end_index + 1 in stretch_object_copy[other_employee]:
            stretch_object_copy[other_employee] = self.shorten_stretch_pre(stretch_object_copy[other_employee],
                                                                           old_start=end_index + 1,
                                                                           new_start=edge_stretch_end['start_index'])
            print("createed_stretch", stretch_object_copy[other_employee][edge_stretch_end['start_index']])
        else:
            stretch_object_copy[other_employee] = solution.create_stretch(stretch_object_copy[other_employee],
                                                                          start_index=edge_stretch_end['start_index'],
                                                                          end_index=end_index)

        return stretch_object_copy

    def update_none_overlapping_start(self, solution, stretch_object_copy, employee_1,
                                      employee_2,
                                      edge_stretch_start_1,
                                      edge_stretch_start_2,
                                      start_index):
        if edge_stretch_start_1 and edge_stretch_start_2:
            stretch_object_copy[employee_1] = self.shorten_stretch_end(stretch_object_copy[employee_1],
                                                                       edge_stretch_start_1['start_index'],
                                                                       edge_stretch_start_2['end_index'])
            stretch_object_copy[employee_2] = self.shorten_stretch_end(stretch_object_copy[employee_2],
                                                                       edge_stretch_start_2['start_index'],
                                                                       edge_stretch_start_1['end_index'])
        elif edge_stretch_start_1:
            stretch_object_copy = self.update_none_overlapping_start_one_edge(solution, stretch_object_copy,
                                                                              employee_1,
                                                                              employee_2,
                                                                              edge_stretch_start_1,
                                                                              start_index
                                                                              )
        elif edge_stretch_start_2:
            stretch_object_copy = self.update_none_overlapping_start_one_edge(solution, stretch_object_copy,
                                                                              employee_2,
                                                                              employee_1,
                                                                              edge_stretch_start_2,
                                                                              start_index
                                                                              )
        return stretch_object_copy

    def update_none_overlapping_start_one_edge(self, solution, stretch_object_copy,
                                               employee,
                                               other_employee,
                                               edge_stretch_start,
                                               start_index
                                               ):
        # remove edge stretch, which is not replace
        stretch_object_copy[employee] = self.shorten_stretch_end(stretch_object_copy[employee],
                                                                 edge_stretch_start['start_index'],
                                                                 start_index - 1)
        start_index_before = self.find_stretch(stretch_object_copy[other_employee], start_index - 1)
        # see if working stretch before the new stretch
        if start_index_before is not None:
            stretch_object_copy[other_employee] = self.shorten_stretch_end(stretch_object_copy[other_employee],
                                                                           start_index_before,
                                                                           edge_stretch_start['end_index'])

        else:
            stretch_object_copy[other_employee] = solution.create_stretch(stretch_object_copy[other_employee],
                                                                          start_index=start_index,
                                                                          end_index=edge_stretch_start['end_index'])

        return stretch_object_copy

    def update_overlapping_non_overlapping(self, solution, stretch_object_copy, overlapping_employee,
                                           other_employee,
                                           overlapping_stretch,
                                           edge_stretches_other,
                                           start_index,
                                           end_index):

        stretch_object_copy[overlapping_employee] = self.update_overlapping_employee(solution,
                                                                                     stretch_object_copy[
                                                                                         overlapping_employee],
                                                                                     overlapping_stretch,
                                                                                     edge_stretches_other,
                                                                                     start_index,
                                                                                     end_index)

        stretch_object_copy[other_employee] = self.update_non_overlapping_employee(stretch_object_copy[other_employee],
                                                                                   edge_stretches_other,
                                                                                   start_index,
                                                                                   end_index)

        return stretch_object_copy

    def update_overlapping_employee(self, solution, stretch_object_employee,
                                    overlapping_stretch,
                                    edge_stretches_other,
                                    start_index,
                                    end_index):
        if overlapping_stretch['start_index'] < start_index \
                and overlapping_stretch['end_index'] > end_index:
            stretch_object_employee = self.update_overlapping_start_end(solution,
                                                                        stretch_object_employee,
                                                                        overlapping_stretch,
                                                                        edge_stretches_other['start'],
                                                                        edge_stretches_other['end'],
                                                                        start_index,
                                                                        end_index)
        elif overlapping_stretch['start_index'] < start_index:
            stretch_object_employee = self.update_overlapping_start(stretch_object_employee,
                                                                    overlapping_stretch,
                                                                    edge_stretches_other['start'],
                                                                    edge_stretches_other['end'],
                                                                    start_index,
                                                                    end_index)
        elif overlapping_stretch['end_index'] > end_index:
            stretch_object_employee = self.update_overlapping_end(stretch_object_employee,
                                                                  overlapping_stretch,
                                                                  edge_stretches_other['start'],
                                                                  edge_stretches_other['end'],
                                                                  start_index,
                                                                  end_index)
        else:
            # TODO combine with above option if possible
            stretch_object_employee = self.update_overlapping_no_sides(solution,
                                                                        stretch_object_employee,
                                                                        overlapping_stretch,
                                                                        edge_stretches_other['start'],
                                                                        edge_stretches_other['end'],
                                                                        start_index,
                                                                        end_index)

        return stretch_object_employee

    def update_non_overlapping_employee(self, stretch_object_employee,
                                        edge_stretches_other,
                                        start_index,
                                        end_index):
        # first check whether there are stretches outside the swap to merge with
        if edge_stretches_other['end'] and edge_stretches_other['end']['length'] > 1:
            end_stretch_starting_index_to_combine = edge_stretches_other['end']['start_index']
        elif end_index + 1 in stretch_object_employee:
            end_stretch_starting_index_to_combine = end_index + 1
        else:
            end_stretch_starting_index_to_combine = None
            if edge_stretches_other['end'] and edge_stretches_other['end']['length'] == 1:
                del stretch_object_employee[end_index]

        # perform merges
        if edge_stretches_other['start'] and edge_stretches_other['start']['start_index'] < start_index:
            start_stretch_starting_index_to_combine = edge_stretches_other['start']['start_index']
        else:
            start_stretch_starting_index_to_combine = self.find_stretch(stretch_object_employee,
                                                                        d_index=start_index-1)

        if start_stretch_starting_index_to_combine and end_stretch_starting_index_to_combine:
            stretch_object_employee = self.merge_overlapping_with_two_stretches(stretch_object_employee,
                                                                                start_stretch_starting_index_to_combine,
                                                                                end_stretch_starting_index_to_combine)
        elif start_stretch_starting_index_to_combine:
            stretch_object_employee = self.shorten_stretch_end(stretch_object_employee,
                                                               start_index=start_stretch_starting_index_to_combine,
                                                               new_end=end_index)
        elif end_stretch_starting_index_to_combine:
            stretch_object_employee = self.shorten_stretch_pre(stretch_object_employee,
                                                               old_start=end_stretch_starting_index_to_combine,
                                                               new_start=start_index)
        else:
            stretch_object_employee = self.create_stretch(stretch_object_employee,
                                                          start_index=start_index,
                                                          end_index=end_index)
        print("non_overlapping")
        pprint.pprint(stretch_object_employee)
        return stretch_object_employee

    def update_overlapping_start(self, stretch_object_employee,
                                 overlapping_stretch,
                                 start_stretch_other,
                                 end_stretch_other,
                                 start_index,
                                 end_index):
        if start_stretch_other:
            # shorten/ change
            stretch_object_employee = self.shorten_stretch_end(stretch_object_employee,
                                                               overlapping_stretch['start_index'],
                                                               start_stretch_other['end_index'])
        else:
            # shorten / change
            stretch_object_employee = self.shorten_stretch_end(
                stretch_object_employee,
                overlapping_stretch['start_index'],
                start_index - 1)

        if end_stretch_other:
            stretch_object_employee = self.create_stretch(stretch_object_employee,
                                                          start_index=end_stretch_other['start_index'],
                                                          end_index=end_index)

        return stretch_object_employee

    def update_overlapping_end(self, stretch_object_employee,
                               overlapping_stretch,
                               start_stretch_other,
                               end_stretch_other,
                               start_index,
                               end_index):
        if end_stretch_other:
            # shorten/ change
            stretch_object_employee = self.shorten_stretch_pre(stretch_object_employee,
                                                               old_start=overlapping_stretch['start_index'],
                                                               new_start=end_stretch_other['start_index'])
        else:
            # shorten / change
            stretch_object_employee = self.shorten_stretch_pre(stretch_object_employee,
                                                               old_start=overlapping_stretch['start_index'],
                                                               new_start=end_index + 1)
        if start_stretch_other:
            stretch_object_employee = self.create_stretch(stretch_object_employee,
                                                              start_index=start_index,
                                                          end_index=start_stretch_other['end_index'])

        return stretch_object_employee

    def update_overlapping_start_end(self, solution, stretch_object_employee,
                                     overlapping_stretch,
                                     start_stretch_other,
                                     end_stretch_other,
                                     start_index,
                                     end_index):
        # start
        if start_stretch_other:
            # shorten/ change
            stretch_object_employee = self.shorten_stretch_end(
                stretch_object_employee,
                overlapping_stretch['start_index'],
                start_stretch_other['end_index'])
        else:
            # shorten / change
            stretch_object_employee = self.shorten_stretch_end(
                stretch_object_employee,
                overlapping_stretch['start_index'],
                start_index - 1)
        # end
        if end_stretch_other:
            # create stretch with starting index from incoming stretch
            stretch_object_employee = solution.create_stretch(stretch_object_employee,
                                                              start_index=end_stretch_other['start_index'],
                                                              end_index=overlapping_stretch['end_index'])
        else:
            # create stretch with end_index + 1 as starting index
            stretch_object_employee = solution.create_stretch(stretch_object_employee,
                                                              start_index=end_index + 1,
                                                              end_index=overlapping_stretch['end_index'])
        return stretch_object_employee

    def update_overlapping_no_sides(self, solution, stretch_object_employee,
                                     overlapping_stretch,
                                     start_stretch_other,
                                     end_stretch_other,
                                     start_index,
                                     end_index):
        # start
        if start_stretch_other:
            # shorten/ change
            stretch_object_employee = self.create_stretch(
                stretch_object_employee,
                start_index,
                start_stretch_other['end_index'])

        # end
        if end_stretch_other:
            # create stretch with starting index from incoming stretch
            stretch_object_employee = solution.create_stretch(stretch_object_employee,
                                                              start_index=end_stretch_other['start_index'],
                                                              end_index=end_index)

        del stretch_object_employee[start_index]
        return stretch_object_employee

    def merge_stretches_different_objects(self, stretch_object_copy,
                                          stretch_object,
                                          employee_id_1,
                                          employee_id_2,
                                          start_index_1,
                                          start_index_2,
                                          swap_info):

        """
                Function to change a stretch object 1 after merge of two stretches
                """

        stretch_object_copy[employee_id_1][start_index_1] = {
            "length": stretch_object[employee_id_2][
                          start_index_2][
                          'end_index'] - start_index_1 + 1,
            'end_index': stretch_object[employee_id_2][
                start_index_2][
                'end_index']}
        # check whether the stretch is longer than the swap
        if stretch_object[employee_id_2][
            start_index_2]['end_index'] > swap_info['end_index']:
            stretch_object_copy = self.shorten_stretch_pre_copy(stretch_object,
                                                                stretch_object_copy,
                                                                old_start=start_index_2,
                                                                new_start=swap_info['end_index'] + 1)
        else:
            del stretch_object_copy[employee_id_2][start_index_2]

        return stretch_object_copy

    def merge_overlapping_with_two_stretches(self, stretch_object_employee,
                                             start_index_1,
                                             start_index_2):
        stretch_object_employee = self.shorten_stretch_end(stretch_object_employee,
                                                           start_index=start_index_1,
                                                           new_end=stretch_object_employee[start_index_2]['end_index'])

        del stretch_object_employee[start_index_2]

        return stretch_object_employee

    def extend_stretch_pre(self, stretch_object_employee, old_start, new_start):
        # create change key of dictionary

        stretch_object_employee[new_start] = stretch_object_employee[old_start]

        # adjust length
        stretch_object_employee[new_start]['length'] += old_start - new_start

        del stretch_object_employee[old_start]

        return stretch_object_employee

    def extend_stretch_end_copy(self, stretch_object, stretch_object_copy,
                                employee_id_1, employee_id_2,
                                swap_info,
                                start_index):
        stretch_object_copy[employee_id_1][start_index] = stretch_object[employee_id_2][start_index]
        if stretch_object[employee_id_2][start_index]['end_index'] > swap_info['end_index']:
            stretch_object_copy[employee_id_2] = self.shorten_stretch_pre_copy(stretch_object[employee_id_2],
                                                                               stretch_object_copy[employee_id_2],
                                                                               old_start=start_index,
                                                                               new_start=swap_info['end_index'] + 1)
        else:
            del stretch_object_copy[employee_id_2]

        return stretch_object_copy

    def extend_stretch_pre_copy(self, stretch_object_employee, stretch_object_copy,
                                old_start, new_start):
        stretch_object_copy[new_start] = stretch_object_employee[old_start]

        # adjust length
        stretch_object_copy[new_start]['length'] += old_start - new_start

        # TODO check if necessary
        if old_start in stretch_object_copy:
            del stretch_object_copy[old_start]

        return stretch_object_copy

    def update_same_day_stretches_end(self, stretch_object, stretch_object_copy,
                                      employee_id_1, employee_id_2,
                                      swap_info, start_index):
        stretch_object_copy[employee_id_1][start_index] = stretch_object[employee_id_2][start_index]

        if start_index in stretch_object_copy:
            del stretch_object_copy[employee_id_2][start_index]

        return stretch_object_copy

    def shorten_stretch_pre_copy(self, stretch_object_employee, stretch_object_copy,
                                 old_start, new_start):

        # change start index of old key
        stretch_object_copy[new_start] \
            = stretch_object_employee[old_start]
        # change the length of the stretch
        stretch_object_copy[new_start]['length'] = new_start - stretch_object_employee[old_start]['end_index'] + 1

        if old_start in stretch_object_copy:
            del stretch_object_copy[old_start]

        return stretch_object_employee

    def shorten_stretch_pre(self, stretch_object_employee, old_start, new_start):
        """
        Function to create key pair for new stretch and remove old stretch
        """
        if stretch_object_employee[old_start]['end_index'] - new_start + 1 > 0:
            # change start index of old key
            stretch_object_employee[new_start] \
                = stretch_object_employee[old_start]
            # change the length of the stretch
            stretch_object_employee[new_start]['length'] = stretch_object_employee[new_start]['end_index'] - new_start + 1
        del stretch_object_employee[old_start]
        print("in shorten", stretch_object_employee)
        return stretch_object_employee

    def merge_stretches(self, stretch_object_employee, start_index_1, start_index_2):
        """
        Function to update solution after merge of two stretches
        """
        # replace end_index of new work stretch with last
        stretch_object_employee[
            start_index_1][
            "end_index"] \
            = stretch_object_employee[
            start_index_2][
            'end_index'
        ]
        # compute new length
        stretch_object_employee[
            start_index_1][
            "length"] \
            += stretch_object_employee[
                   start_index_2]['length'] + 1

        # remove unnecessary stretch
        stretch_object_employee.pop(start_index_2)

        return stretch_object_employee

    def shorten_stretch_end(self, stretch_object_copy, start_index, new_end):
        # function to shorten a stretch
        if new_end < start_index:
            del stretch_object_copy[start_index]
        else:
            stretch_object_copy[start_index]['length'] = new_end - start_index + 1
            stretch_object_copy[start_index]['end_index'] = new_end

        return stretch_object_copy

    def split_stretch(self, stretch_object_employee, start_index_1, d_index):
        """
        Function to split stretch in two different stretches
        """
        # add new key value for second new work stretch
        stretch_object_employee[d_index + 1] \
            = {
            'end_index': stretch_object_employee[
                start_index_1]['end_index'],
            'length': stretch_object_employee[
                          start_index_1]['end_index'] - d_index
        }

        # change end index and length of first new work stretch
        stretch_object_employee[start_index_1]['end_index'] \
            = d_index - 1
        stretch_object_employee[start_index_1]['length'] \
            = d_index - start_index_1

        return stretch_object_employee

    def find_work_stretch_end(self, solution, employee_id, d_index):
        """
        Find key of work stretch given that d_index is the last day
        """
        for s_index, work_stretch in solution.work_stretches[employee_id].items():
            if work_stretch['end_index'] == d_index:
                return s_index

    def find_work_stretch_middle(self, solution, employee_id, d_index):
        """
       Find key of work stretch given that d_index is the middle day
       """
        for s_index, work_stretch in solution.work_stretches[employee_id].items():
            if d_index in range(s_index + 1, work_stretch['end_index']):
                return s_index

    def check_length(self, stretch_object):
        for stretch_employee in stretch_object.values():
            for stretch in stretch_employee.values():
                print(stretch)
                if stretch['length'] < 0:
                    print("length negative")
                    break

    def create_stretch(self, stretch_object_employee, start_index, end_index):
        stretch_object_employee[start_index] = {"end_index": end_index,
                                                "length": end_index - start_index + 1}
        return stretch_object_employee

    # def update_stretch_incoming(self, solution, stretch_object, swap_info):
    #     """
    #     Update the stretches for the incoming swap from the other employee's assignments
    #     if no upcoming stretch, shorten the existing stretch
    #     """
    #     stretch_object_copy = deepcopy(stretch_object)
    #     stretch_object_copy = self.update_stretch_incoming_start(solution, stretch_object, stretch_object_copy,
    #                                                              swap_info)
    #     self.check_length(stretch_object_copy)
    #     stretch_object_copy = self.update_stretch_incoming_end(solution, stretch_object, stretch_object_copy, swap_info)
    #
    #     return stretch_object_copy
    #
    # # def remove_left_over_stretches(self, stretch_object_copy, swap_info):
    # #     # check if there are starting indices left to remove
    # #     for employee_id in [swap_info['employee_id_1'], swap_info['employee_id_2']]:
    # #         if swap_info['start_index']

    # def update_stretch_incoming_end(self, solution, stretch_object, stretch_object_copy, swap_info):
    #     """
    #     Function to update stretches on the end of the swap
    #     """
    #     for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
    #         other_employee_id = swap_info['employee_id_{}'.format(2 - i)]
    #
    #         # merge incoming and present stretch
    #         if solution.check_if_working_day(employee_id, swap_info['end_index'] + 1) \
    #                 and solution.check_if_working_day(other_employee_id, swap_info['end_index']):
    #             start_index_1 = self.find_stretch(stretch_object[employee_id], swap_info['end_index'] + 1)
    #             start_index_2 = self.find_stretch(stretch_object[other_employee_id], swap_info['end_index'])
    #             stretch_object_copy[employee_id] = self.extend_stretch_pre_copy(stretch_object[employee_id],
    #                                                                             stretch_object_copy[employee_id],
    #                                                                             old_start=start_index_1,
    #                                                                             new_start=start_index_2)
    #         # check if old stretch over border is unmatched
    #         elif solution.check_if_working_day(employee_id, swap_info['end_index']) \
    #                 and solution.check_if_working_day(employee_id, swap_info['end_index'] + 1):
    #             start_index = self.find_stretch(stretch_object[employee_id], swap_info['end_index'])
    #             stretch_object_copy[employee_id] = self.shorten_stretch_pre_copy(stretch_object[employee_id],
    #                                                                              stretch_object_copy[employee_id],
    #                                                                              old_start=start_index,
    #                                                                              new_start=swap_info['end_index'] + 1)
    #         # check if both incoming and present on the same day
    #         elif solution.check_if_working_day(employee_id, swap_info['end_index']) \
    #                 and solution.check_if_working_day(other_employee_id, swap_info['end_index']):
    #             start_index_2 = self.find_stretch(stretch_object[other_employee_id], swap_info['end_index'])
    #             stretch_object_copy = self.update_same_day_stretches_end(stretch_object,
    #                                                                      stretch_object_copy,
    #                                                                      employee_id,
    #                                                                      other_employee_id,
    #                                                                      swap_info,
    #                                                                      start_index_2)
    #         # check if incoming stretch unmatched
    #         elif solution.check_if_working_day(other_employee_id, swap_info['end_index']):
    #             start_index = self.find_stretch(stretch_object[other_employee_id], swap_info['end_index'])
    #             stretch_object_copy[employee_id] = solution.create_stretch(stretch_object_copy[employee_id],
    #                                                                        start_index=start_index,
    #                                                                        end_index=swap_info['end_index'])
    #
    #         # check remove outgoing stretch
    #         elif solution.check_if_working_day(other_employee_id, swap_info['end_index']):
    #             start_index = self.find_stretch(stretch_object[employee_id], swap_info['end_index'])
    #             del stretch_object_copy[employee_id][start_index]
    #
    #     return stretch_object_copy

    # def update_stretch_incoming_start(self, solution, stretch_object, stretch_object_copy, swap_info):
    #     print("update)_start")
    #     for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
    #         other_employee_id = swap_info['employee_id_{}'.format(2 - i)]
    #
    #         # check if first day
    #         if swap_info['start_index'] == 0:
    #             # check if a stretch should be merged
    #             if solution.historical_work_stretch[employee_id] > 0 and solution.check_if_working_day(
    #                     other_employee_id,
    #                     swap_info[
    #                         'start_index']):
    #                 start_index_2 = self.find_stretch(stretch_object[other_employee_id], swap_info['start_index'])
    #                 stretch_object_copy = self.merge_stretches_different_objects(stretch_object_copy,
    #                                                                              stretch_object,
    #                                                                              employee_id,
    #                                                                              other_employee_id,
    #                                                                              -solution.historical_work_stretch[
    #                                                                                  employee_id],
    #                                                                              start_index_2,
    #                                                                              swap_info)
    #             # check if stretch is unmatched by other employee
    #             elif solution.historical_work_stretch[employee_id] > 0 and solution.check_if_working_day(employee_id,
    #                                                                                                      swap_info[
    #                                                                                                          'start_index']):
    #                 stretch_object_copy[employee_id] = self.shorten_stretch_end(
    #                     stretch_object[employee_id],
    #                     stretch_object_copy[employee_id],
    #                     -solution.historical_work_stretch[employee_id],
    #                     new_end=-1)
    #             # check if both start on the start index and not working before
    #             elif solution.check_if_working_day(employee_id, swap_info['start_index']) \
    #                     and solution.check_if_working_day(other_employee_id, swap_info['start_index']):
    #                 stretch_object_copy = self.extend_stretch_end_copy(stretch_object, stretch_object_copy,
    #                                                                    employee_id, other_employee_id,
    #                                                                    swap_info, swap_info['start_index'])
    #
    #             # check if other employees stretch is unmatched
    #             elif solution.check_if_working_day(other_employee_id, swap_info['start_index']):
    #                 start_index_2 = self.find_stretch(stretch_object[other_employee_id], swap_info['start_index'])
    #                 stretch_object_copy[employee_id] \
    #                     = solution.create_stretch(stretch_object_copy,
    #                                               start_index=swap_info['start_index'],
    #                                               end_index=stretch_object[other_employee_id][start_index_2][
    #                                                   'end_index'])
    #             elif solution.check_if_working_day(employee_id, swap_info['start_index']):
    #                 del stretch_object_copy[employee_id]['start_index']
    #
    #         else:
    #             # check if stretch of one employee is matched with the other employee
    #             if solution.check_if_working_day(employee_id, swap_info['start_index'] - 1) \
    #                     and solution.check_if_working_day(other_employee_id, swap_info['start_index']):
    #                 start_index_1 = self.find_stretch(stretch_object[employee_id], swap_info['start_index'] - 1)
    #                 start_index_2 = self.find_stretch(stretch_object[other_employee_id], swap_info['start_index'])
    #
    #                 stretch_object_copy = self.merge_stretches_different_objects(stretch_object_copy,
    #                                                                              stretch_object,
    #                                                                              employee_id,
    #                                                                              other_employee_id,
    #                                                                              start_index_1,
    #                                                                              start_index_2,
    #                                                                              swap_info)
    #             # check if stretch of employee is unmatched with other employees
    #             elif solution.check_if_working_day(employee_id, swap_info['start_index'] - 1) \
    #                     and solution.check_if_working_day(employee_id, swap_info['start_index']):
    #                 start_index = self.find_stretch(stretch_object[employee_id],
    #                                                 swap_info['start_index'] - 1)
    #                 stretch_object_copy[employee_id] = self.shorten_stretch_end(
    #                     stretch_object[employee_id],
    #                     stretch_object_copy[employee_id],
    #                     start_index,
    #                     new_end=swap_info['start_index'] - 1)
    #             # check if both start on the start index and not working before
    #             elif solution.check_if_working_day(employee_id, swap_info['start_index']) \
    #                     and solution.check_if_working_day(other_employee_id, swap_info['start_index']):
    #                 stretch_object_copy = self.extend_stretch_end_copy(stretch_object, stretch_object_copy,
    #                                                                    employee_id, other_employee_id,
    #                                                                    swap_info, swap_info['start_index'])
    #             # check if other employee's stretch is unmatched
    #             elif solution.check_if_working_day(other_employee_id, swap_info['start_index']):
    #                 start_index_2 = self.find_stretch(stretch_object[other_employee_id], swap_info['start_index'])
    #                 stretch_object_copy[employee_id] \
    #                     = solution.create_stretch(stretch_object_copy[employee_id],
    #                                               start_index=swap_info['start_index'],
    #                                               end_index=stretch_object[other_employee_id][start_index_2][
    #                                                   'end_index'])
    #             elif solution.check_if_working_day(employee_id, swap_info['start_index']):
    #                 del stretch_object_copy[employee_id][swap_info['start_index']]
    #
    #     return stretch_object_copy

    # def enumerate_employee(self, swap_info):
    #     for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
    #         yield i, employee_id

    # def update_stretch_outgoing(self, solution, stretch_object, swap_info):
    #     # TODO only change stretches that are not going to be changed by incoming
    #     for i, employee_id in enumerate([swap_info['employee_id_1'], swap_info['employee_id_2']]):
    #         # check start_day
    #         # if both days working
    #         if swap_info['start_index'] == 0:
    #             if solution.historical_work_stretch[employee_id] > 0 and solution.check_if_working_day(employee_id,
    #                                                                                                    swap_info[
    #                                                                                                        'start_index']):
    #                 stretch_object[employee_id] = self.shorten_stretch_end(
    #                     stretch_object[employee_id],
    #                     stretch_object[employee_id],
    #                     -solution.historical_work_stretch[employee_id],
    #                     new_end=-1)
    #         else:
    #             if solution.check_if_working_day(employee_id, swap_info['start_index'] - 1) \
    #                     and solution.check_if_working_day(employee_id, swap_info['start_index']):
    #                 start_index = self.find_stretch(stretch_object[employee_id],
    #                                                 swap_info['start_index'] - 1)
    #                 stretch_object[employee_id] = self.shorten_stretch_end(
    #                     stretch_object[employee_id],
    #                     stretch_object[employee_id],
    #                     start_index,
    #                     new_end=swap_info['start_index'] - 1)
    #
    #         # check whether stretch around the end index is split up
    #         if solution.check_if_working_day(employee_id, swap_info['end_index']) \
    #                 and solution.check_if_working_day(employee_id, swap_info['end_index'] + 1):
    #             start_index = self.find_stretch(stretch_object[employee_id],
    #                                             swap_info['end_index'])
    #             stretch_object[employee_id] = self.shorten_stretch_pre(
    #                 stretch_object[employee_id],
    #                 stretch_object[employee_id][start_index]['end_index'],
    #                 new_start=swap_info['end_index'] + 1
    #             )
    #
    #     return stretch_object
