import json
import pprint # to pretty print
import os


#path = "/home/luai/Desktop/python/test"
new_path = "C:\Master_thesis\Master_thesis\Data\sceschia-nurserostering-website-ecbcccff92e9\Datasets\JSON/n030w4"
f1 = open('Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON/n030w4/WD-n030w4-0.json')
f = open('Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON/n030w4/H0-n030w4-0.json')
f = open('Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON/n030w4/Sc-n030w4.json')


def instance_to_path(instance_name, folder_path):
    """
    Function to create a path from the name of the instance
    :param instance_name:
    :return:
    string stating the path of the folder
    """
    return folder_path+"/{}".format(instance_name)


print(instance_to_path("n030w4", 'Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON'))


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

def get_json_files(path_to_json):
    """Function to get list of json files in folder
    :return:
    list of json files
    """
    return [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

def load_json_file(file_path):
    """
    Function to load json file
    :param file_path_file:
    :return:
    json_file in dictionary format
    """
    f = open(file_path)
    json_value = json.load(f)

    return json_value


def load_instances(folder_path, instance):
    """
    Function to load instances and save into dicitonary
    :param path:
    :return:
    dictionary with files
    keys as filenames and value are dictionaries
    """
    # create dict to store json files
    instance_dict = dict()

    # get list of json files
    path_to_json = instance_to_path(instance, folder_path)

    json_files = get_json_files(path_to_json)

    for file in json_files:
        # remove json for dictionary key per file
        json_key = file.removesuffix(".json")

        # create path for each json file
        file_path = path_to_json+"/{}".format(file)

        # add json file to dictionary
        instance_dict[json_key] = load_json_file(file_path)

    return instance_dict


instance_dict = load_instances("Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON", "n030w4")

pprint.pprint(instance_dict)

