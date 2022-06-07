import json

class Settings:
    """
    Class to save all problem settings
    """

    def __init__(self, settings_file_path=None, param=None):
        """Initialize settings"""

        if settings_file_path:
            f = open(settings_file_path)
            settings_json = json.load(f)

            # instance loading info
            # self.instance_name = settings_json['instance_settings']['instance_name']
            self.path = settings_json['instance_settings']['path']
            self.solution_path = settings_json['instance_settings']['solution_path']
            # self.history_file = settings_json['instance_settings']['history_file']
            # self.weeks = settings_json['instance_settings']['weeks']
            self.similarity = settings_json['instance_settings']['similarity']
            self.tuning = settings_json['instance_settings']['tuning']

            # load stage_1_settings
            self.stage_1_settings = settings_json['stage_1_settings']

            # load stage_2_settings
            self.stage_2_settings = settings_json['stage_2_settings']

            # tuning
            if param:
                self.stage_1_settings['heuristic_settings']['initial_temp'] = param
                self.stage_2_settings['heuristic_settings']['initial_temp'] = param
