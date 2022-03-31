from Domain.employee import EmployeeCollection
from Invoke.Constraints import Rules
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
        #self._initialize_rules(rules_specs)
        if rules is not None:
            rules = EmployeeCollection().create_dict_from_list(rules)
        else:
            rules = {}

        self.collection = rules

    def __len__(self):
        return len(self.collection)

    def initialize_rules(self, rules_specs):
        """
        Initializes the rule objects that are to be stored in the RuleCollection.
        """
        import sys
        for rule_spec in rules_specs:
            try:
                class_ = getattr(Rules, 'Rule'+rule_spec['id'])
                # split later
                self.collection[rule_spec['id']] = class_(rule_spec=rule_spec)

            except Exception as e:
                raise type(e)(str(e) +
                              ' seems to trip up the import of rule with ID = ' + rule_spec.get("rule_id", "'missing id'")).with_traceback(
                    sys.exc_info()[2])

        self.soft_rule_collection = self.collect_soft_rules()

        if self.soft_rule_collection.collection:
            self.penalty_array = self.create_penalty_array()

        # self.collection["S1"].incremental_violation_change(self, change_info=None)

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

    def __init__(self, rule_spec=None):
        if rule_spec:
            self.id = rule_spec["id"]
            self.is_active = rule_spec["is_active"]
            self.is_mandatory = rule_spec["is_mandatory"]
            self.penalty = rule_spec["penalty"]
            self.is_horizontal = rule_spec["is_horizontal"]

    def check_if_violation(self, number_of_violations):
        """
        Function to put number of rule violations in output
        """

        return number_of_violations > 0
