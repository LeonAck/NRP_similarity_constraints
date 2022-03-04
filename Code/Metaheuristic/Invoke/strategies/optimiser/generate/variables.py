from config import configuration
from dotmap import DotMap

VAR_DEFAULTS = configuration.optimiser.variables


def potential_assignments(solver, employees):
    for employee in employees:
        for shift in employee.eligible_shifts_in_schedule:
            solver.create_variable(
                id=VAR_DEFAULTS.assignment.id(employee, shift),
                lower_bound=VAR_DEFAULTS.assignment.lower_bound(employee, shift),
                upper_bound=VAR_DEFAULTS.assignment.upper_bound,
            )

def set_initial_solution(solver, initial_solution):
    start_solution = []
    for initial_solution_var in initial_solution:
        start_solution.append((solver.find_variable(
            VAR_DEFAULTS.assignment.id(DotMap({"id": initial_solution_var.user_id}),
                                       DotMap({"id": initial_solution_var.shift_id}))), initial_solution_var.value))
    solver.set_initial_solution(start_solution)

def set_assignment_objectives(solver, employees, settings, travel_expenses):

    for employee in employees:
        for shift in employee.unfixed_eligible_shifts_in_schedule:
            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
            if var:
                shift_cost = 0
                if shift.shift_cost:
                    shift_cost = shift.shift_cost
                var.obj = var.obj + shift_cost

    if settings.cost_objective > 0:
        for employee in employees:
            for shift in employee.unfixed_eligible_shifts_in_schedule:
                var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                if var:
                    pay_duration = shift.pay_duration
                    if len(employee.employee_pay_penalties) > 0:
                        penalty = employee.get_penalty(shift)
                        pay_duration = pay_duration * penalty

                    travel_expense = 0
                    if settings.use_travel_expenses:
                        employee_postal_code = employee.postal_code
                        shift_postal_code = shift.postal_code
                        if travel_expenses.get(employee_postal_code):
                            for postal_code in travel_expenses[employee_postal_code]:
                                if shift_postal_code == postal_code['postal_code']:
                                    travel_expense = postal_code['travel_expenses']
                                    break
                    var.obj = var.obj + round(
                        shift.pay_multiplication_factor * employee.hourly_rate / 60 * pay_duration * settings.cost_objective,
                        0) + 2 * travel_expense * settings.cost_objective

    if settings.proficiency_objective > 0:
        for employee in employees:
            for shift in employee.unfixed_eligible_shifts_in_schedule:
                shiftAllocVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                proficiencyScore = 0
                if len(shift.subshifts) > 0:
                    for subShift_index in range(0, len(shift.subshifts)):
                        subShift = shift.subshifts[subShift_index]
                        for department in employee.departments:
                            if department.proficiency_rating and department.id == subShift.department_id:
                                if not settings.use_proficiency_per_hour:
                                    proficiencyScore += department.proficiency_rating
                                else:
                                    proficiencyScore += (department.proficiency_rating * subShift.pay_duration / 60)
                else:
                    for department in employee.departments:
                        if department.proficiency_rating and department.id == shift.department_id:
                            if not settings.use_proficiency_per_hour:
                                proficiencyScore += department.proficiency_rating
                            else:
                                proficiencyScore += (department.proficiency_rating * subShift.pay_duration / 60)

                if shiftAllocVar and proficiencyScore > 0:
                    shiftAllocVar.obj = shiftAllocVar.obj - 1 * proficiencyScore * settings.proficiency_objective

        # Skill Proficiency rating of shifts
    if settings.skill_objective > 0:
        for employee in employees:
            for shift in employee.unfixed_eligible_shifts_in_schedule:
                shiftAllocVar = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                proficiencyScore = 0
                for employeeSkill in employee.skills:
                    for shiftSkill in shift.shift_skills:
                        if employeeSkill.level > 0 and employeeSkill.id == shiftSkill.id:
                            proficiencyScore += int(employeeSkill.level)

                if shiftAllocVar and proficiencyScore > 0:
                    shiftAllocVar.obj = shiftAllocVar.obj + 1 * proficiencyScore * settings.skill_objective

def works_on_off(solver, employees, days):
    for day in days:
        for employee in employees:
            solver.create_variable(
                id=VAR_DEFAULTS.works_on.id(employee, day),
                lower_bound=VAR_DEFAULTS.works_on.lower_bound,
                upper_bound=VAR_DEFAULTS.works_on.upper_bound,
            )
            solver.create_variable(
                id=VAR_DEFAULTS.is_off.id(employee, day),
                lower_bound=VAR_DEFAULTS.is_off.lower_bound,
                upper_bound=VAR_DEFAULTS.is_off.upper_bound,
            )
