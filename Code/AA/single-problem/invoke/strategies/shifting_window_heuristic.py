from strategies.optimiser import Optimiser
from datetime import datetime, timedelta
import random
from domain.shift import ShiftCollection
from lib.dt import addition_timezone_aware
class ShiftingWindowHeuristic(object):

    def __init__(self, domain):
        self.domain = domain
        self.travel_expenses_matrix = domain.travel_expenses_matrix

    def find_solution(self):
        random.seed(1)
        start_time = datetime.now()

        total_result = {'shifts': [], 'rule_violations': [], 'goal_score': 0, "technical_kpis": {"use_shifting_window": True, "windows_stats": []}}
        day_last = addition_timezone_aware(self.domain.days[-1].date_time, timedelta(days=1),self.domain.settings.time_zone)
        all_shifts = self.domain.shifts.get_shifts_by_filter(lambda shift: shift.start >= self.domain.days[0].date)
        initially_fixed_shifts = all_shifts.get_shifts_by_filter(lambda shift: shift.is_fixed).get_shifts_starts_in_interval(self.domain.days[0].date_time, day_last)

        for window_start_day in self.domain.days.get_start_days_for_steps(self.domain.settings.fix_window_day_size):
            window_end = addition_timezone_aware(window_start_day.date_time, timedelta(days=self.domain.settings.shifting_window_day_size),self.domain.settings.time_zone)
            fix_window_end = addition_timezone_aware(window_start_day.date_time, timedelta(days=self.domain.settings.fix_window_day_size),self.domain.settings.time_zone)
            start_include_shift_period = addition_timezone_aware(window_start_day.date_time, -timedelta(days=self.domain.settings.include_shifts_days),self.domain.settings.time_zone)
            previously_fixed_shifts = all_shifts.get_shifts_starts_in_interval(start_include_shift_period, day_last).get_shifts_by_filter(lambda shift: shift.is_fixed)
            #get open shifts
            iteration_shifts = all_shifts.get_shifts_starts_in_interval(window_start_day.date_time, window_end).get_shifts_by_filter(lambda shift: not shift.is_fixed)


            if len(iteration_shifts) > 0:   #if there are any open shifts
                #add fixed shifts
                iteration_shifts.extend(self.unfix_fixed_shifts(self.domain.settings.fix_drop_ratio, initially_fixed_shifts, previously_fixed_shifts, start_include_shift_period, day_last))
                result = self.run_optimiser(iteration_shifts)
                assigned_shifts = result['shifts']
                self.set_fixed_shifts(assigned_shifts, all_shifts, fix_window_end)
                total_result = self.merge_output(total_result, result, start_include_shift_period.timestamp(), day_last.timestamp(), window_start_day.date, fix_window_end.timestamp())

        self.unfix_all_shifts(initially_fixed_shifts, total_result['shifts'])

        total_result = self.set_unassigned_shift_violations(self.domain.rules, all_shifts, total_result)

        total_result["technical_kpis"]["runtime"] = (datetime.now() - start_time).total_seconds()
        print('TOTAL_ASSIGNED', len(total_result['shifts']))
        return total_result

    def run_optimiser(self, iteration_shifts):
        optimiser = Optimiser(domain=self.domain, shifts=iteration_shifts)
        return optimiser.find_solution()


    def merge_output(self, total_result, shift_fill_result,start_include_shift_period, day_last, window_start, window_end):
        for employee in self.domain.employees:
            assigned_shifts_to_employee = [shift for shift in shift_fill_result['shifts'] if str(shift['user_id']) == str(employee.id) and start_include_shift_period <= shift['start'] <= day_last]
            filtered_total_result = [shift for shift in total_result['shifts'] if not (str(shift['user_id']) == str(employee.id) and start_include_shift_period <= shift['start'] <= day_last)]
            total_result['shifts'] = filtered_total_result + assigned_shifts_to_employee

            rule_violations_for_employee = [rule_violation for rule_violation in shift_fill_result['rule_violations'] if str(rule_violation.get('user_id')) == str(employee.id) and rule_violation.get('date') and start_include_shift_period <= rule_violation.get('date') <= day_last]
            filtered_total_result = [rule_violation for rule_violation in shift_fill_result['rule_violations'] if not(str(rule_violation.get('user_id')) == str(employee.id) and rule_violation.get('date') and start_include_shift_period <= rule_violation.get('date') <= day_last)]
            total_result['rule_violations'] = filtered_total_result + rule_violations_for_employee

        assigned_shift_ids = [str(shift['shift_id']) for shift in total_result['shifts']]
        total_result['rule_violations'] = [rule_violation for rule_violation in total_result['rule_violations'] if not (str(rule_violation['rule_id']) == "1" and str(rule_violation['shift_id']) in assigned_shift_ids)]

        total_result["technical_kpis"]["windows_stats"].append({"start": window_start, "finish": window_end, "mip_gap": shift_fill_result["technical_kpis"]["mip_gap"], "runtime": shift_fill_result["technical_kpis"]["runtime"]})

        return total_result

    def get_previous_window(self, window_start, window_size):
        previous_window_start = window_start - int(timedelta(days=window_size).total_seconds())
        previous_window_end = window_start
        return previous_window_start, previous_window_end

    def get_open_shifts_within_period(self, shifts, window_start, window_end):
        return [shift for shift in shifts if window_start <= shift.start < window_end and not shift.is_fixed]

    def get_fixed_shifts(self, shifts, window_start, window_end):
        return [shift for shift in shifts if shift.is_fixed and window_start <= shift.start < window_end]

    def set_fixed_shifts(self, assigned_shifts, all_shifts, window_end):
        for assigned_shift in assigned_shifts:
            for shift in all_shifts:
                if assigned_shift['shift_id'] == shift.id:
                    if shift.start_datetime < window_end:
                        shift.is_fixed = True
                        shift.employee_id = assigned_shift['user_id']
                        break

    def set_final_fixed_shifts(self, result_shifts, all_shifts):
        for result_shift in result_shifts:
            for shift in all_shifts:
                if result_shift['shift_id'] == shift.id:
                    result_shift['is_fixed'] = True
                    result_shift['user_id'] = result_shift['user_id']
                    break
        return result_shifts

    def unfix_fixed_shifts(self, drop_ratio, initially_fixed_shifts, previously_fixed_shifts, window_start, window_end):
        for fixed_shift in previously_fixed_shifts:
            if fixed_shift not in initially_fixed_shifts:
                random_number = random.uniform(0, 1)
                if random_number <= self.computed_drop_ratio(drop_ratio, fixed_shift.start_datetime, window_start, window_end):
                    fixed_shift.employee_id = None
                    fixed_shift.is_fixed = False
        return previously_fixed_shifts

    def unfix_all_shifts(self, initially_fixed_shifts, shift_fill_result):
        for fixed_shift in shift_fill_result:
            if fixed_shift['shift_id'] not in [shift.id for shift in initially_fixed_shifts]:
                fixed_shift['is_fixed'] = False
        return shift_fill_result

    def computed_drop_ratio(self, drop_ratio, shift_start, start_window, end_window):
        calculated_drop_ratio = (drop_ratio * ((shift_start - start_window) / (end_window - start_window)))
        return calculated_drop_ratio

    def set_unassigned_shift_violations(self, rules, shifts, shift_fill_result):
        for shift in shifts:
            if not shift.is_fixed:
                for assigned_shift in shift_fill_result['shifts']:
                    if str(assigned_shift['shift_id']) == str(shift.id):
                        break
                else:
                    shift_fill_result = self.set_violation(rules, shift, shift_fill_result)
        return shift_fill_result

    def set_violation(self, rules, shift, shift_fill_result):
        for rule_violation in shift_fill_result['rule_violations']:
            if str(rule_violation['rule_id']) == "1" and str(rule_violation['shift_id']) == str(shift.id):
                break
        else:
            shift_fill_result['rule_violations'].append(
                {
                    "rule_id": "1",
                    "shift_id": shift.id,
                    "violation_costs": rules["1"][0].penalty,
                    "date": shift.start,
                    "shift_start": shift.start,
                    "shift_finish": shift.end,
                    "department_id": str(shift.department_id)
                }
            )
        return shift_fill_result
