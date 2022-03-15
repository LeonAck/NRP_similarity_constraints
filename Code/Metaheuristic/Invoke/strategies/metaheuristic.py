class MetaHeuristic:
    """
    Class to perform Particle Swarm Optimization
    """
    def __init__(self, domain):
        self.domain = domain
        # self.travel_expenses_matrix = domain.travel_expenses_matrix
        self.shifts = domain.shifts
        self.employees = domain.employees
        self.rules = domain.rules
        self.settings = domain.settings
        self.days = domain.days
        self.shift_type_definitions = domain.shift_type_definitions
        self.assignments = {}