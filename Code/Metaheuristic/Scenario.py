
class Scenario:
    """
    Class to store all the scenario information

    contracts

    forbidden shift type successions
    """

    def __init__(self, input_data):
        """
        Initialize parameters
        """

        self.contract_collection = None

        self.contract_collection = self.collect_contracts()
        self.forbidden_shift_type_successions = None

        # store all present skill sets
        self.skill_sets = self.initialize_skill_sets()

    def collect_contracts(self):
        """
        Class to store all contracts
        :return:
        dict of contracts
        """
        return None

    def initialize_skill_sets(self):
        """
        Function to get present skill sets in scenario
        """
        return None

    def create_requests(self):
        """
        Create array of skill requests
        :return:
        array with dimensions num_days x num_shift_types x num_
        """


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
