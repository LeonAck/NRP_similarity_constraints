from strategies.optimiser import Optimiser
from domain.initialSolutionVar import initialSolutionVar
import random
import time
import math
import multiprocessing
from domain.employee import EmployeeCollection
from domain.shift import ShiftCollection

class KOptHeuristic(object):
    def __init__(self, domain):
        self.domain = domain
        self.travel_expenses_matrix = domain.travel_expenses_matrix
        self.shifts = domain.shifts
        self.employees = domain.employees
        self.rules = domain.rules
        self.settings = domain.settings
        self.days = domain.days
        self.shift_type_definitions = domain.shift_type_definitions
        self.assignments = {}

        #make sure not all employees are copied each time when passing domain to optimsiser
        self.domain.shifts = None
        self.domain.employees = None

    def find_solution(self):
        self.start_time = time.time()

        # 0-opt: create-initial solution
        for employee in self.employees:
            shifts_for_employee = ShiftCollection(self.get_shifts_for_employee([employee]))
            if len(shifts_for_employee) > 0:
                result = self.run_optimiser(EmployeeCollection([employee]), shifts_for_employee)

                if result['result'] == 1:
                    self.update_assigned_shifts(result)
                    self.update_assignments([employee], result)

        # 1-opt
        improvement_stats = {"1_opt_finished": False, "1_opt_iterations": 0, "1_opt_optimal": 0, "1_opt_skipped": 0}
        for employee in self.employees:

            elapsed = time.time() - self.start_time
            if elapsed > self.settings.improve_time_limit:
                improvement_stats["1_opt_iterations"] = str(improvement_stats["1_opt_iterations"]) + "/" + str(
                    len(self.employees))
                return self.get_full_output(improvement_stats,elapsed)

            shifts_for_employee = self.get_shifts_for_employee([employee])
            unassigned_shifts = self.get_unassigned_shifts([employee])
            shifts_for_problem = ShiftCollection(shifts_for_employee + unassigned_shifts)
            if len(shifts_for_problem) > 0:
                result = self.run_optimiser(EmployeeCollection([employee]), shifts_for_problem)
                self.incr_opt_key_dict(improvement_stats, "iterations")

                if result['result'] == 1:
                    self.update_assigned_shifts(result)
                    self.update_assignments(EmployeeCollection([employee]), result)
                    self.incr_opt_key_dict(improvement_stats, "optimal")
            else:
                self.incr_opt_key_dict(improvement_stats, "skipped")

        improvement_stats["1_opt_finished"] = True
        improvement_stats["1_opt_iterations"] = str(improvement_stats["1_opt_iterations"]) + "/" + str(len(self.employees))

        ##2-opt
        improvement_stats.update(
            {"2_opt_finished": False,
             "2_opt_iterations": 0,
             "2_opt_within_gap": 0,
             "2_opt_optimal": 0,
             "2_opt_skipped": 0,
             "2_opt_employees": {}})
        for employee in self.employees:
            improvement_stats["2_opt_employees"][employee.id] = {"iterations": 0, "within_gap": 0, "optimal": 0, "skipped": 0}

        nbr_iterations = int((len(self.employees) - 1) * (len(self.employees) )/ 2)
        batch_start = 0
        batch_size = nbr_iterations
        if self.settings.batch_size:
            batch_size = self.settings.batch_size
        while True:
            elapsed = time.time() - self.start_time
            if batch_start >= nbr_iterations or elapsed > self.settings.improve_time_limit:
                break
            batch_end = batch_start + batch_size
            if batch_end > nbr_iterations:
                batch_end = nbr_iterations

            ##if batch size declared, activate termination after time limit
            if self.settings.batch_size:
                manager = multiprocessing.Manager()
                improvement_stats_manager = manager.dict()
                output = manager.dict()
                p = multiprocessing.Process(target=self.run_2_opt_batch, args=(range(batch_start,batch_end), improvement_stats, improvement_stats_manager, output))
                p.start()
                time_limit_batch = min(self.settings.improve_time_limit - elapsed + self.settings.runtime, (self.settings.runtime + 0.1) * batch_size)
                time_limit_batch = max(1, time_limit_batch)
                p.join(time_limit_batch)

                if p.is_alive():
                    p.terminate()

                if 'assignments' in output:
                    for employee_id in output['assignments']:
                        self.assignments[employee_id] = output['assignments'][employee_id]
                    for shift in [shift for shift in self.shifts if not shift.is_fixed]:
                        shift.employee_id = output['shifts'][shift.id]
                    improvement_stats = improvement_stats_manager["body"]
            else:
                self.run_2_opt_batch(range(batch_start,batch_end), improvement_stats)
            batch_start += batch_size

        improvement_stats["2_opt_finished"] = True
        improvement_stats["2_opt_iterations"] = str(improvement_stats["2_opt_iterations"]) + "/" + str(nbr_iterations)

        elapsed = time.time() - self.start_time
        return self.get_full_output(improvement_stats,elapsed)

    def run_2_opt_batch(self, batch_range, improvement_stats, improvement_stats_manager ={},output_file={}):

        for counter in batch_range:
            elapsed = time.time() - self.start_time
            if elapsed > self.settings.improve_time_limit:
                improvement_stats_manager["body"] = improvement_stats
                output_file["assignments"] = self.assignments
                output_file["shifts"] = self.make_shift_dict(self.shifts)
                return

            i = counter % len(self.employees)
            j = (i + math.floor(counter / len(self.employees)) + 1) % len(self.employees)

            employee_i = self.employees[i]
            employee_j = self.employees[j]

            shifts_for_employees = self.get_shifts_for_employee([employee_i, employee_j])
            unassigned_shifts = self.get_unassigned_shifts([employee_i, employee_j])
            shifts_for_problem = ShiftCollection(shifts_for_employees + unassigned_shifts)
            employee_collection = EmployeeCollection([employee_i, employee_j])
            has_shared_shifts = employee_collection.check_shared_shifts(shifts_for_problem)
            if len(shifts_for_problem) > 0 and has_shared_shifts:
                result = self.run_optimiser(employee_collection, shifts_for_problem)
                self.incr_opt_key_dict(improvement_stats, "iterations", [employee_i.id, employee_j.id])

                lower_bound = result["lower_bound"] if result["lower_bound"] != 0 else 1e-8
                if result['result'] in [1, 3] and (result['upper_bound'] - lower_bound) / lower_bound <= self.settings.acceptance_gap_improvement or \
                        result['result'] == 1:
                    self.update_assigned_shifts(result)
                    self.update_assignments([employee_i, employee_j], result)
                    self.incr_opt_key_dict(improvement_stats, "within_gap", [employee_i.id, employee_j.id])
                    if result['result'] == 1:
                        self.incr_opt_key_dict(improvement_stats, "optimal", [employee_i.id, employee_j.id])
            else:
                self.incr_opt_key_dict(improvement_stats, "skipped", [employee_i.id, employee_j.id])

        improvement_stats_manager["body"] = improvement_stats
        output_file["assignments"] = self.assignments
        output_file["shifts"] = self.make_shift_dict(self.shifts)

    def incr_opt_key_dict(self, dictionary, key, employees=None):
        if employees:
            dictionary["2_opt_" + key] += 1
            dictionary["2_opt_employees"][employees[0]][key] += 1
            dictionary["2_opt_employees"][employees[1]][key] += 1
        else:
            dictionary["1_opt_" + key] += 1

    def make_shift_dict(self, shifts):
        shift_dic = {}
        for shift in shifts:
            shift_dic[shift.id] = shift.employee_id
        return shift_dic

    def update_assignments(self, employee_list, result):
        if len(result['shifts']) == 0:
            return
        for employee in employee_list:
            self.assignments[str(employee.id)] = {"shifts": [], "rule_violations": []}
        for assigned_shift in result['shifts']:
            shift_user_id = str(assigned_shift['user_id'])
            self.assignments[shift_user_id]['shifts'].append(assigned_shift)
        for rule_violation in result['rule_violations']:
            if 'user_id' in rule_violation:
                rule_violation_user_id = str(rule_violation['user_id'])
                self.assignments[rule_violation_user_id]['rule_violations'].append(rule_violation)

    def get_shifts_for_employee(self, employee_list):
        return [shift for employee in employee_list for shift in self.shifts if
                str(shift.employee_id) == str(employee.id)]

    def get_unassigned_shifts(self, employee_list):
        unassigned_shifts = [shift for shift in self.shifts if shift.employee_id is None and any(employee.is_eligible(shift) for employee in employee_list)]
        if len(unassigned_shifts) > self.settings.number_of_unassigned_shifts:
            unassigned_shifts = random.sample(unassigned_shifts, self.settings.number_of_unassigned_shifts)
        return unassigned_shifts

    def update_assigned_shifts(self, result):
        assigned_shifts = result['shifts']
        rule_violations = result['rule_violations']
        if len(assigned_shifts) == 0:
            return
        for shift in self.shifts:
            for assigned_shift in assigned_shifts:
                if str(assigned_shift['shift_id']) == str(shift.id):
                    shift.employee_id = assigned_shift['user_id']
                    break
            for rule_violation in rule_violations:
                if str(rule_violation['rule_id']) == "1":
                    if str(rule_violation['shift_id']) == str(shift.id):
                        shift.employee_id = None

    def run_optimiser(self, employees, shifts):
        self.domain.initial_solution = self.create_initial_solution(employees)
        optimiser = Optimiser(domain=self.domain, employees=employees, shifts=shifts)
        if any([str(rule_id) in ["60", "62"] for rule_id in self.rules]):
            output_results = optimiser.find_solution([employee for employee in self.employees if not employee in employees],
                                [shift for shift in self.shifts if not shift in shifts and shift.employee_id])
        else:
            output_results = optimiser.find_solution()
        optimiser.solver.clear()
        return output_results

    def create_initial_solution(self, employees):
        initial_solution = []
        for employee in employees:
            if str(employee.id) in self.assignments:
                for shift in self.assignments[str(employee.id)]['shifts']:
                    initial_solution.append(initialSolutionVar({'shift_id': str(shift['shift_id']), "user_id": str(employee.id), "value": 1}))
        return initial_solution

    def get_final_unassigned_shifts(self, final_assignments):
        unassigned_shifts = []
        for shift in self.shifts:
            if not shift.is_fixed:
                for assigned_shift in final_assignments:
                    if str(shift.id) == str(assigned_shift['shift_id']):
                        break
                else:
                    unassigned_shifts.append(
                        {
                            "rule_id": "1",
                            "shift_id": shift.id,
                            "violation_costs": self.rules["1"][0].penalty,
                            "date": shift.start,
                            "shift_start": shift.start,
                            "shift_finish": shift.end,
                            "department_id": str(shift.department_id)
                        }
                    )
        return unassigned_shifts

    def get_full_output(self, improvement_stats, runtime):
        full_output = {}
        full_output_assignments = []
        full_output_rule_violations = []
        for employee_id in self.assignments:
            full_output_assignments += self.assignments[employee_id]['shifts']
            full_output_rule_violations += self.assignments[employee_id]['rule_violations']

        unassigned_shifts = self.get_final_unassigned_shifts(full_output_assignments)

        full_output_rule_violations += unassigned_shifts

        full_output['result'] = 1
        full_output['goal_score'] = 0
        full_output['shifts'] = full_output_assignments
        full_output['rule_violations'] = full_output_rule_violations

        technical_kpis = {"runtime": runtime, "use_improvement_heuristic": True,
                          "improvement_heuristic": improvement_stats}
        full_output["technical_kpis"] = technical_kpis
        return full_output
