# Rule 5: minimum break time after shift of type parameter3 if shift ends after parameter4 minutes after midnight
from mip import xsum
from config import constants, configuration
from strategies.optimiser.output import Violation

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables


class Rule5:
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        min_break_length = self.rule.parameter1
        max_time_between_shifts = self.rule.parameter2
        shift_type_to_check_from = self.rule.parameter3 if self.rule.parameter3 else None
        end_after = self.rule.parameter4 if self.rule.parameter4 else None
        exclude_shifts_same_day = self.rule.parameter5 if self.rule.parameter5 else None
        shift_type_to_check_to = self.rule.parameter6 if self.rule.parameter6 else None
        for employee in domain.employees.get_rule_applicable_employees(self.rule):
            min_break_length = employee.minimum_break_length if employee.minimum_break_length else min_break_length
            for shift_i in employee.eligible_shifts_in_schedule.get_shifts_of_type(shift_type_to_check_from).get_rule_applicable_shifts(self.rule):
                if not end_after or (shift_i.end - shift_i.midnight_time_stamp % constants.time.minutes_per_day > end_after * constants.time.seconds_per_minute):
                    lhs_constraint = []
                    make_constraint = False

                    lhs_constraint.append((1000, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_i))))

                    for shift_j in employee.eligible_shifts_in_schedule.get_shifts_of_type(shift_type_to_check_to).get_shifts_starts_in_interval(shift_i.end, shift_i.end + min_break_length * constants.time.seconds_per_minute).get_rule_applicable_shifts(self.rule).exclude_shift(shift_i):
                            if shift_j.start >= shift_i.end and ((not exclude_shifts_same_day) or (exclude_shifts_same_day and shift_i.midnight_time_stamp + constants.time.seconds_per_day < shift_j.start)):
                                gap = (shift_j.start - shift_i.end) / 60
                                # check if the time between the shifts is longer than max_time_between_shifts (otherwise the two shifts are seen 1 split shift) and shorter than the min_break_length
                                if 0 <= gap < min_break_length and (max_time_between_shifts and (
                                        gap > max_time_between_shifts > 0) or max_time_between_shifts == 0):
                                    lhs_constraint.append((1, solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_j))))
                                    make_constraint = True
                            else:
                                break

                    if make_constraint:
                        solver.create_slacked_constraint(
                            id=RULES_DEFAULTS[self.rule.tag].id(employee, shift_i, self.rule.rule_counter),
                            constraint_lhs=lhs_constraint,
                            constraint_sense="<=",
                            constraint_rhs=1000,
                            slack_lower_bound=0,
                            slack_upper_bound=10,
                            slack_constraint_coeff=-int(not self.rule.is_mandatory),
                            slack_objective_coeff=self.rule.penalty * domain.settings.rule_objective
                        )

    def add_violation_to_output(self, solver, domain, output):
        min_break_length = self.rule.parameter1
        max_time_between_shifts = self.rule.parameter2 if self.rule.parameter2 else None
        shift_type_to_check_from = self.rule.parameter3 if self.rule.parameter3 else None
        end_after = self.rule.parameter4 if self.rule.parameter4 else None
        shift_type_to_check_to = self.rule.parameter6 if self.rule.parameter6 else None

        for employee in domain.employees:
            for shift_i in employee.eligible_shifts_in_schedule.get_shifts_of_type(shift_type_to_check_from).get_rule_applicable_shifts(self.rule):
                if not end_after or (shift_i.end - shift_i.midnight_time_stamp % constants.time.minutes_per_day > end_after * constants.time.seconds_per_minute):
                    min_rest_time_between_shifts_slack_var = solver.find_slack_variable_constraint(RULES_DEFAULTS.min_rest_time_between_shifts.id(employee, shift_i, self.rule.rule_counter))
                    if min_rest_time_between_shifts_slack_var and min_rest_time_between_shifts_slack_var.x > 0:
                        violation_shifts = [shift_i]
                        for shift_j in employee.eligible_shifts_in_schedule.get_shifts_of_type(shift_type_to_check_to).get_shifts_starts_in_interval(shift_i.end, shift_i.end + min_break_length * constants.time.seconds_per_minute).get_rule_applicable_shifts(self.rule).exclude_shift(shift_i):
                            shift_j_var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_j))
                            if max_time_between_shifts and max_time_between_shifts > 0 and shift_j.start <= shift_i.end + max_time_between_shifts:
                                continue
                            if shift_j_var and shift_j_var.x > 0:
                                violation_shifts.append(shift_j)
                                break
                        output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                                     shift_id=shift_i.id,
                                                     violation_costs=min_rest_time_between_shifts_slack_var.x * min_rest_time_between_shifts_slack_var.obj,
                                                     user_id=employee.id,
                                                     date=shift_i.start,
                                                     shift_start=shift_i.start,
                                                     shift_finish=shift_i.end,
                                                     department_id=shift_i.department_id,
                                                     relevant_shifts=[shift.id for shift in violation_shifts],
                                                     violation_description=generate_violation_text(min_break_length, shift_type_to_check_from, end_after)))


def generate_violation_text(min_break_length, shift_type_to_check_from, end_after=None):
    of_type_text = ""
    if shift_type_to_check_from:
        of_type_text = "of type {} ".format(shift_type_to_check_from)
    if end_after:
        hours = int(end_after / 60)
        minutes = int(end_after - hours * 60)
        return "Less than {} hours rest after a shift {} ending after {}".format(min_break_length / constants.time.seconds_per_minute, of_type_text, "%02d:%02d" % (hours, minutes))
    else:
        return "Less than {} hours rest after a shift {}".format(min_break_length / constants.time.seconds_per_minute, of_type_text)
