import numpy as np

class SkillCollection:
    """
    Class to collect the skills in the scenario
    """

    def __init__(self, scenario_data):
        self.scenario_data = scenario_data

        # extract skill data
        self.skills = self.scenario_data['skills']
        self.num_skills = len(self.skills)

    def index_to_skill(self, index):
        """
        Get skill id based on the skill index
        """
        pass


class Skill:
    """
    Class to store skill information
    """
    def __init__(self):
        self.id = None
        self.index = None