import numpy as np
import random

# TODO add function to get nurses that work a certain shift per day
class EmployeeCollection:
    """
    Class to collect all employees
    """

    def __init__(self, employees=None):

        if employees is not None:
            employees = self.create_dict_from_list(employees)
        else:
            employees = {}

        self._collection = employees

    def __len__(self):
        return len(self._collection)

    def get_employee_w_skill(self, skill):
        """
        Collect employees with specific skill
        """
        return EmployeeCollection([employee for employee in self._collection.values() if employee.has_skill(skill)])

    def get_employee_w_skillset(self, skill_set_id):
        return EmployeeCollection([employee for employee in self._collection.values() if employee.skill_set_id == skill_set_id])

    def get_nurse_w_s_sk_assignment(self, assignment_tuple):
        """
        Collect employees that work a specific shift skill combination for certain day
        """

    def create_dict_from_list(self, list):
        """
        Create dict from employee list
        """
        employee_dict = {
        }
        for employee in list:
            employee_dict[employee.id] = employee

        return employee_dict

    def exclude_employee(self, employee_id_to_exclude):
        return EmployeeCollection([employee for employee in self._collection.values() if employee.id is not employee_id_to_exclude])

    def initialize_employees(self, scenario, employees_specs):
        """
        Function to create class for all employees

        :return:
        instance of class Employee Collection with employees
        """
        import sys
        try:
            # for each employee_spec create an instance of the Employee class
            for employee_spec in employees_specs:
                self._collection[employee_spec['id']] = Employee(scenario, employee_spec)

        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of user with ID = ' + employees_specs.get("id",
                                                                                                "'missing id'")).with_traceback(
                sys.exc_info()[2])
        #self._collection.sort(key=lambda employee: employee.id)
        return self

    def random_pick(self):
        """
        Randomly pick one employee from the collection
        :return:
        employee_index
        """
        return random.choice(list(self._collection))

    def get_ids(self):
        """
        Function to get list of ideas
        """
        return [employee.id for employee in self._collection.values()]


class Employee:
    """
    Class to store employee information
    """

    def __init__(self, scenario, employee_spec=None):
        """Initialize employee parameters"""

        # information from scenario
        self.id = employee_spec['id']
        self.contract_type = employee_spec['contract']
        self.skills = employee_spec['skills']

        self.scenario = scenario
        self.skill_set_id = self.set_skill_set()

        self.skill_indices = self.set_skill_indices()

        # information from history
        self.history_lastAssignedShiftType = None
        self.history_numberOfConsecutiveAssignments = None
        self.history_numberOfConsecutiveDaysOff = None
        self.history_numberOfConsecutiveWorkingDays = None
        self.history_numberOfWorkingWeekends = None

    def set_skill_set(self):
        """
        Function to attach object of skill_set collection to employee
        """
        # find corresponding skill_set object
        for index, skill_set in self.scenario.skill_set_collection.collection.items():
            if self.skills == skill_set.skills_in_set:
                index_to_set = index
                break
        return index_to_set

    def set_skill_indices(self):
        """
        Function to set skill indicies of employee
        """
        return [self.scenario.skills.index(skill) for skill in self.skills]


    def has_skill(self, skill):
        return skill in self.skills

    def is_eligible(self):
        """
        Get employees that can work a certain skill request
        Have the right skill
        Are available on that day
        :return:
        True or False
        """
        return None


