from config import configuration
VAR_DEFAULTS = configuration.optimiser.variables
CONSTR_DEFAULTS = configuration.optimiser.constraints
RULES_DEFAULTS = configuration.optimiser.rules


def generate_shifts_output(solver, employees, settings, travel_expenses):
    assigned = 0
    shifts_output = []
    for employee in employees:
        for shift in employee.eligible_shifts_in_schedule:
            assignment_var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
            if assignment_var and round(assignment_var.x) > 0:
                assigned += int(not shift.is_fixed)
                shift_output_item = shift.generate_standard_output(employee)

                shift_output_item['shift_costs'] = round((shift.pay_duration * shift.pay_multiplication_factor * employee.hourly_rate) / 60)
                if len(shift.subshifts) > 0 and settings.add_subshifts_to_output:
                    shift_output_item['subshifts'] = []
                    for subshift in shift.subshifts:
                        subShiftData = {
                            "start": subshift.start,
                            "finish": subshift.end
                        }
                        if subshift.department_id:
                            subShiftData['department_id'] = subshift.department_id
                        if subshift.id:
                            subShiftData['id'] = subshift.id
                        shift_output_item['subshifts'].append(subShiftData)
                if len(shift.breaks) > 0:
                    shift_output_item['breaks'] = []
                    for b in shift.breaks:
                        shift_output_item['breaks'].append({
                            "start": b.start,
                            "finish": b.end
                        })
                pay_duration = shift.pay_duration
                if len(employee.employee_pay_penalties) > 0:
                    penalty = employee.get_penalty(shift)
                    pay_duration = pay_duration * penalty
                shift_output_item['shift_costs'] = round((pay_duration * shift.pay_multiplication_factor * employee.hourly_rate) / 60)
                if shift.group_id != None:
                    shift_output_item['group_id'] = shift.group_id
                if settings.use_travel_expenses:
                    shift_output_item['travel_expenses'] = _calculate_travel_expenses(shift, employee, travel_expenses)
                shifts_output.append(shift_output_item)
    print ('Shift assigned', assigned)
    return shifts_output

def generate_unassigned_shifts_output(solver, domain):
    unassigned_shifts_output = []
    for shift in domain.shifts.get_non_fixed_shifts().get_shifts_starts_in_interval(domain.settings.start, domain.settings.end):
        if not any([solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x == 1 for employee in domain.employees]):
            unassigned_shifts_output.append(shift.generate_standard_output())
    return unassigned_shifts_output

def _calculate_travel_expenses(shift, shift_employee, travel_expenses):
    #why is this necessary @Jeroen?
    # if not shift_employee:
    #     for employee in employees:
    #         if employee.id == shift.employee_id:
    #             shift_employee = employee

    employee_postal_code = shift_employee.postal_code
    shift_postal_code = shift.postal_code
    travel_expense = 0
    if travel_expenses:
        for postal_code in travel_expenses[employee_postal_code]:
            if shift_postal_code == postal_code['postal_code']:
                travel_expense = postal_code['travel_expenses']
                break
    return travel_expense