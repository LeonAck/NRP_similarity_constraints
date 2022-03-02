from strategies.k_opt_heuristic import KOptHeuristic
from strategies.optimiser import Optimiser
from strategies.shifting_window_heuristic import ShiftingWindowHeuristic
from strategies.combined_heuristic import CombinedHeuristic
from strategies.skill_group_optimiser import SkillGroupOptimiser

class Strategies(object):
    def __init__(self, domain):
        self.domain = domain

    def get_strategy(self):
        if self.domain.settings.run_combined_heuristic:
            return CombinedHeuristic(self.domain)
        elif self.domain.settings.improve_results:
            return KOptHeuristic(self.domain)
        elif self.domain.settings.run_shifting_window:
            return ShiftingWindowHeuristic(self.domain)
        else:
            if not self.domain.settings.split_skills:
                return Optimiser(self.domain)
            else:
                return SkillGroupOptimiser(self.domain)
