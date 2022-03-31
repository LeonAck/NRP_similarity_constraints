
class Settings:
    """
    Class to save all problem settings
    """

    def __init__(self, settings_file=None):
        """Initialize settings"""

        # input data settings
        self.source = "NRC"

        # settings for NRC-II data
        if self.source == "NRC":
            self.instance_name = "n030w8"
            self.path = "C:\Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON"
            self.history_file = 0
            self.weeks = [1, 2, 3, 4, 5]

        # weights per soft constraint

        # heuristic settings

        # problem settings
        self.soft_constraints = ["S1"]
        self.hard_constraints = None
        self.rules_specs = [
        {
            "id": "H1",
            "is_mandatory": True,
            "is_active": True,
            "is_horizontal": True,
            "penalty": 0
            },
            {"id": "H3",
             "is_mandatory": True,
             "is_active": True,
             "is_horizontal": True,
             "penalty": 0
             },
            {"id": "S1",
            "is_mandatory": False,
            "is_active": True,
            "is_horizontal": False,
            "penalty": 10
                }
        ]
