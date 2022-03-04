from config import constants, configuration
CONSTANTS = constants
VAR_DEFAULTS = configuration.optimiser.variables
CONSTR_DEFAULTS = configuration.optimiser.constraints


def shift_assignment(solver, employees, shifts, settings):
    for shift in shifts.get_non_fixed_shifts().get_shifts_starts_in_interval(
            settings.start, settings.end):
        assignment_vars = [
            (1,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
            for employee in employees.get_shift_eligible_employees(shift)
        ]
        solver.create_slacked_constraint(
            id=CONSTR_DEFAULTS.shift_assignment.id(shift, "1"),
            constraint_lhs=assignment_vars,
            constraint_sense="==",
            constraint_rhs=1,
            slack_lower_bound=0,
            slack_upper_bound=1,
            slack_constraint_coeff=1,
            slack_objective_coeff=0
        )

def works_on_off(solver, employees, days):
    for employee in employees:
        for day in days:
            if len(employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date, day.date + CONSTANTS.time.seconds_per_day)) > 0:
                is_off_var = solver.find_variable(VAR_DEFAULTS.is_off.id(employee, day))
                works_on_var = solver.find_variable(VAR_DEFAULTS.works_on.id(employee, day))

                assignment_vars_positive = [(1,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                                  for shift in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date, day.date + CONSTANTS.time.seconds_per_day)]
                assignment_vars_negative = [(-1,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))
                                  for shift in employee.eligible_shifts_in_schedule.get_shifts_starts_in_interval(day.date, day.date + CONSTANTS.time.seconds_per_day)]

                # works on constraint
                assignment_vars_negative.append((1000,works_on_var))
                solver.create_slacked_constraint(
                    CONSTR_DEFAULTS.works_on.id(employee, day),
                    assignment_vars_negative,
                    '>=',
                    0
                )

                assignment_vars_positive.append((1000, is_off_var))
                solver.create_slacked_constraint(
                    CONSTR_DEFAULTS.is_off.id(employee, day),
                    assignment_vars_positive, '<=', 1000
                )
                solver.create_slacked_constraint(
                    CONSTR_DEFAULTS.equality_works_on_off.id(employee, day),
                    [(1, is_off_var), (1, works_on_var)], '==', 1
                )

def disallow_employee_mix(solver, employees):
    for employee in employees:
        non_exclusion_list = []
        exclusion_list = []
        for shift in employees.fixed_shifts:
            for employee_2 in employees.exclude_employee(employee):
                if len(employee_2.fixed_shifts.get_shifts_starts_in_interval(shift.start, shift.end)) > 0 and employee_2 not in non_exclusion_list:
                    non_exclusion_list.append(employee_2)
                else:
                    exclusion_list.append(employee_2)

        if len(exclusion_list) < len(employees):
            for shift in employee.eligible_shifts_in_schedule:
                left_hand_side = [(100,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)))]
                for employee_2 in exclusion_list:
                    for shift_2 in employee_2.eligible_shifts_in_schedule.get_shifts_starts_in_interval(shift.start, shift.end).exclude_shift(shift):
                        left_hand_side.append((1,solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift_2))))

                solver.create_slacked_constraint(
                    CONSTR_DEFAULTS.disallow_employee_mix.id(employee, shift),
                    left_hand_side, '<=', 100
                )
