
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
            # should be a list of numbers, no range
            self.weeks = [1, 2, 3, 4]

        # weights per soft constraint

        # heuristic settings

        # problem settings second stage
        # if first_stage:
        #     pass
        self.rules_specs = {
        "H1":{"id": "H1",
            "is_mandatory": True,
            "is_active": True,
            "is_horizontal": True,
            "parameter_per_contract": False,
              "parameter_per_s_type": False,
            "penalty": 0,
            "parameter_1": 0
            },
            "H3":{"id": "H3",
             "is_mandatory": True,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": False,
                  "parameter_per_s_type": False,
             "penalty": 0,
             "parameter_1": 0
             },
             "S1":{"id": "S1",
            "is_mandatory": False,
            "is_active": True,
            "is_horizontal": False,
             "parameter_per_contract": False,
                   "parameter_per_s_type": False,
            "penalty": 30,
             "parameter_1": 0
            },
            "S2Max": {"id":  "S2Max",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
              "parameter_per_s_type": False,
             "penalty": 30,
             "parameter_1": 0
             },
             "S2Min": {"id": "S2Min",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
            "parameter_per_s_type": False,
             "penalty": 30,
             "parameter_1": 0
             },
            "S2ShiftMax":{"id": "S2Shiftmax",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
                          "parameter_per_contract": False,
                          "parameter_per_s_type": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S2ShiftMin":{"id": "S2ShiftMin",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
              "parameter_per_contract": False,
            "parameter_per_s_type": True,
             "penalty": 15,
             "parameter_1": 0
             },
            "S3Max":{"id": "S3Max",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
                     "parameter_per_s_type": False,
             "penalty": 30,
             "parameter_1": 0
             },
            "S3Min":{"id": "S3Min",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
                     "parameter_per_s_type": False,
             "penalty": 30,
             "parameter_1": 0
             },
            "S4":{"id":  "S4",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
                  "parameter_per_s_type": False,
             "penalty": 30,
             "parameter_1": 0
             },
            "S5_max": {"id": "S5_max",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
                       "parameter_per_s_type": False,
             "penalty": 20,
             "parameter_1": 3
             },
            "S5_min": {"id": "S5_min",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
                       "parameter_per_s_type": False,
             "penalty": 20,
             "parameter_1": 2
             },
            "S6": {"id": "S6",
             "is_mandatory": False,
             "is_active": True,
             "is_horizontal": True,
             "parameter_per_contract": True,
                   "parameter_per_s_type": False,
             "penalty": 30,
             "parameter_1": 2
             },
            "S7Day": {"id": "S7Day",
                        "is_mandatory": False,
                      "is_active": True,
                      "is_horizontal": True,
                       "parameter_per_contract": False,
                   "parameter_per_s_type": False,
             "penalty": 10,
             "parameter_1": 4},
            "S7Shift": {"id": "S7Shift",
                      "is_mandatory": False,
                      "is_active": True,
                      "is_horizontal": True,
                      "parameter_per_contract": False,
                      "parameter_per_s_type": False,
                      "penalty": 6,
                      "parameter_1": 4}
        }

        self.parameter_to_rule_mapping = {
            "S2Max": "maximumNumberOfConsecutiveWorkingDays",
            "S2Min": "minimumNumberOfConsecutiveWorkingDays",
            "S3Max": "maximumNumberOfConsecutiveDaysOff",
            "S3Min": "minimumNumberOfConsecutiveDaysOff",
            "S4": "completeWeekends",
            "S5_max": "maximumNumberOfAssignments",
            "S5_min": "minimumNumberOfAssignments",
            "S6": "maximumNumberOfWorkingWeekends",
            "S2ShiftMax": "maximumNumberOfConsecutiveAssignments",
            "S2ShiftMin": "minimumNumberOfConsecutiveAssignments"
        }


