import json
import pprint #to pretty print
import os


path = "/home/luai/Desktop/python/test"
f1 = open('Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON/n030w4/WD-n030w4-0.json')
f = open('Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON/n030w4/H0-n030w4-0.json')
f = open('Data/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON/n030w4/Sc-n030w4.json')

def load_instances(path):
    """
    Function to load instances and save into dicitonary
    :param path:
    :return:
    dictionary with files
    keys as filenames and value are dictionaries
    """
    dirs = os.listdir(path)

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
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

data = json.load(f)

pprint.pprint(data)