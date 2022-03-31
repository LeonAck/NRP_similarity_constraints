import numpy as np


class ShiftTypeCollection:
    """
    Create class to collect shift types
    """

    def __init__(self, scenario_data):
        # collect shift types
        self.shift_types = self.initialize_shift_types(scenario_data)
        self.shift_types_indices = np.arange(0, len(self.shift_types), dtype=object)

    def __len__(self):
        return len(self.shift_types)

    def initialize_shift_types(self, scenario_data):
        """
        Class to get shift types in the solution
        """
        return [s_type['id'] for s_type in scenario_data['shiftTypes']]

    def get_id_from_index(self, s_index):
        return self.shift_types[s_index]

