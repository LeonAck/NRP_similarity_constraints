import numpy as np

class SkillSetCollection:
    """
    Class to collect skillsets in the scenario
    """
    def __init__(self, scenario_data, skill_sets=None):
        if skill_sets is None:
            skill_sets = {}
        self._collection = skill_sets

        self.scenario_data = scenario_data

        # how do I want to initialize?
        self.unique_skill_sets = self.get_unique_skill_sets()

    def get_skill_start_indices(self):
        return [value.start_index for value in self._collection.values()]

    def get_skill_start_index_of_set(self, skill_set_index):
        start_indices = self.get_skill_start_indices()
        return start_indices[skill_set_index]

    def get_unique_skill_sets(self):
        """
        Function to get present skill sets in scenario
        """
        skills_array = np.array([set['skills'] for set in
                                 self.scenario_data['nurses']], dtype=object)
        skills_array = np.unique(skills_array)
        return sorted(np.unique(skills_array), key=lambda x: len(x))

    def set_starting_index_skill_counter(self):
        """
        Starting index of each skill set in array counter
        """
        for index, skill_set in enumerate(self._collection):
            pass

        return self._collection

    def initialize_skill_sets(self):
        """
        Function to create dictionary out of skill_sets
        """
        import sys
        try:
            # create start_index for skill_set within skill_Counter object
            start_index = 0
            for index, skill_set in enumerate(self.unique_skill_sets):
                self._collection[index] = SkillSet(index, skill_set, start_index)
                start_index += len(skill_set)
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of skill_set with skills = ' + skill_set.get("id",
                                                                                                "'missing id'")).with_traceback(
                sys.exc_info()[2])

        return self


class SkillSet:
    """
    Class to store skillset information
    """

    def __init__(self, index, set_object, start_index):
        self.id = index
        self.skills_in_set = set_object

        # information to find in skill counter
        self.start_index = start_index
        self.skill_index_in_set = {}

    def __len__(self):
        return len(self.skills_in_set)

    def get_index_in_set(self, skill):
        """
        For a skill, find the index in a skill set
        """

    def get_skills_in_set(self):
        """
        Collect all skill ids in set
        """

    def get_start_index(self):
        """
        Set start index in skill counter
        """
