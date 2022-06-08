import numpy as np
import itertools
from invoke.Solutions.solution import Solution
from invoke.Domain.employee import EmployeeCollection
from invoke.Rules.RuleS7 import RuleS7
from invoke.Rules.RuleS2Max import RuleS2Max
from copy import deepcopy

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
        self.num_shift_types = scenario.num_shift_types
        self.employee_preferences = scenario.employee_preferences

        # set parameter
        self.k_swap = scenario.stage_settings['heuristic_settings']['k_swap']

        if previous_solution:
            self.shift_assignments = previous_solution.shift_assignments
            self.diff_min_request = previous_solution.diff_min_request
            self.working_days = previous_solution.working_days

        else:
            if scenario.stage_settings['stage_number'] == 1 and scenario.stage_settings['ref_as_initial']:
                self.shift_assignments = deepcopy(scenario.ref_assignments)
            else:
                # initialize shift assignment objects
                self.shift_assignments = self.create_shift_assignments()

                # assign skill requests based on H1, H2 and H4
                self.assign_skill_requests()
            # ALWAYS
            #H2 create array to keep track of difference between optimal skill_requests and actual skill assignment
            self.diff_min_request = self.initialize_diff_min_request(self.scenario)

            # collect working days
            self.working_days = self.collect_working_days(self.scenario)

        # H3 forbidden successions
        self.forbidden_shift_type_successions = scenario.forbidden_shift_type_successions
        self.last_assigned_shift = scenario.last_assigned_shift

        # S1 create array to keep track of difference between optimal skill_requests and actual skill assignment
        if 'S1' in self.rules:
            self.diff_opt_request = self.initialize_diff_opt_request(self.scenario)

        # S2 collect work stretches
        if 'S2Max' in self.rules:
            self.last_assigned_shift = scenario.last_assigned_shift
            self.historical_work_stretch = scenario.historical_work_stretch
            self.work_stretches = self.collect_work_stretches(solution=self)

        # S2Shift collect shift stretches
        if 'S2ShiftMax' in self.rules:
            self.historical_shift_stretch = scenario.historical_shift_stretch
            self.shift_stretches = self.collect_shift_stretches(solution=self)

        # S3 collect day off stretches
        if 'S3Max' in self.rules:
            self.historical_off_stretch = scenario.historical_off_stretch
            self.day_off_stretches = self.collect_day_off_stretches(solution=self)

        # S6 collect number of assignments per nurse
        if 'S6Max' in self.rules:
            self.num_assignments_per_nurse = self.get_num_assignments_per_nurse()

        # S7 collect number of working weekends per nurse
        if 'S7' in self.rules:
            self.num_working_weekends = RuleS7().count_working_weekends_employee(
                solution=self,
                scenario=self.scenario)

        # S7Day collect reference day comparison
        if 'S7Day' in self.rules:
            self.day_comparison = self.collect_day_within_comparison(solution=self)

        # S7Shift
        if 'S7Shift' in self.rules:
            self.shift_comparison = self.collect_shift_comparison_within(solution=self)
        if 'S8RefDay' in self.rules or 'S8RefShift' in self.rules or 'S8RefSkill' in self.rules:
            self.ref_assignments = scenario.ref_assignments
        if 'S8RefDay' in self.rules:
            self.ref_comparison_day_level = self.collect_day_comparison_ref(solution=self)

        if 'S8RefShift' in self.rules:
            self.ref_comparison_shift_level = self.collect_shift_comparison_ref(solution=self)

        if 'S8RefSkill' in self.rules:
            self.multi_skill = scenario.multi_skill
            self.ref_comparison_skill_level = self.collect_skill_comparison_ref(solution=self)

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
        return self.collect_assignments(scenario) - scenario.optimal_coverage

    def collect_assignments(self, scenario):
        skill_assignments = np.zeros((scenario.num_days_in_horizon,
                                  scenario.skill_collection.num_skills,
                                  scenario.num_shift_types))
        for employee_id in scenario.employees._collection.keys():
            for d_index in range(scenario.num_days_in_horizon):
                skill_assignments[
                    d_index,
                    self.shift_assignments[employee_id][d_index][1],
                    self.shift_assignments[employee_id][d_index][0]
                ] += 1 if self.shift_assignments[employee_id][d_index][0] >= 0 else 0

        return skill_assignments

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
            shift_assignments[employee_id] = np.full((self.scenario.num_days_in_horizon, 2), -1, dtype=int)

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

    def collect_working_days(self, scenario):
        working_days = {}
        for employee_id in scenario.employees._collection.keys():
            working_days_employee = []
            for d_index in range(0, scenario.num_days_in_horizon):
                if self.check_if_working_day(employee_id, d_index):
                    working_days_employee.append(d_index)

            working_days[employee_id] = working_days_employee

        return working_days

    def collect_work_stretches(self, solution):
        """
        Function to collect for each nurse the stretches of consecutive
        working days or days off
        """
        work_stretches = {}
        for employee_id in self.scenario.employees._collection.keys():

            # for each working day, get check if employee is working
            working_check = [1 if solution.check_if_working_day(employee_id, d_index) else 0
                                for d_index in range(self.scenario.num_days_in_horizon)]

            work_stretch_employee = self.collect_stretches(working_check)

            # implement history
            if self.historical_work_stretch[employee_id] > 0:
                if 0 in work_stretch_employee:
                    # combine history stretch with first day stretch
                    work_stretch_employee = RuleS2Max().extend_stretch_pre(
                        stretch_object_employee=work_stretch_employee,
                        new_start=-self.historical_work_stretch[employee_id],
                        old_start=0)
                else:
                    # add new stretch to history
                    work_stretch_employee = solution.create_stretch(
                        stretch_object_employee=work_stretch_employee,
                        start_index=-self.historical_work_stretch[employee_id],
                        end_index=-1)
            work_stretches[employee_id] = work_stretch_employee

        return work_stretches

    def collect_work_stretches_employee(self, solution, employee_id):
        # for each working day, get check if employee is working
        working_check = [1 if solution.check_if_working_day(employee_id, d_index) else 0
                         for d_index in range(self.scenario.num_days_in_horizon)]

        work_stretch_employee = self.collect_stretches(working_check)

        # implement history
        if self.historical_work_stretch[employee_id] > 0:
            if 0 in work_stretch_employee:
                # combine history stretch with first day stretch
                work_stretch_employee = RuleS2Max().extend_stretch_pre(
                    stretch_object_employee=work_stretch_employee,
                    new_start=-self.historical_work_stretch[employee_id],
                    old_start=0)
            else:
                # add new stretch to history
                work_stretch_employee = solution.create_stretch(
                    stretch_object_employee=work_stretch_employee,
                    start_index=-self.historical_work_stretch[employee_id],
                    end_index=-1)

        return work_stretch_employee

    def collect_day_off_stretches(self, solution):
        """
        Collect streaks of days off for all employees
        """
        day_off_stretches = {}
        for employee_id in self.scenario.employees._collection.keys():

            day_off_check = [1 if not solution.check_if_working_day(employee_id, d_index) else 0
                             for d_index in range(self.scenario.num_days_in_horizon)]

            day_off_stretch_employee = self.collect_stretches(day_off_check)

            day_off_stretches[employee_id] = day_off_stretch_employee

            # implement history
            if self.historical_off_stretch[employee_id] > 0:
                if 0 in day_off_stretch_employee:
                    # combine history stretch with first day stretch
                    day_off_stretch_employee = RuleS2Max().extend_stretch_pre(
                        stretch_object_employee=day_off_stretch_employee,
                        new_start=-self.historical_off_stretch[employee_id],
                        old_start=0)
                else:
                    # add new stretch to history
                    day_off_stretch_employee = solution.create_stretch(
                        stretch_object_employee=day_off_stretch_employee,
                        start_index=-self.historical_off_stretch[employee_id],
                        end_index=-1)
            day_off_stretches[employee_id] = day_off_stretch_employee

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
        for s_index in self.scenario.shift_collection.shift_types_indices:
            shift_stretch_shift = {}
            for employee_id in self.scenario.employees._collection.keys():


                # for each working day, check if employee works that shift type

                working_shift_check = [1 if solution.check_if_working_s_type_on_day(employee_id, d_index, s_index)
                                 else 0
                                 for d_index in range(self.scenario.num_days_in_horizon)]

                shift_stretch_shift_employee = self.collect_stretches(working_shift_check)

                # implement history
                if self.last_assigned_shift[employee_id] == s_index:
                    if 0 in shift_stretch_shift_employee:
                        # combine history stretch with first day stretch
                        shift_stretch_shift_employee = RuleS2Max().extend_stretch_pre(
                            stretch_object_employee=shift_stretch_shift_employee,
                            new_start=-self.historical_shift_stretch[employee_id],
                            old_start=0)
                    else:
                        # add new stretch to history
                        shift_stretch_shift_employee = solution.create_stretch(
                            stretch_object_employee=shift_stretch_shift_employee,
                            start_index=-self.historical_shift_stretch[employee_id],
                            end_index=-1)

                shift_stretch_shift[employee_id] = shift_stretch_shift_employee

            # add for each employee the stretches to the general dict
            shift_stretches[s_index] = shift_stretch_shift

        return shift_stretches

    def collect_day_within_comparison(self, solution):
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

    def collect_shift_comparison_within(self, solution):
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

    def collect_day_comparison_ref(self, solution):
        """
        Create object with True and False that show whether assignment
        of current day and day in reference are the same
        True if assigned on both days
        False if assigned on one of the day
        """

        day_assignment_comparison = {}
        # np.array(len(self.day_collection.num_days_in_horizon))
        for employee_id in self.scenario.employees._collection.keys():
            day_list = [1 if solution.check_if_working_day_ref(employee_id, d_index)
                             == solution.check_if_working_day(employee_id, d_index) else 0
                        for d_index in range(0, self.scenario.day_collection.num_days_in_horizon)]
            # combine into one list
            day_assignment_comparison[employee_id] = np.array(day_list)

        return day_assignment_comparison

    def collect_shift_comparison_ref(self, solution):
        """
        Collect dict where for each employee we have an array
        with:
        1 if working both days and same shift
        0 if working both days and different shift
        -1 if outside of range of comparison or not working both days

        """
        shift_assignment_comparison = {}

        for employee_id in self.scenario.employees._collection.keys():
            shift_comparison_empl = [
                (
                      1 if solution.check_if_same_shift_type_ref(employee_id, d_index) else 0
                )
                if solution.check_if_working_day(
                    employee_id, d_index)
                   and solution.check_if_working_day_ref(employee_id, d_index)
                else -1
                for d_index in range(0, self.scenario.day_collection.num_days_in_horizon)

            ]

            # combine into one dict
            shift_assignment_comparison[employee_id] = np.array(shift_comparison_empl)

        return shift_assignment_comparison

    def collect_skill_comparison_ref(self, solution):
        """
        Collect dict where for each employee we have an array
        with:
        1 if working both days, working the same shift, working the same skill
        0 if working both days, working the same shift, but not the same skill
        -1 if not working either of the days, or working both days but working a different shift
        :return:
        dict
        """
        skill_assignment_comparison = {}

        for employee_id in self.scenario.employees._collection.keys():
            skill_comparison_empl =[]
            for d_index in range(0, self.scenario.day_collection.num_days_in_horizon):
                if self.multi_skill[employee_id]:
                    if solution.check_if_working_day(employee_id, d_index) \
                   and solution.check_if_working_day_ref(employee_id, d_index)\
                    and solution.check_if_same_shift_type_ref(employee_id, d_index):
                        if solution.check_if_same_skill_type_ref(employee_id, d_index):
                            skill_comparison_empl.append(1)
                        else:
                            skill_comparison_empl.append(0)
                    else:
                        skill_comparison_empl.append(-1)
                else:
                    skill_comparison_empl.append(-1)

            # combine into one dict
            skill_assignment_comparison[employee_id] = np.array(skill_comparison_empl)

        return skill_assignment_comparison

