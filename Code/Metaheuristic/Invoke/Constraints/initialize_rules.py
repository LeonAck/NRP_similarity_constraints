from Domain.employee import EmployeeCollection
from Invoke.Constraints import Rules

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
                print("hi")
            except Exception as e:
                raise type(e)(str(e) +
                              ' seems to trip up the import of rule with ID = ' + rule_spec.get("rule_id", "'missing id'")).with_traceback(
                    sys.exc_info()[2])
        return self

    def collect_soft_rules(self):
        """
        Function to collect soft rules
        """
        # look at AA

    def collect_incremental_violations(self, current_assignment, new_assignment):
        """
        Function to collect violations from change in array
        :return:
        array
        """

class Rule:

    def __init__(self, rule_spec=None):
        self.is_active = True
        self.is_mandatory = True
        self.penalty = None
        self.is_horizontal = True

    def check_if_violation(self, number_of_violations):
        """
        Function to put number of rule violations in output
        """

        return number_of_violations > 0
