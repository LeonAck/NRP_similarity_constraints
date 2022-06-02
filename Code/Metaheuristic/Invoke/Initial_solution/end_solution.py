import numpy as np
from Invoke.Constraints.Rules import RuleS8RefSkill, RuleS8RefDay, RuleS8RefShift
class EndSolution:
    """
       Class to add similarity violations to best solution
       """

    def __init__(self, scenario, previous_solution=None):


        self.best_solution = previous_solution
        self.scenario = scenario
        self.ref_assignments = scenario.ref_assignments

        self.ref_comparison_day_level = self.collect_day_comparison_ref(solution=self.best_solution)

        self.ref_comparison_shift_level = self.collect_shift_comparison_ref(solution=self.best_solution)

        self.multi_skill = scenario.multi_skill
        self.ref_comparison_skill_level = self.collect_skill_comparison_ref(solution=self.best_solution)

        # get violations
        self.violation_array = self.add_similarity_violations()


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

    def add_similarity_violations(self):
        self.best_solution.violation_array.append(RuleS8RefDay().count_violations(self.best_solution, self.scenario))
        self.best_solution.violation_array.append(RuleS8RefShift().count_violations(self.best_solution, self.scenario))
        self.best_solution.violation_array.append(RuleS8RefSkill().count_violations(self.best_solution, self.scenario))

        return self.best_solution.violation_array

