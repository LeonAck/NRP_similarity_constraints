from config import configuration
from strategies.optimiser.generate.rules.Rule30 import Rule30

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

# Rule 7: Maximum work domain.days in payperiod
class Rule7:
    def __init__(self, rule):
        # Max consecutive shifts constraint, porting to rule 30
        self.rule = rule
        self.rule.id = "7"
        self.rule.parameter4 = self.rule.parameter3

    def set_rule(self, solver, domain):
        rule_30 = Rule30(self.rule)
        rule_30.set_rule(solver, domain)

    def add_violation_to_output(self, solver, domain, output):
        rule_30 = Rule30(self.rule)
        rule_30.add_violation_to_output(solver, domain, output)
