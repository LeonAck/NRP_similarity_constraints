import numpy as np

class Scenario:
    """
    Class to store all the scenario information

    contracts

    forbidden shift type successions
    """

    def __init__(self, settings, instance):
        """
        Initialize parameters
        """
        self.source = settings.source
        # initialize instance data
        self.weeks_data = instance.weeks_data
        self.history_data = instance.history_data
        self.scenario_data = instance.scenario_data
        self.problem_horizon = instance.problem_horizon

        # extract shift type data
        self.shift_types = self.initialize_shift_types()
        self.num_shift_types = len(self.shift_types)

        # extract skill data
        self.skills = self.scenario_data['skills']
        self.num_skills = len(self.skills)
        self.skill_sets = self.initialize_skill_sets()

        # extract skill requets
        self.skill_requests = self.initialize_skill_requests()

        # extract contract information
        self.contract_collection = None

        self.contract_collection = self.collect_contracts()
        self.forbidden_shift_type_successions = None

       # do I want to add skill sets as well?

    def collect_contracts(self):
        """
        Class to store all contracts
        :return:
        dict of contracts
        """
        return None


    def initialize_shift_types(self):
        """
        Class to get shift types in the solution
        """
        return [s_type['id'] for s_type in self.scenario_data['shiftTypes']]

    def initialize_skill_sets(self):
        """
        Function to get present skill sets in scenario
        """
        skills_array = np.array([set['skills'] for set in
                                 self.scenario_data['nurses']], dtype=object)

        return np.unique(skills_array)

    def initialize_skill_requests(self):
        """
        Create array of skill requests
        :return:
        array with dimensions num_days x num_shift_types x num_skill types
        """
        request_array = np.zeros((self.problem_horizon * 7,
                                  self.num_shift_types,
                                  self.num_skills))

        # for value in self.scenario_data.values():
        #     for day, requirement in value.items():
        #         day_index = self.weekday_to_index(
        #             day.removeprefix("requirementOn"))


        return request_array


class Contract:
    """
    Class for the contract that each nurse has
    """

    def __init__(self, input_data):
        """
        Initialize contract parameters
        """
        self.id = None
        self.complete_weekends = None
        self.maximumNumberOfAssignments = None
        self.maximumNumberOfConsecutiveDaysOff = None
        self.maximumNumberOfConsecutiveWorkingDays = None
        self.maximumNumberOfWorkingWeekends = None
        self.minimumNumberOfAssignments = None
        self.minimumNumberOfConsecutiveDaysOff = None
        self.minimumNumberOfConsecutiveWorkingDays = None


class SkillSet:
    """
    Create class to save skill set info
    """

    def __init__(self, id, skills):
        self.id = None
        self.skills = None

        # get id of skills in counter
        self.skill_set_index = None

class ShiftType:
    """
    Class to collect shift type information
    """
