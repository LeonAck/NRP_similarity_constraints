class RuleCollection:
    """
    A collection of rules. Behaves as a dictionary
    """

    def __init__(
            self,
            rules_specs,
    ):
        self.collection = {}
        self._initialize_rules(rules_specs)

    def _initialize_rules(self, rules_specs):
        """
        Initializes the rule objects that are to be stored in the RuleCollection.
        """
        import sys
        try:
            for rule_spec in rules_specs:
                id = None
                rule_object = Rule(rule_spec)
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of rule with ID = ' + rule_spec.get("rule_id", "'missing id'")).with_traceback(
                sys.exc_info()[2])

class Rule:

    def __init__(self, rules_spec):
        self.is_active = None
        self.is_mandatory = None
        self.penalty = None

    def check_if_violation(self, number_of_violations):
        """
        Function to put number of rule violations in output
        """

        return number_of_violations > 0
