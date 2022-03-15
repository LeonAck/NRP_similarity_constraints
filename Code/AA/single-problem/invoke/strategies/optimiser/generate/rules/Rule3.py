from strategies.optimiser.generate.rules.Rule30 import Rule30

class Rule3:
    def __init__(self, rule):
        # Max consecutive shifts constraint, porting to rule 30
        self.rule = rule
        self.rule.id = "3"
        self.rule.parameter3 = self.rule.parameter1 + 1

    def set_rule(self, solver, domain):
        rule_30 = Rule30(self.rule)
        rule_30.set_rule(solver, domain)

    def add_violation_to_output(self, solver, domain, output):
        rule_30 = Rule30(self.rule)
        rule_30.add_violation_to_output(solver, domain, output)