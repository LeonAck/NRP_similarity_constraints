import json
import os
from Domain.settings import Settings
from Domain.scenario import Scenario
from Invoke.Initial_solution.initial_solution import InitialSolution
from Check.check_function_feasibility import FeasibilityCheck
from operators import sk_request_to_day_off


class Instance:
    """
    Class to store the instance data
    """
    def __init__(self, settings):
        """initialize instnace parameters"""
        # information for loading instance
        self.instance_name = settings.instance_name
        self.path = settings.path
        self.history_file = settings.history_file
        self.weeks = settings.weeks

        # scenario information
        self.problem_size = self.set_problem_size()
        self.problem_horizon = self.set_problem_horizon()

        # create dict to store json files
        self.history_data = dict()
        self.scenario_data = dict()
        self.weeks_data = dict()
        self.load_instance()

        # simplify notation
        self.simplify_week_data()
        self.simplify_scenario_data()

    def set_problem_size(self):
        """
        Function to get problem size from instance string
        """
        return int(self.instance_name[1:4])

    def set_problem_horizon(self):
        """
        Function to get number of weeks from instance string
        :return:
        number of weeks (int)
        """
        return len(self.weeks)

    def instance_to_path(self):
        """
        Function to create a path from the name of the instance
        :param instance_name:
        :return:
        string stating the path of the folder
        """
        return self.path+"/{}".format(self.instance_name)

    def get_json_files(self, path_to_json):
        """Function to get list of json files in folder
        :return:
        list of json files
        """

        return [pos_json.removesuffix(".json") for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    def load_json_file(self, file_path):
        """
        Function to load json file
        :param file_path:
        :return:
        json_file in dictionary format
        """
        f = open(file_path)
        json_value = json.load(f)

        return json_value

    def get_history_file(self, list_of_files):
        """
        Function to get name of right history file
        """
        return [file for file in list_of_files if file.startswith("H0")
                and file.endswith(str(self.history_file))]

    def get_scenario_file(self, list_of_files):
        """
        Function to get scenario file
        """
        scenario_file = [file for file in list_of_files if file.startswith("Sc")]

        if not scenario_file:
            raise Exception("Folder does not contain a scenario file")

        else:
            return scenario_file

    def get_week_files(self, list_of_files):
        """
        Function to get selection of week files chosen in settings
        """
        # TODO must still add way to keep the order of the week files
        weeks_strings = ["-"+str(i) for i in self.weeks]
        return [file for file in list_of_files if file.startswith("WD")
                and file.endswith(tuple(weeks_strings))]

    def load_files(self, list_of_files):
        """
        Function to load files into dict
        """

    def load_instance(self):
        """
        Function to load instances and save into dicitonary
        :return:
        dictionary with files
        keys as filenames and value are dictionaries
        """

        # get list of json files
        path_to_json = self.instance_to_path()

        all_json_files = self.get_json_files(path_to_json)

        for file in self.get_history_file(all_json_files):
            # create path for each json file
            file_path = path_to_json + "/{}".format(file + ".json")

            # add json file to dictionary
            self.history_data = self.load_json_file(file_path)

        for file in self.get_scenario_file(all_json_files):
            # create path for each json file
            file_path = path_to_json + "/{}".format(file + ".json")

            # add json file to dictionary
            self.scenario_data = self.load_json_file(file_path)

        for file in self.get_week_files(all_json_files):
            # create path for each json file
            file_path = path_to_json + "/{}".format(file + ".json")

            # add json file to dictionary
            self.weeks_data[file] = self.load_json_file(file_path)

        return None

    def abbreviate_skills(self, skill_string):
        """
        Save first letter as lower case
        """
        return skill_string[0].lower()

    def abbreviate_shift_type(self, shiftype_string):
        """
        Save first letter as upper case
        """
        return shiftype_string[0]

    def weekday_to_index(self, weekday_string):
        """
        Function to change weekday string to index
        Monday --> 0
        Tuesday --> 1
        etc.

        """
        if weekday_string == "Monday":
            return 0
        if weekday_string == "Tuesday":
            return 1
        if weekday_string == "Wednesday":
            return 2
        if weekday_string == "Thursday":
            return 3
        if weekday_string == "Friday":
            return 4
        if weekday_string == "Saturday":
            return 5
        if weekday_string == "Sunday":
            return 6
        else:
            raise Exception("This is not a weekday")

    def simplify_week_key(self, week_key):
        """
        Change weekday string to "Wx" where x is week number
        """
        if isinstance(week_key, str):
            return int(week_key.removeprefix("WD-"+self.instance_name+"-"))
        else:
            return week_key

    def requirement_key_to_index(self):
        """
        Function to change all requirement keys to index
        example: requirementOnMonday to 0
        """
        # change key of requirements to integers
        # Monday --> 0
        # Tuesday --> 1
        # etc.
        for value in self.weeks_data.values():
            for requirements in value['requirements']:
                translate_req = {}
                for key in requirements.keys():
                    if key.startswith("requirementOn"):
                        translate_req[key] = self.weekday_to_index(
                            key.removeprefix("requirementOn"))

                for old, new in translate_req.items():
                    requirements[new] = requirements.pop(old)

    def abbreviate_shifts_skills_week_data(self):
        """
        Abbreviate shift type and skills in week data dicts
        """
        for value in self.weeks_data.values():
            for requirements in value['requirements']:
                for key, value in requirements.items():
                    if key == 'shiftType':
                        requirements[key] = self.abbreviate_shift_type(value)

                    if key == 'skill':
                        requirements[key] = self.abbreviate_skills(value)

    def abbreviate_shifts_skills_scenario_data(self):
        """
        Abbreviate shift type and skills in scenario data dicts
        """
        for s_type in self.scenario_data['shiftTypes']:
            s_type['id'] = self.abbreviate_shift_type(s_type['id'])


    def simplify_week_data(self):
        """
        Function to simplify scenario
        """

        # change week key into integer
        translate = {}
        # save new keys
        for key in self.weeks_data.keys():
            translate[key] = self.simplify_week_key(key)

        # replace old keys by new keys
        for old, new in translate.items():
            self.weeks_data[new] = self.weeks_data.pop(old)

        # changes keys of weekly requirements
        self.requirement_key_to_index()

        # abbreviate shift type and skills
        self.abbreviate_shifts_skills_week_data()

    def simplify_scenario_data(self):
        """
        Function to simplify scenario data
        """
        # save first letter of shift type as capital
        self.abbreviate_shifts_skills_scenario_data()

        # save first letter of skill as lower case
        # change in list of skills
        save_skills = self.scenario_data["skills"]
        self.scenario_data["skills"] = [self.abbreviate_skills(skill)
                                        for skill in self.scenario_data["skills"]]

        # change skills for each nurse
        # for key, value in self.scenario_data:
        for n_index, nurse in enumerate(self.scenario_data['nurses']):
            for s_index, skill in enumerate(nurse['skills']):
                self.scenario_data['nurses'][
                    n_index]['skills'][s_index] = self.abbreviate_skills(skill)

settings = Settings()
instance = Instance(settings)
scenario = Scenario(settings, instance)
init_solution = InitialSolution(scenario)
FeasibilityCheck().assignments_equals_skill_counter(init_solution, scenario)
FeasibilityCheck().h2_check_function(init_solution, scenario)
employee_id = "Stefaan"
d_index = 5
s_type_index = 2
sk_request_to_day_off(init_solution, scenario.skill_set_collection, scenario.employees, employee_id, d_index, s_type_index)
#instance.load_instances()
# pprint.pprint(instance.history_data)
# pprint.pprint(instance.scenario_data)
# pprint.pprint(instance.weeks_data)
# pprint.pprint(scenario.scenario_data)

# pprint.pprint(scenario.weeks_data)
# pprint.pprint(scenario.skill_requests)
# print(scenario.num_days_in_horizon)
# print(scenario.employees._collection['Patrick'].has_skill("h"))