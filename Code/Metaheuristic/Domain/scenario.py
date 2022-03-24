import numpy as np
from Domain.employee import EmployeeCollection
from Domain.skills import SkillCollection
from Domain.skill_set import SkillSetCollection


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
        self.weeks = settings.weeks
        self.history_data = instance.history_data
        self.scenario_data = instance.scenario_data
        self.problem_horizon = instance.problem_horizon

        # extract problem data
        self.num_days_in_horizon = self.problem_horizon * 7

        # extract shift type data
        self.shift_types = self.initialize_shift_types()
        self.num_shift_types = len(self.shift_types)

        # initialize skills and skill_sets collection
        self.skill_collection = SkillCollection(self.scenario_data)
        self.skill_set_collection = SkillSetCollection(self.scenario_data
                                                       ).initialize_skill_sets(self.skill_collection)
        # create skill object for each skill
        self.skill_collection.initialize_skills(self.skill_set_collection)

        self.skills = self.scenario_data['skills']
        self.skill_sets = self.get_unique_skill_sets()

        # extract employee data
        self.employees_spec = self.scenario_data["nurses"]
        self.employees = EmployeeCollection().initialize_employees(self, self.employees_spec)

        # extract skill requests
        self.skill_requests = self.initialize_skill_requests()

        # extract contract information
        self.contract_collection = None

        self.contract_collection = self.collect_contracts()
        self.forbidden_shift_type_successions = self.scenario_data['forbiddenShiftTypeSuccessions']

       # do I want to add skill sets as well?

    # TODO remove function
    def get_unique_skill_sets(self):
        """
        Function to get present skill sets in scenario
        """
        skills_array = np.array([set['skills'] for set in
                                 self.scenario_data['nurses']], dtype=object)
        skills_array = np.unique(skills_array)
        return sorted(np.unique(skills_array), key=lambda x: len(x))

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

    def initialize_skill_requests(self):
        """
        Create array of skill requests
        :return:
        array with dimensions num_days x num_shift_types x num_skill types
        """
        request_array = np.zeros((len(self.weeks) * 7,
                                  self.skill_collection.num_skills,
                                  self.num_shift_types,))

        # create objects with indices
        s_type_indices = self.list_to_index(self.shift_types)
        skill_indices = self.list_to_index(self.skill_collection.skills)

        for key, value in self.weeks_data.items():
            for req_dict in value['requirements']:
                for k, v in req_dict.items():
                    if k == "shiftType":
                        s_type_index = s_type_indices[v]
                    elif k == "skill":
                        skill_index = skill_indices[v]

                for k, v in req_dict.items():
                    if isinstance(k, int):
                        request_array[(key - 1) * 7 + k,
                        skill_index, s_type_index] = v['minimum']

        return request_array

    def list_to_index(self, list_obj):
        """
        Give index to each skill based on number of skills
        """
        # create object to store list_items and their index
        index_dict = {}
        index = 0
        for item in list_obj:
            index_dict[item] = index
            index += 1

        return index_dict


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
