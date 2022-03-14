

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
            self.instance_name = "n012w8"
            self.path = "C:\Master_thesis\Code\Metaheuristic\Input\sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON"
            self.problem_size = self.get_problem_size()
            self.problem_horizon = self.get_problem_horizon()

        # problem settings
        self.soft_constraints = None
        self.hard_constraints = None

        # weights per soft constraint

        # heuristic settings

    def get_problem_size(self):
        """
        Function to get problem size from instance string
        """
        return int(self.instance[1:4])

    def get_problem_horizon(self):
        """
        Function to get number of weeks from instance string
        :return:
        number of weeks (int)
        """
        return int(self.instance[5:])