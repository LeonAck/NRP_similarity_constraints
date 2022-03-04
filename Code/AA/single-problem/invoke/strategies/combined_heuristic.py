from strategies.shifting_window_heuristic import ShiftingWindowHeuristic
from strategies.k_opt_heuristic import KOptHeuristic


def get_technical_kpis(shifting_window_result, k_opt_result):
    return {**shifting_window_result['technical_kpis'], **k_opt_result['technical_kpis'],
            'runtime': shifting_window_result['technical_kpis']['runtime'] + k_opt_result['technical_kpis']['runtime']}


class CombinedHeuristic(object):
    def __init__(self, domain):
        self.domain = domain

    def find_solution(self):
        """
        Get initially fixed shifts, needed in order to keep those fixed
        when going into the Improvement Heuristic phase. Since the option
        for switching off certain rules in the Shifting Window Heuristic
        is supported, we need to store the list of rules that were added
        initially, so that we can use them during the Improvement Heuristic
        """

        initially_fixed_shift_ids = self.get_fixed_shift_ids()
        self.set_shifting_window_rules()

        """
        Next, we run the Shifting Window Heuristic
        """
        shifting_window_heuristic = ShiftingWindowHeuristic(self.domain)
        shifting_window_result = shifting_window_heuristic.find_solution()

        """
        Shifts that were not fixed initially and that were fixed
        by the Shifting Window Heuristic need to be unfixed again.
        """
        self.prepare_k_opt_problem(shifting_window_result, initially_fixed_shift_ids)
        self.set_rules_to_active()

        """
        We now run the Improvement Heuristic on the results
        of the Shifting Window Heuristic
        """
        k_opt_heuristic = KOptHeuristic(self.domain)
        result = k_opt_heuristic.find_solution()

        result['technical_kpis'] = get_technical_kpis(shifting_window_result, result)

        if self.domain.settings.return_shifting_window_results:
            result['shifting_window_result'] = shifting_window_result
            del shifting_window_result['technical_kpis']

        return result

    def prepare_k_opt_problem(self, shifting_window_result, initially_fixed_shift_ids):
        for result_shift in shifting_window_result['shifts']:
            matching_input_shift = next(shift for shift in self.domain.shifts if result_shift['shift_id'] == shift.id)
            if matching_input_shift.id not in initially_fixed_shift_ids:
                matching_input_shift.is_fixed = False
                matching_input_shift.employee_id = result_shift['user_id']

    def get_fixed_shift_ids(self):
        return [shift.id for shift in self.domain.shifts if shift.is_fixed]

    def set_shifting_window_rules(self):
        self.domain.rules.set_shifting_window_rules()

    def set_rules_to_active(self):
        self.domain.rules.set_rules_to_active()
