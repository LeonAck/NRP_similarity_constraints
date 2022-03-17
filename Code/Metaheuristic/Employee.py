import numpy as np
import random

class EmployeeCollection:
    """
    Class to collect all employees
    """

    def __init__(self, input_data=None, employees=None):
        if employees is None:
            employees = {}
        self._collection = employees

    def get_employee_w_skill(self, skill):
        """
        Collect employees with specific skill
        """
        return EmployeeCollection([employee for employee in self._collection if employee.has_skill(skill)])

    def initialize_employees(self, scenario, employees_spec):
        """
        Function to create class for all employees

        :return:
        instance of class Employee Collection with employees
        """
        import sys
        try:
            # for each employee_spec create an instance of the Employee class
            for employee_spec in employees_spec:
                self._collection[employee_spec['id']] = Employee(scenario, employee_spec)
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of user with ID = ' + employees_spec.get("id",
                                                                                                "'missing id'")).with_traceback(
                sys.exc_info()[2])
        #self._collection.sort(key=lambda employee: employee.id)
        return self

    def randomly_pick(self):
        """
        Randomly pick one employee from the collection
        :return:
        employee_index
        """
        return random.choice(self._collection)


class Employee:
    """
    Class to store employee information
    """

    def __init__(self, scenario, employee_spec=None):
        """Initialize employee parameters"""

        # information from scenario
        self.id = employee_spec['id']
        self.contract_type = employee_spec['contract']
        self.skill_set = employee_spec['skills']
        self.scenario = scenario

        # information from history
        self.history_lastAssignedShiftType = None
        self.history_numberOfConsecutiveAssignments = None
        self.history_numberOfConsecutiveDaysOff = None
        self.history_numberOfConsecutiveWorkingDays = None
        self.history_numberOfWorkingWeekends = None

        # information to keep track of solution
        self.total_assignments = None
        self.shift_assignments = self.create_assignments_array(self.scenario)
        self.working_days = None
        self.work_stretches = None
        self.working_weekends_set = None
        self.number_working_weekends = None
        self.shift_stretches = None # nog bedenken of dit samenkomt in een enkel object
        # of per shift type opslaan als object
        self.day_off_stretches = None

    def update_shift_assignment(self, day_index, s_type_index):
        """
        Update shift assignment of employee
        """
        self.shift_assignments[day_index] = s_type_index


    def has_skill(self, skill):
        return skill in self.skill_set

    def create_assignments_array(self, scenario):
        """
        Create an array with length of the number of days
        Each element in the array store the assignment of the nurse on that day
        0 --> off
        1 --> s_type_1
        2 --> s_type_2
        etc.
        :return:
        array of zeros
        """
        return np.zeros(scenario.num_days_in_horizon)


