"""
Set to create initial solution
"""
import numpy as np
import itertools
from pprint import pprint
from solution import Solution
from Domain.employee import EmployeeCollection
from Invoke.Constraints.Rules.RuleS6 import RuleS6
from Invoke.Constraints.Rules.RuleS2Max import RuleS2Max


class BuildSolution(Solution):
    """
    Class to create initial solution
    """

    def __init__(self, scenario, previous_solution=None):
        # inherit from parent class
        super().__init__()

        self.scenario = scenario
        self.day_collection = scenario.day_collection
        self.rule_collection = scenario.rule_collection
        self.rules = list(self.rule_collection.collection.keys())

        if previous_solution:
            self.shift_assignments = previous_solution.shift_assignments
        else:
            # initialize shift assignment objects
            self.shift_assignments = self.create_shift_assignments()

            # assign skill requests based on H1, H2 and H4
            self.assign_skill_requests()
        # ALWAYS
        #H2 create array to keep track of difference between optimal skill_requests and actual skill assignment
        self.diff_min_request = self.initialize_diff_min_request(self.scenario)

        # H3 forbidden successions
        self.forbidden_shift_type_successions = scenario.forbidden_shift_type_successions
        self.last_assigned_shifts = scenario.last_assigned_shifts

        # S1 create array to keep track of difference between optimal skill_requests and actual skill assignment
        if 'S1' in self.rules:
            self.diff_opt_request = self.initialize_diff_opt_request(self.scenario)

        # S2 collect work stretches
        if 'S2Max' in self.rules:
            self.historical_working_stretch = scenario.history_working_streak
            self.work_stretches = self.collect_work_stretches(solution=self)


        # S2Shift collect shift stretches
        if 'S2ShiftMax' in self.rules:
            self.shift_stretches = self.collect_shift_stretches(solution=self)

        # S3 collect day off stretches
        if 'S3Max' in self.rules:
            self.day_off_stretches = self.collect_day_off_stretches(solution=self)

        # S5 collect number of assignments per nurse
        if 'S5Max' in self.rules:
            self.num_assignments_per_nurse = self.get_num_assignments_per_nurse()

        # S6 collect number of working weekends per nurse
        if 'S6' in self.rules:
            self.num_working_weekends = RuleS6().count_working_weekends_employee(
                solution=self,
                scenario=self.scenario)

        # S7Day collect reference day comparison
        if 'S7Day' in self.rules:
            self.day_comparison = self.collect_ref_day_comparison(solution=self)

        # S7Shift
        if 'S7Shift' in self.rules:
            self.shift_comparison = self.collect_ref_shift_comparison(solution=self)

        # get violations
        self.violation_array = self.get_violations(self.scenario, self.scenario.rule_collection)

        # calc objective value
        self.obj_value = self.calc_objective_value_violations(
            violation_array=self.violation_array,
            rule_collection=self.scenario.rule_collection)

    def assign_skill_requests(self):
        """
        Function to assign skill request to employees
        """
        # get requests per day
        for day_index, request_per_day in enumerate(self.scenario.skill_requests):
            # create collection of nurses available on day
            employees_available_on_day = EmployeeCollection().initialize_employees(
                self.scenario, self.scenario.employees_specs)

            #  loop through requests per day and per skill
            for skill_index, request_per_day_per_skill in enumerate(request_per_day):

                # create set of employees with skill that are available on that day
                employees_with_skill = employees_available_on_day.get_employee_w_skill(
                    self.scenario.skills[skill_index])

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

    def collect_work_stretches(self, solution):
        """
        Function to collect for each nurse the stretches of consecutive
        working days or days off
        """
        work_stretches = {}
        for employee_id in self.scenario.employees._collection.keys():
            work_stretch_employee = {}
            # for each working day, get check if employee is working
            working_check = [1 if solution.check_if_working_day(employee_id, d_index) else 0
                                for d_index in range(self.scenario.num_days_in_horizon)]

            work_stretch_employee = self.collect_stretches(working_check)

            # implement history
            if self.historical_working_stretch[employee_id] > 0:
                if 0 in work_stretch_employee:
                    # combine history stretch with first day stretch
                    work_stretch_employee = RuleS2Max().extend_stretch_pre(
                        stretch_object_employee=work_stretch_employee,
                        new_start=-self.historical_working_stretch[employee_id],
                        old_start=0)
                else:
                    # add new stretch to history
                    work_stretch_employee = solution.create_work_stretch(
                        stretch_object_employee=work_stretch_employee,
                        start_index=-self.historical_working_stretch[employee_id],
                        end_index=-1)
            work_stretches[employee_id] = work_stretch_employee

        return work_stretches

    def collect_day_off_stretches(self, solution):
        """
        Collect streaks of days off for all employees
        """
        day_off_stretches = {}
        for employee_id in self.scenario.employees._collection.keys():

            day_off_check = [1 if not solution.check_if_working_day(employee_id, d_index) else 0
                             for d_index in range(self.scenario.num_days_in_horizon)]

            day_off_stretch_employee = self.collect_stretches(day_off_check)

            day_off_stretches[employee_id]= day_off_stretch_employee

        return day_off_stretches

    def collect_stretches(self, check_object):
        stretch_object_employee = {}
        start_index = 0
        # get lists of consecutive working days
        for k, v in itertools.groupby(check_object):
            len_stretch = sum(1 for _ in v)
            if k:
                # save in dict under start index with end index
                work_stretch = {}
                work_stretch["end_index"] = start_index + len_stretch - 1
                work_stretch["length"] = len_stretch
                stretch_object_employee[start_index] = work_stretch
                start_index += len_stretch
            else:
                start_index += len_stretch

        return stretch_object_employee

    def collect_shift_stretches(self, solution):
        """
        Function to collect for each employee and each shift type
        the work stretches of that particular shift type
        """
        shift_stretches = {}
        for employee_id in self.scenario.employees._collection.keys():
            shift_stretch_employee = {}
            for s_index in self.scenario.shift_collection.shift_types_indices:
                shift_stretches_employee_per_shift = {}
                # for each working day, check if employee works that shift type

                working_shift_check = [1 if solution.check_if_working_s_type_on_day(employee_id, d_index, s_index)
                                 else 0
                                 for d_index in range(self.scenario.num_days_in_horizon)]

                start_index = 0
                # get lists of consecutive days working specific shift type
                for k, v in itertools.groupby(working_shift_check):
                    len_stretch = sum(1 for _ in v)
                    if k:
                        # save in dict under start index with end index
                        shift_stretch = {}
                        shift_stretch["end_index"] = start_index + len_stretch - 1
                        shift_stretch["length"] = len_stretch
                        shift_stretches_employee_per_shift[start_index] = shift_stretch
                        start_index += len_stretch
                    else:
                        start_index += len_stretch

                # assign for each s_type the stretches to the employee
                shift_stretch_employee[s_index] = shift_stretches_employee_per_shift
            # add for each employee the stretches to the general dict
            shift_stretches[employee_id] = shift_stretch_employee

        return shift_stretches

    def collect_ref_day_comparison(self, solution):
        """
        Create object with True and False that show whether assignment
        of current day and reference day are the same
        True if assigned on both days
        False if assigned on one of the day
        """

        day_assignment_comparison = {}
        rule_parameter = self.scenario.rule_collection.collection['S7Day'].parameter_1
        #np.array(len(self.day_collection.num_days_in_horizon))
        for employee_id in self.scenario.employees._collection.keys():
            day_list = [1 if solution.check_if_working_day(employee_id, d_index-rule_parameter)
                        == solution.check_if_working_day(employee_id, d_index) else 0
                        for d_index in range(0, self.scenario.day_collection.num_days_in_horizon)
                        if d_index - rule_parameter >= 0]
            # combine into one list
            day_assignment_comparison[employee_id] = np.concatenate((np.full(rule_parameter, fill_value=-1), np.array(day_list)))

        return day_assignment_comparison

    def collect_ref_shift_comparison(self, solution):
        """
        Collect dict where for each employee we have an array
        with:
        1 if working both days and same shift
        0 if working both days and different shift
        -1 if outside of range of comparison or not working both days

        """
        shift_assignment_comparison = {}
        rule_parameter = self.scenario.rule_collection.collection['S7Shift'].parameter_1

        for employee_id in self.scenario.employees._collection.keys():
            shift_comparison_empl = [
                (
                    1 if solution.check_if_same_shift_type(
                employee_id, d_index, d_index - rule_parameter) else 0
                )
                if solution.check_if_working_day(
                employee_id, d_index)
                   and solution.check_if_working_day(employee_id, d_index-rule_parameter)
                    else -1
                 for d_index in range(0, self.scenario.day_collection.num_days_in_horizon)
                 if d_index - rule_parameter >= 0
            ]

            # combine into one list
            shift_assignment_comparison[employee_id] = np.concatenate(
                (np.full(rule_parameter, fill_value=-1), np.array( shift_comparison_empl)))

        return shift_assignment_comparison













