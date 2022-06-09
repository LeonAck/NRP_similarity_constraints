from Domain.employee import EmployeeCollection
import numpy as np


class RuleCollection:
    """
    A collection of rules. Behaves as a dictionary
    """

    def __init__(
            self,
            rules=None
    ):
        self.collection = {}
        if rules is not None:
            rules = EmployeeCollection().create_dict_from_list(rules)
        else:
            rules = {}

        self.collection = rules

    def __len__(self):
        return len(self.collection)

    def initialize_rules(self, Rules, rules_specs, employees):
        """
        Initializes the rule objects that are to be stored in the RuleCollection.
        """
        import sys
        for rule_id, rule_spec in rules_specs.items():
            if rule_spec['is_active']:
                try:
                    class_ = getattr(Rules, 'Rule' + rule_id)
                    # split later
                    self.collection[rule_id] = class_(employees=employees, rule_spec=rule_spec)

                except Exception as e:
                    raise type(e)(str(e) +
                                  ' seems to trip up the import of rule with ID = ' + rule_id).with_traceback(
                        sys.exc_info()[2])

        self.soft_rule_collection = self.collect_soft_rules()

        # collect rules for which the swap operator is relevant
        self.soft_rule_swap_collection = RuleCollection([rule for rule in self.collection.values() if not rule.is_mandatory and rule.swap])

        if self.soft_rule_collection.collection:
            self.penalty_array = self.create_penalty_array()

        return self

    def collect_soft_rules(self):
        """
        Function to collect soft rules
        """
        return RuleCollection([rule for rule in self.collection.values() if not rule.is_mandatory])

    def create_penalty_array(self):
        """
        Function to create an array of penalties
        """
        return np.array([rule.penalty for rule in self.soft_rule_collection.collection.values()])

    def collect_incremental_violations(self, current_assignment, new_assignment):
        """
        Function to collect violations from change in array
        :return:
        array
        """

class Rule:

    def __init__(self, employees, rule_spec=None):
        if rule_spec:
            self.id = rule_spec["id"]
            self.is_active = rule_spec["is_active"]
            self.is_mandatory = rule_spec["is_mandatory"]
            self.penalty = rule_spec["penalty"]
            self.is_horizontal = rule_spec["is_horizontal"]
            self.swap = rule_spec['swap']
            if rule_spec["parameter_per_contract"]:
                self.parameter_per_employee = self.get_parameter_per_employee(employees,
                                                                              rule_spec['parameter_1'])
            elif rule_spec['parameter_per_s_type']:
                self.parameter_per_s_type = rule_spec['parameter_2']
            else:
                self.parameter_1 = rule_spec['parameter_1']

    def check_if_violation(self, number_of_violations):
        """
        Function to put number of rule violations in output_files
        """

        return number_of_violations > 0

    def get_parameter_per_employee(self, employees, contract_parameter_dict):
        """
        Function to create dictionary where employee id is linked ot parameter
        :return:
        dictionary
        """
        parameter_dict = {}
        for employee in employees._collection.values():
            parameter_dict[employee.id] = contract_parameter_dict[employee.contract_type]

        return parameter_dict





