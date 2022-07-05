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
        self.skill_indices = np.arange(0, len(self.skills))

        # create object to save skills
        self.collection = {}

    def index_to_id(self, index):
        """
        Get skill id based on the skill index
        """
        for id, skill in self.collection.items():
            if skill.index == index:
                skill_id = id
        if skill_id:
            return skill_id
        else:
            raise ValueError("This skill_index does not exist")

    def get_id_from_index(self, sk_index):
        try:
            return self.skills[sk_index]
        except KeyError:
            print("{} is not a skill index in this collection".format(sk_index))


    def initialize_skills(self, skill_set_collection):
        """
        Collect instances of skill class

        :return:
        Skill_collection
        """

        for sk_index, skill in enumerate(self.skills):
            indices_in_skill_counter = skill_set_collection.\
                get_indices_in_skill_counter(skill)
            self.collection[skill] = Skill(sk_index, indices_in_skill_counter)


        return self

class Skill:
    """
    Class to store skill information
    """
    def __init__(self, index, indices_in_skill_counter):
        self.id = None
        self.index = index
        self.indices_in_skill_counter = indices_in_skill_counter

