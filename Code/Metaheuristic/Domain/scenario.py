import numpy as np
from Domain.employee import EmployeeCollection
from Domain.skills import SkillCollection
from Domain.skill_set import SkillSetCollection
from Domain.shifts import ShiftTypeCollection
from Invoke.Constraints.initialize_rules import RuleCollection
from Domain.days import DayCollection
import pickle

class Scenario:
    """
    Class to store all the scenario information

    contracts

    forbidden shift type successions
    """

    def __init__(self, stage_settings, instance):
        """
        Initialize parameters
        """

        # initialize instance data
        self.instance = instance
        self.weeks_data = instance.weeks_data
        self.weeks = instance.weeks
        self.history_data = instance.history_data
        self.scenario_data = instance.scenario_data
        self.problem_horizon = instance.problem_horizon

        # initialize two stage settings
        self.stage_number = stage_settings['stage_number']
        self.stage_settings = stage_settings
        self.rules_specs = self.stage_settings['rules']

        # extract problem data
        self.num_days_in_horizon = self.problem_horizon * 7
        self.day_collection = DayCollection(self.num_days_in_horizon)

        # extract shift type data
        self.shift_collection = ShiftTypeCollection(self.scenario_data)
        self.num_shift_types = len(self.shift_collection)

        # initialize skills and skill_sets collection
        self.skill_collection = SkillCollection(self.scenario_data)
        self.skill_set_collection = SkillSetCollection(self.scenario_data
                                                       ).initialize_skill_sets(self.skill_collection)
        # create skill object for each skill
        self.skill_collection.initialize_skills(self.skill_set_collection)

        self.skills = self.scenario_data['skills']
        self.skill_sets = self.get_unique_skill_sets()

        # extract employee data
        self.employees_specs = self.scenario_data["nurses"]
        self.employees = EmployeeCollection().initialize_employees(self, self.employees_specs)

        # get dict of multiskill employees
        self.multi_skill = self.get_dict_multi_skill()

        # extract minimal and optimal skill requests
        self.skill_requests = self.initialize_skill_requests()
        self.optimal_coverage = self.initialize_optimal_coverage()

        # collect shift of requests and forbidden shift type successions
        self.employee_preferences = instance.employee_preferences
        self.forbidden_shift_type_successions = self.scenario_data['forbiddenShiftTypeSuccessions']

        # get history data
        self.last_assigned_shift = instance.last_assigned_shift
        self.historical_work_stretch = instance.historical_work_stretch
        self.historical_off_stretch = instance.historical_off_stretch
        self.historical_shift_stretch = instance.historical_shift_stretch

        # greedy operator
        self.greedy_number = stage_settings['heuristic_settings']['greedy_number']
        # save rule mappings
        self.parameter_to_rule_mapping = {
            "S2Max": "maximumNumberOfConsecutiveWorkingDays",
            "S2Min": "minimumNumberOfConsecutiveWorkingDays",
            "S3Max": "maximumNumberOfConsecutiveDaysOff",
            "S3Min": "minimumNumberOfConsecutiveDaysOff",
            "S4": "completeWeekends",
            "S5Max": "maximumNumberOfAssignments",
            "S5Min": "minimumNumberOfAssignments",
            "S6": "maximumNumberOfWorkingWeekends",
            "S2ShiftMax": "maximumNumberOfConsecutiveAssignments",
            "S2ShiftMin": "minimumNumberOfConsecutiveAssignments"
        }

        # collect rules
        self.rules_specs = self.add_differentiate_rule_parameters(self.rules_specs)
        self.rule_collection = RuleCollection().initialize_rules(self.rules_specs, self.employees)

        # S8ref
        if 'S8RefDay' in self.rule_collection.collection or 'S8RefShift' in self.rule_collection.collection or 'S8RefSkill' in self.rule_collection.collection:
            self.ref_assignments = self.get_ref_assignments()

    # TODO remove function
    def get_unique_skill_sets(self):
        """
        Function to get present skill sets in scenario
        """
        skills_array = np.array([set['skills'] for set in
                                 self.scenario_data['nurses']], dtype=object)
        skills_array = np.unique(skills_array)
        return sorted(np.unique(skills_array), key=lambda x: len(x))

    def get_dict_multi_skill(self):
        multi_skill_dict = {employee_id: True if len(v.skills) > 1 else False for employee_id, v in self.employees._collection.items()}
        return multi_skill_dict


    def add_differentiate_rule_parameters(self, rules_specs):
        """
        Function to add the rule parameters to the settings based on the instance
        parameters
        :return:
        instance of settings class
        """
        for rule_id, rule_spec in rules_specs.items():
            if rule_id in self.parameter_to_rule_mapping:
                if rule_spec['parameter_per_contract']:
                    rules_specs[rule_id]["parameter_1"] \
                        = self.rule_parameter_contract_dict(self.parameter_to_rule_mapping[rule_id])
                if rule_spec['parameter_per_s_type']:
                    rules_specs[rule_id]["parameter_2"] \
                        = self.get_s_type_specific_par(self.parameter_to_rule_mapping[rule_id])

        return rules_specs

    def get_s_type_specific_par(self, parameter_str):
        """
        Function to create dict of s_type specific parameters
        """
        parameter_dict = {}
        for s_type in self.scenario_data['shiftTypes']:
            parameter_dict[
                self.instance.get_index_of_shift_type(
                    self.instance.abbreviate_shift_type(s_type['id']))] = s_type[parameter_str]

        return parameter_dict

    def rule_parameter_contract_dict(self, parameter_str):
        """
        Function to create dict with parameters for every contract type
        for a specific rule
        :return:
        dict
        """
        parameter_dict = {}
        for contract in self.scenario_data['contracts']:
            parameter_dict[contract['id']] = contract[parameter_str]

        return parameter_dict

    def collect_contracts(self):
        """
        Class to store all contracts
        :return:
        dict of contracts
        """
        return None

    def initialize_skill_requests(self):
        """
        Create array of skill requests
        :return:
        array with dimensions num_days x skills x num shift types
        """
        request_array = np.zeros((len(self.weeks) * 7,
                                  self.skill_collection.num_skills,
                                  self.num_shift_types))

        # create objects with indices
        s_type_indices = self.list_to_index(self.shift_collection.shift_types)
        skill_indices = self.list_to_index(self.skill_collection.skills)

        for i, value in enumerate(self.weeks_data.values()):
            for req_dict in value['requirements']:
                for k, v in req_dict.items():
                    if k == "shiftType":
                        s_type_index = s_type_indices[v]
                    elif k == "skill":
                        skill_index = skill_indices[v]

                for k, v in req_dict.items():
                    if isinstance(k, int):
                        request_array[i * 7 + k,
                        skill_index, s_type_index] = v['minimum']

        return request_array

    def get_ref_assignments(self):
        with open(self.stage_settings['ref_period_path'], "rb") as ref_shift_assignments_file:
            ref_assignments = pickle.load(ref_shift_assignments_file)
        return ref_assignments

    def initialize_optimal_coverage(self):
        """
               Create array of skill requests
               :return:
               array with dimensions num_days x num_shift_types x num_skill types
        """
        request_array = np.zeros((len(self.weeks) * 7,
                                  self.skill_collection.num_skills,
                                  self.num_shift_types,))

        # create objects with indices
        s_type_indices = self.list_to_index(self.shift_collection.shift_types)
        skill_indices = self.list_to_index(self.skill_collection.skills)

        for i, value in enumerate(self.weeks_data.values()):
            for req_dict in value['requirements']:
                for k, v in req_dict.items():
                    if k == "shiftType":
                        s_type_index = s_type_indices[v]
                    elif k == "skill":
                        skill_index = skill_indices[v]

                for k, v in req_dict.items():
                    if isinstance(k, int):
                        request_array[i * 7 + k,
                                      skill_index, s_type_index] = v['optimal']

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
