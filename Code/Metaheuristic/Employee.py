
class EmployeeCollection:
    """
    Class to collect all employees
    """

    def __init__(self, input_data):
        None

    def initialize_employees(self):
        """
        Function to create class for all employees

        :return:
        dict with employee_id as key and employee class as value
        """



class Employee:
    """
    Class to store employee information
    """

    def __init__(self, input_data):
        """Initialize employee parameters"""

        # information from scenario
        self.id = None
        self.contract_type = None
        self.skill_set = None

        # information from history
        self.his_lastAssignedShiftType = None
        self.his_numberOfConsecutiveAssignments = None
        self.his_numberOfConsecutiveDaysOff = None
        self.his_numberOfConsecutiveWorkingDays = None
        self.his_numberOfWorkingWeekends = None

        # information to keep track of solution
        self.total_assignments = None
        self.shift_assignments = None
        self.working_days = None
        self.work_stretches = None
        self.working_weekends_set = None
        self.number_working_weekends = None
        self.shift_stretches = None # nog bedenken of dit samenkomt in een enkel object
        # of per shift type opslaan als object
        self.day_off_stretches = None

    def update_shift_assignment(self):
        """
        Update shift assignment of employee
        """
        return None

