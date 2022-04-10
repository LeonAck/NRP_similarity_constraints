
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
            self.instance_name = "n030w4"
            self.path = "C:\Master_thesis/Code/Metaheuristic/Input/sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON"
            self.history_file = 0
            self.weeks = [1, 2, 3, 4, 5, 6,  7, 8]

        # weights per soft constraint

        # heuristic settings

        # problem settings
        self.soft_constraints = ["S1"]
        self.hard_constraints = None
        self.rules_specs = {
        "H1":{

            "is_mandatory": True,
            "is_active": True,
            "is_horizontal": True,
            "parameter_per_contract": False,
            "penalty": 0,
            "parameter_1": 0
            },
            "H3":{
             "is_mandatory": True,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": False,
             "penalty": 0,
             "parameter_1": 0
             },
             "S1":{
            "is_mandatory": False,
            "is_active": True,
            "is_horizontal": False,
             "parameter_per_contract": False,
            "penalty": 10,
             "parameter_1": 0
                },
            "S2_max": {
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 15,
             "parameter_1": 0
             },
             "S2_min":{
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S2_s_max":{
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S2_s_min":{
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S3_max":{
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S3_min":{
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S4":{
             "is_mandatory": False,
             "is_active": False,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 10,
             "parameter_1": 0
             },
            "S5_max": {
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 12,
             "parameter_1": 3
             },
            "S5_min": {
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 12,
             "parameter_1": 2
             },
            "S6": {
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
             "penalty": 10,
             "parameter_1": 2
             }
        }

        self.parameter_to_rule_mapping = {
            "S2_max": "maximumNumberOfConsecutiveWorkingDays",
            "S2_min": "minimumNumberOfConsecutiveWorkingDays",
            "S3_max": "maximumNumberOfConsecutiveDaysOff",
            "S3_min": "minimumNumberOfConsecutiveDaysOff",
            "S4": "completeWeekends",
            "S5_max": "minimumNumberOfAssignments",
            "S5_min": "minimumNumberOfAssignments",
            "S6": "maximumNumberOfWorkingWeekends",
        }

