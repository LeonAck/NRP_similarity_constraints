import json
import os
from copy import copy
import numpy as np


class Instance:
    """
    Class to store the instance data
    """

    def __init__(self, settings, file_name=None):
        """initialize instance parameters"""
        self.folder_name = "030-4-1-6-2-9-1"
        self.similarity = settings.similarity

        # information for loading instance
        self.instance_name = self.deduce_folder_name()
        self.path = settings.path
        self.solution_path = settings.solution_path
        self.history_file = int(self.folder_name[6])
        self.weeks = self.get_weeks_from_folder_name()

        # scenario information
        self.problem_size = self.set_problem_size()
        self.problem_horizon = self.set_problem_horizon()

        # create dict to store json files
        self.history_data = dict()
        self.scenario_data = dict()
        self.weeks_data = dict()
        self.load_instance()
        self.skills = self.scenario_data['skills']

        # simplify notation
        self.simplify_week_data()
        self.simplify_scenario_data()
        self.history_data = self.simplify_history_data()

        # get reference period
        if self.similarity:
            self.ref_assignments = self.prev_solution_to_ref_assignments()

        # get history data per employee
        if not self.similarity:
            self.last_assigned_shift = self.collect_history_data_per_employee(feature='lastAssignedShiftType')
            self.historical_work_stretch = self.collect_history_data_per_employee(
                feature='numberOfConsecutiveWorkingDays')
            self.historical_off_stretch = self.collect_history_data_per_employee(feature='numberOfConsecutiveDaysOff')
            self.historical_shift_stretch = self.collect_history_data_per_employee(
                feature='numberOfConsecutiveAssignments')
        else:
            self.historical_work_stretch, self.last_assigned_shift, self.historical_shift_stretch, self.historical_off_stretch = self.get_history_from_reference()
        # get employee preferences
        self.employee_preferences = self.collect_employee_preferences()

    def collect_employee_preferences(self):
        employee_preferences = {}

        for i, value in enumerate(self.weeks_data.values()):
            for shift_off_request in value["shiftOffRequests"]:
                if shift_off_request['nurse'] in employee_preferences:

                    employee_preferences[shift_off_request['nurse']][
                        7 * i + self.weekday_to_index(shift_off_request['day'])] \
                        = self.get_index_of_shift_type(shift_off_request['shiftType']) \
                        if shift_off_request['shiftType'] != "Any" else -1
                # create new
                else:
                    employee_preferences[shift_off_request['nurse']] = {}
                    employee_preferences[shift_off_request['nurse']][
                        7 * i + self.weekday_to_index(shift_off_request['day'])] \
                        = self.get_index_of_shift_type(shift_off_request['shiftType']) \
                        if shift_off_request['shiftType'] != "Any" else -1

        return employee_preferences

    def collect_history_data_per_employee(self, feature):
        last_assigned_shifts = {}
        for employee_id, employee_history in self.history_data.items():
            last_assigned_shifts[employee_id] = employee_history[feature]

        return last_assigned_shifts

    def replace_history_data_per_employee(self, value):
        placeholder = {}
        for employee_id in self.history_data.keys():
            placeholder[employee_id] = value
        return placeholder

    def simplify_history_data(self):
        history_data = {}

        # assign values to employee_id
        for employee_data in self.history_data['nurseHistory']:
            history_data[employee_data['nurse']] = employee_data

        # change shifts abbreviations
        for employee_id, employee_history in history_data.items():
            history_data[employee_id]['lastAssignedShiftType'] = -1 \
                if employee_history['lastAssignedShiftType'] == 'None' \
                else self.get_index_of_shift_type(employee_history['lastAssignedShiftType'])

        return history_data

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
        :return:
        string stating the path of the folder
        """
        return self.path + "/{}".format(self.instance_name)

    def get_json_files(self, path_to_json):
        """Function to get list of json files in folder
        :return:
        list of json files
        """

        return [pos_json.removesuffix(".json") for pos_json
                in os.listdir(path_to_json) if pos_json.endswith('.json')]

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
        weeks_strings = ["-" + str(i) for i in self.weeks]
        week_files = []
        for string in weeks_strings:
            for file in list_of_files:
                if file.startswith("WD") \
                        and file.endswith(string):
                    week_files.append(file)
        return week_files

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
            return int(week_key.removeprefix("WD-" + self.instance_name + "-"))
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

    def get_index_of_shift_type(self, shift_type_id):
        """
        Function to get index when given a skill type
        """
        for index, s_type in enumerate(self.scenario_data['shiftTypes']):
            if s_type['id'] == self.abbreviate_shift_type(shift_type_id):
                return index

    def get_index_of_skill_type(self, skill_type):
        return self.skills.index(skill_type)

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
        self.scenario_data["skills"] = [self.abbreviate_skills(skill)
                                        for skill in self.scenario_data["skills"]]

        # change skills for each nurse
        # for key, value in self.scenario_data:
        for n_index, nurse in enumerate(self.scenario_data['nurses']):
            for s_index, skill in enumerate(nurse['skills']):
                self.scenario_data['nurses'][
                    n_index]['skills'][s_index] = self.abbreviate_skills(skill)

        # abbreviate shift types in succesion
        for i, succession in enumerate(self.scenario_data['forbiddenShiftTypeSuccessions']):
            self.scenario_data['forbiddenShiftTypeSuccessions'][i]['precedingShiftType'] \
                = self.get_index_of_shift_type(
                self.scenario_data['forbiddenShiftTypeSuccessions'][i]['precedingShiftType'])
            self.scenario_data['forbiddenShiftTypeSuccessions'][i]['succeedingShiftTypes'] \
                = [self.get_index_of_shift_type(succession_second) for succession_second in
                   succession['succeedingShiftTypes']]

        # create list of tuples for only the shifts that have a forbidden succeeding shift type
        self.scenario_data['forbiddenShiftTypeSuccessions'] \
            = [(successions['precedingShiftType'],
                successions['succeedingShiftTypes'])
               for successions
               in self.scenario_data['forbiddenShiftTypeSuccessions']
               ]

    def deduce_folder_name(self):
        num_nurses = self.folder_name[0:3]
        num_weeks = self.folder_name[4]

        return "n{}w{}".format(num_nurses, num_weeks)

    def prev_solution_to_ref_assignments(self):
        solution_path = self.solution_path + "/{}/solution.txt".format(self.folder_name)
        # create object for ref_assignments
        ref_assignments = {}
        for nurse in self.scenario_data['nurses']:
            ref_assignments[nurse['id']] = np.full((len(self.weeks) * 7, 2), -1, dtype=int)

        with open(solution_path, "rb") as s_file:
            lines = s_file.readlines()
        for line in lines[1:-4]:
            split_line = self.prepare_line_for_assignment(line)
            if split_line[1] <= 27:
                ref_assignments[split_line[0]][split_line[1]] = np.array([split_line[2], split_line[3]])
        return ref_assignments

    def prepare_line_for_assignment(self, line):
        split_line = str(line).split(" ")
        split_line[0] = split_line[0][2:]
        split_line[1] = int(split_line[1][:-4])
        split_line[2] = self.get_index_of_shift_type(split_line[2])
        split_line[3] = self.get_index_of_skill_type(split_line[3][:-5])
        return split_line

    def get_weeks_from_folder_name(self):
        folder_name = copy(self.folder_name)
        week_string = folder_name[7:]
        weeks = []
        while len(week_string) > 0:
            weeks.append(int(week_string[1]))
            week_string = week_string[2:]
        return weeks[4:] if self.similarity else weeks

    def get_history_from_reference(self):
        # historical_work_stretch

        historical_work_stretch = {}
        last_assigned_shift = {}
        historical_off_stretch = {}
        historical_shift_stretch = {}
        for employee_id, assignments in self.ref_assignments.items():

            # historical work stretch
            if assignments[-1][0] == -1:
                historical_work_stretch[employee_id] = 0
            else:
                i = 1
                s_type = None
                while s_type != -1:
                    s_type = assignments[-i][0]
                    i += 1

                historical_work_stretch[employee_id] = i-2

            # historical off stretch
            if historical_work_stretch[employee_id] > 0:
                historical_off_stretch[employee_id] = 0
            else:
                i = 1
                s_type = -1
                while s_type == -1:
                    s_type = assignments[-i][0]
                    i += 1
                historical_off_stretch[employee_id] = i-2

            # last assigned shift
            if historical_work_stretch[employee_id] > 0:
                last_assigned_shift[employee_id] = assignments[-1][0]
            else:
                last_assigned_shift[employee_id] = -1

            # historical shift stretch
            if historical_work_stretch[employee_id] > 0:
                i = 1
                s_type = last_assigned_shift[employee_id]
                while s_type == last_assigned_shift[employee_id]:
                    s_type = assignments[-i][0]
                    i += 1
                historical_shift_stretch[employee_id] = i-2
            else:
                historical_shift_stretch[employee_id] = 0

        return historical_work_stretch, last_assigned_shift, historical_shift_stretch, historical_off_stretch
