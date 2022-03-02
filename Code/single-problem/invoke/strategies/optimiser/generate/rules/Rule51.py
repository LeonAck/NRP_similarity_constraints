###TO BE REMOVED

class Rule51:
    # Only for violation checking
    def __init__(self, rule):
        self.rule = rule

    def set_rule(self, solver, domain):
        pass

    def add_violation_to_output(self, solver, domain, output):
        # At most parameter3 domain.shifts of type parameter1 with lenght > parameter1 per period of parameter4 x 24h and parameter5 weeks
        shiftType = self.rule.parameter2
        nrExceptions = self.rule.parameter3
        periodToCheck = self.rule.parameter4*24*60
        weeksNotDays = False
        if self.rule.parameter5:
            weeksNotDays = True
            periodToCheck = self.rule.parameter5*7*24*60
        parameters = {"parameter_1": self.rule.parameter1, "parameter_2": self.rule.parameter2,
                      "parameter_3": self.rule.parameter3, "parameter_4": self.rule.parameter4,
                      "parameter_5": self.rule.parameter5}

        for employee in domain.employees:
            if not self.rule.parameter1:
                maximumShiftDuration = employee.maximumShiftDuration
            else:
                maximumShiftDuration = self.rule.parameter1
            employeeShifts = [shift for shift in domain.shifts if solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)) and solver.find_variable(VAR_DEFAULTS.assignment.id(employee, shift)).x > 0]
            shifts_of_type = [shift for shift in employeeShifts if (shiftType and shiftType in shift.shift_types) or not shiftType]
            shifts_of_typeTooLong = [shift for shift in shifts_of_type if shift.pay_duration + shift.break_duration > maximumShiftDuration]
            if len(shifts_of_typeTooLong) == 0:
                continue
            if not weeksNotDays:
                # check number of long domain.shifts per parameter4 domain.days from the start of each shift
                for firstShift in shifts_of_typeTooLong:
                    shiftsInPeriod = [shift for shift in shifts_of_typeTooLong if firstShift.start <= shift.start < firstShift.start + periodToCheck*60]
                    if len(shiftsInPeriod) > nrExceptions:
                        var = solver.var_by_name('assignment_{}_{}_{}_{}_{}'.format(employee.id, str(firstShift.start), str(firstShift.end), firstShift.department_id, firstShift.id))
                        output.append(
                                        violationData('51', firstShift.id, var.x * self.rule.penalty * domain.settings .rule_objective, employee.id, firstShift.start, firstShift.start, firstShift.end,
                                                      firstShift.department_id, [shift.id for shift in shiftsInPeriod], generate_violation_text(nrExceptions, shiftType, maximumShiftDuration, periodToCheck, weeksNotDays, firstShift.start)))
            else:
                # check number of long domain.shifts for parameter5 weeks, ending on domain.settings .end
                periodStart = domain.settings .end - periodToCheck*60
                historicalCount = employee.longNightShifts
                shiftsInPeriod = [shift for shift in shifts_of_typeTooLong]
                if len(shiftsInPeriod) + historicalCount > nrExceptions:
                    firstShift = shiftsInPeriod[0]
                    var = solver.var_by_name('assignment_{}_{}_{}_{}_{}'.format(employee.id, str(firstShift.start), str(firstShift.end), firstShift.department_id, firstShift.id))
                    output.append(
                        violationData('51', firstShift.id, var.x * self.rule.penalty * domain.settings .rule_objective, employee.id, periodStart, None, None,
                                      firstShift.department_id, [shift.id for shift in shiftsInPeriod], generate_violation_text(nrExceptions, shiftType, maximumShiftDuration, periodToCheck, weeksNotDays, periodStart), parameters))


def generate_violation_text(nrExceptions, shiftType, maxLength, periodToCheck, weeksNotDays, periodStart):
    periodLength = ""
    if weeksNotDays:
        nr = periodToCheck / (7 * 24 * 60)
        periodLength += str(nr)
        periodLength += " weeks"
    else:
        nr = periodToCheck / (24 * 60)
        periodLength += str(nr)
        periodLength += "x24 hours"
    return "More than {} shift of type {} longer than {} hours in the period of {} starting on {}.".format(nrExceptions, shiftType, maxLength/60, periodLength, periodStart)