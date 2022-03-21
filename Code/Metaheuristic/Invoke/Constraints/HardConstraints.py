

class RuleCollection:
    """
    A collection of rules. Behaves as a list, which means that iterating over it returns
    the rules.
    """

    def __init__(
            self,
            rules_specs,
            settings,
            days
    ):
        self._collection = {}
        self._initialize_rules(rules_specs, settings, days)
