from mip import xsum
from config import configuration
from strategies.optimiser.output import Violation
from lib.parse import parse_boolean

RULES_DEFAULTS = configuration.optimiser.rules
VAR_DEFAULTS = configuration.optimiser.variables

class Rule34:
    def __init__(self, rule):
        self.rule = rule

    # penalty if hours per week differ too much from average payperiodminutesmax per week
    def set_rule(self, solver, domain):
        if self.rule.penalty > 0:
            nr_days = int(self.rule.parameter1)
            for employee in domain.employees:
                employeeShifts = [shift for shift in domain.shifts if employee.is_eligible(shift)]
                for index in range(0, len(domain.days), nr_days):
                    start_week = domain.days[index].date
                    if index + nr_days < len(domain.days):
                        end_week = domain.days[index + nr_days].date
                    else:
                        end_week = domain.settings .end
                    employee_payperiod_minutes_max = employee.payperiod_minutes_max
                    avgContractHours = employee_payperiod_minutes_max / (28/nr_days)
                    shifts_week = [shift for shift in employeeShifts if shift.start >= start_week and shift.start < end_week]
                    if len(shifts_week) > 0:
                        averageHoursSlackVarPos = solver.add_var(lb=0, ub=avgContractHours, var_type='C', name='averageHoursSlackVarPos_{}_{}'.format(employee.id, start_week))
                        slack_coeff_pos = 1
                        averageHoursSlackVarNeg = solver.add_var(lb=0, ub=employee.payperiod_minutes_max, var_type='C', name='averageHoursSlackVarNeg_{}_{}'.format(employee.id, start_week))
                        slack_coeff_neg = -1
                        vars = []
                        coeffs = []
                        for shift in shifts_week:
                            var = solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift))
                            if var:
                                vars.append(var)
                                coeffs.append(int(shift.pay_duration))
                        averageHoursSlackVarPos.obj = int(self.rule.penalty/60 * domain.settings .rule_objective)
                        averageHoursSlackVarNeg.obj = int(self.rule.penalty/60 * domain.settings .rule_objective)
                        solver.add_constr(0.8*avgContractHours >= slack_coeff_pos * averageHoursSlackVarPos + slack_coeff_neg * averageHoursSlackVarNeg + xsum(vars[i] * coeffs[i] for i in range(0, len(vars))) <= 1.2*avgContractHours, anme='averageHoursConstraint_{}_{}'.format(employee.id, start_week))


    def add_violation_to_output(self, solver, domain, output):
        nr_days = int(self.rule.parameter1)
        for employee in domain.employees:
            for index in range(0, len(domain.days), nr_days):
                start_week = domain.days[index].date
                averageHoursSlackVarPos = solver.var_by_name('averageHoursSlackVarPos_{}_{}'.format(employee.id, start_week))
                averageHoursSlackVarNeg = solver.var_by_name('averageHoursSlackVarNeg_{}_{}'.format(employee.id, start_week))
                if averageHoursSlackVarPos and averageHoursSlackVarPos.x > 0:
                   output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                            user_id=employee.id,
                                            violation_costs=averageHoursSlackVarPos.x * averageHoursSlackVarPos.obj,
                                            date=start_week))
                if averageHoursSlackVarNeg and averageHoursSlackVarNeg.c > 0:
                    output.append(Violation(rule_id=self.rule.id, rule_tag=self.rule.tag,
                                            user_id=employee.id,
                                            violation_costs=averageHoursSlackVarNeg.x * averageHoursSlackVarNeg.obj,
                                            date=start_week))