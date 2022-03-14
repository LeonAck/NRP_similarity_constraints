import json
import pprint # to pretty print
import os
from settings import Settings


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
        self.history_data = dict(
        )
        self.scenario_data = dict()
        self.weeks_dict = dict()
        self.load_instance()

    #def get_instance_dict(self): return self.instance_dict

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
        return int(self.instance_name[5:])

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
        weeks_strings = [str(i) for i in self.weeks]
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
        # selection of files based on instances
        files_to_keep = self.get_history_file(all_json_files) +\
                        self.get_scenario_file(all_json_files) +\
                        self.get_week_files(all_json_files)
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
            self.weeks_dict[file] = self.load_json_file(file_path)

        return None

settings = Settings()
instance = Instance(settings)

#instance.load_instances()
pprint.pprint(instance.history_data)
pprint.pprint(instance.scenario_data)
pprint.pprint(instance.weeks_dict)

"""
def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = [pos_json for pos_json in os.listdir(dirName) if pos_json.endswith('.json')]
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)

        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)

    return allFiles
"""