import json
import pprint # to pretty print
import os


class Instance:
    """
    Class to store the instance data
    """
    def __init__(self, instance_name, path):
        """initialize instnace parameters"""
        # information for loading instance
        self.instance_name = instance_name
        self.path = path

        """
        # instance information
        self.size = size
        self.weeks = weeks
        """
        # create dict to store json files
        self.instance_dict = dict()
        self.instance_dict = self.load_instances()

    def get_instance_dict(self): return self.instance_dict

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
        return [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    def load_json_file(self, file_path):
        """
        Function to load json file
        :param file_path_file:
        :return:
        json_file in dictionary format
        """
        f = open(file_path)
        json_value = json.load(f)

        return json_value

    def load_instances(self):
        """
        Function to load instances and save into dicitonary
        :param path:
        :return:
        dictionary with files
        keys as filenames and value are dictionaries
        """

        # get list of json files
        path_to_json = self.instance_to_path()

        json_files = self.get_json_files(path_to_json)

        for file in json_files:
            # remove json for dictionary key per file
            json_key = file.removesuffix(".json")

            # create path for each json file
            file_path = path_to_json+"/{}".format(file)

            # add json file to dictionary
            self.instance_dict[json_key] = self.load_json_file(file_path)

        return self.instance_dict


instance = Instance("n030w4", "C:/Master_thesis/Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON")
#instance.load_instances()
pprint.pprint(instance.get_instance_dict())


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