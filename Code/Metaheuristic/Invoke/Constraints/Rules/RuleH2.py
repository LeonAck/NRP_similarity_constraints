from Invoke.Constraints.initialize_rules import Rule

class RuleH3(Rule):
    """
    Rule that checks for understaffing.
    Compares skill request to number of nurses with that skill assigned to shift
    """
    def __init__(self, rules_spec):
        super().__init__(rules_spec)