

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
            self.instance_name = "n110w32"
            self.path = "C:\Master_thesis\Code\Metaheuristic\Input\sceschia-nurserostering-website-ecbcccff92e9/Datasets/JSON"
            self.history_file = 0
            self.weeks = [1, 2 ,3, 4, 5, 6, 7, 8, 9, 10]

        # problem settings
        self.soft_constraints = None
        self.hard_constraints = None

        # weights per soft constraint

        # heuristic settings

