
class Settings:
    """
    Class to save all problem settings
    """

    def __init__(self, settings_file):
        """Initialize settings"""

        self.soft_constraints = None
        self.hard_constraints = None

        # weights per soft constraint

        # heuristic settings
