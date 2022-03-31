from Invoke.Constraints.initialize_rules import Rule
import numpy as np

class RuleS1(Rule):
    """
        Rule that checks for optimal coverage per skill request
        Compares optimal skill request to number of nurses with that skill assigned to shift
    """

    def __init__(self, rule_spec=None):
        super().__init__(rule_spec)
