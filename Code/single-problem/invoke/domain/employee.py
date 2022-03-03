from datetime import datetime
import pytz
from config import configuration
from domain.shift import ShiftCollection

DEFAULTS = configuration.domain.employee.defaults

class EmployeeCollection:
    """
    A collection of Employees. Initializes the Employee objects
    based on the given specification, and makes them available as a list would.
    """

    def __init__(self, employees=None):
        if employees is None:
            employees = []
        self._collection = employees
    #

    def __getitem__(self, key):
        return self._collection[key]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        return f'EmployeeCollection({[employee.__repr__() for employee in self._collection]})'
    #
    def get_shift_eligible_employees(self, shift):
        return EmployeeCollection([employee for employee in self._collection if shift in employee.eligible_shifts_in_schedule])

    def get_rule_applicable_employees(self, rule):
        return EmployeeCollection([employee for employee in self._collection if rule.is_applicable_employee(employee)])

    def exclude_employee(self, employee_to_exclude):
        return EmployeeCollection([employee for employee in self._collection if employee is not employee_to_exclude])

    def check_shared_shifts(self, shifts):
        for shift in shifts:
            has_shared_shifts = any(
                [emp_i.is_eligible(shift) and emp_j.is_eligible(shift) for emp_i in self._collection for
                 emp_j in self._collection if emp_i != emp_j])
            if has_shared_shifts:
                return True
        return False

    def get_non_overlapping_skill_groups(self):
        skill_groups = []
        for employee in self._collection:
            if len(employee.skills) > 0:
                skill_ids = employee.get_sorted_skill_ids()
                new_group = True

                for sg in skill_groups:
                    # if there are both the same, then skip
                    found = False
                    for skill in skill_ids:
                        if skill in sg:
                            found = True
                            new_group = False
                    if found:
                        for skill in skill_ids:
                            if skill not in sg:
                                sg.append(skill)
                                sg.sort()
                if new_group:
                    skill_groups.append(skill_ids)
        new_list = []
        for sg in skill_groups:
            if sg not in new_list:
                new_list.append(sg)
        return new_list

    def get_employees_skill_group(self, skill_group):
        return EmployeeCollection([employee for employee in self._collection if employee.checkSkillGroup(skill_group)])

    def refresh_shift_properties(self, new_shifts, settings):
        for employee in self._collection:
            employee.set_shift_properties(new_shifts, settings)

    def initialize_employees(self, employees_spec, shifts, settings):
        """
        Initializes the Employee objects that are to be stored in teh EmployeeCollection.
        """
        import sys
        try:
            for employee_spec in employees_spec:
                self._collection.append(Employee(employee_spec, shifts, settings))
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of user with ID = ' + employee_spec.get("id", "'missing id'")).with_traceback(sys.exc_info()[2])
        # sort based on employee id
        self._collection.sort(key=lambda employee: employee.id)
        return self


class Employee:
    def __init__(self, employee_spec, shifts, settings):
        self.id = employee_spec["id"]
        self.start_contract = employee_spec.get("start_contract", DEFAULTS.start_contract)
        self.finish_contract = employee_spec.get("finish_contract", DEFAULTS.finish_contract)
        self.hourly_rate = employee_spec.get("hourly_rate", DEFAULTS.hourly_rate)
        self.is_fixed = employee_spec.get("is_fixed", DEFAULTS.is_fixed)
        self.postal_code = employee_spec.get("postal_code")
        self.use_availabilities = employee_spec.get("use_availabilities")
        self.start_first_of_month = employee_spec.get("start_first_of_month", DEFAULTS.start_first_of_month)
        self.pay_period_cycle = employee_spec.get("pay_period_cycle", DEFAULTS.pay_period_cycle)
        self.payperiod_minutes_min = employee_spec.get("payperiod_minutes_min", DEFAULTS.payperiod_minutes_min)
        self.payperiod_minutes_max = employee_spec.get("payperiod_minutes_max", DEFAULTS.payperiod_minutes_max)
        self.minimum_break_length = employee_spec.get("minimum_time_between_shifts", DEFAULTS.payperiod_minutes_max)
        self.payperiod_length = employee_spec.get("payperiod_length", employee_spec.get("payperiod_length_days", DEFAULTS.payperiod_length))
        self.previous_consecutive_shifts = employee_spec.get("previous_consecutive_shifts", DEFAULTS.previous_consecutive_shifts)
        self.previous_hours = employee_spec.get("previous_hours", DEFAULTS.previous_hours)
        self.max_weekends = employee_spec.get("max_weekends")
        self.payperiod_start = employee_spec.get('payperiod_start', self.get_payperiod_start(settings))
        self.shifts_of_type = employee_spec.get('shifts_of_type', DEFAULTS.shifts_of_type)

        self.skills = [
            EmployeeSkill(skill_spec)
            for skill_spec in employee_spec.get("skills", [])
        ]
        self.licenses = [
            EmployeeLicense(license_spec)
            for license_spec in employee_spec.get("licenses", [])
        ]
        self.agreements = [
            EmployeeAgreement(agreement_spec)
            for agreement_spec in employee_spec.get("agreements", [])
        ]
        self.availabilities = [
            EmployeeAvailability(availability_spec)
            for availability_spec in employee_spec.get("availabilities", []) # Otherwise isElgible check is incorrect
        ]
        self.unavailabilities = [
            EmployeeUnavailability(unavailability_spec)
            for unavailability_spec in employee_spec.get("unavailabilities", [])
        ]
        self.employee_preferences = [
            EmployeePreference(preference_spec)
            for preference_spec in employee_spec.get("preferences", [])
        ]
        self.employee_off_day_preferences = [
            EmployeePreference(off_day_preference_spec)
            for off_day_preference_spec in employee_spec.get("off_day_preferences", [])
        ]
        self.departments = [
            EmployeeDepartment(department_spec)
            for department_spec in employee_spec.get("department_ids", [])
        ]
        self.department_ids = [department.id for department in self.departments]

        self.employee_pay_penalties = [
            EmployeePayPenalty(pay_penalty_spec)
            for pay_penalty_spec in employee_spec.get("pay_penalties", [])
        ]

        self.shift_counts = [
            EmployeeShiftCount(shift_count_spec)
            for shift_count_spec in employee_spec.get("shift_counts", [])
        ]

        self.shiftTypePreferences = [
            EmployeeShiftTypePreference(shift_type_preference_spec)
            for shift_type_preference_spec in employee_spec.get("shift_type_preferences", [])
        ]

        self.set_shift_properties(shifts, settings)

    def __repr__(self):
        return f'Employee(id={self.id})'

    def set_shift_properties(self, shifts, settings, shift_type = None):
        self.fixed_shifts = ShiftCollection(
            [shift for shift in shifts if shift.employee_id == self.id and shift.is_fixed])
        self.fixed_shifts_in_schedule = self.fixed_shifts.get_shifts_starts_in_interval(settings.start, settings.end)
        self.eligible_shifts = ShiftCollection([shift for shift in shifts if self.is_eligible(shift)])
        self.eligible_shifts_in_schedule = self.eligible_shifts.get_shifts_starts_in_interval(settings.start, settings.end)
        self.unfixed_eligible_shifts_in_schedule = self.eligible_shifts_in_schedule.get_unfixed_shifts()


    def get_payperiod_start(self, settings):
        payperiod_start = datetime.utcfromtimestamp(float(settings.start)).replace(tzinfo=pytz.utc)
        date = payperiod_start.astimezone(settings.time_zone)
        date = date.replace(hour=0, minute=0, second=0)
        return int(date.timestamp())

    def get_payduration_unavailabilities(self, payperiod_start, payperiod_end):
        payduration_unavailabilities = 0
        for unavailability in self.unavailabilities:
            # there are two scenarios here. If we don't know anything about the days themselves we have to just take the pay_duration of the entire leave object
            if len(unavailability.unavailabilityWorkdays) == 0:
                if payperiod_start < unavailability.end and payperiod_end > unavailability.start:
                    payduration_unavailabilities += unavailability.pay_duration
            else:
                for workday in unavailability.unavailabilityWorkdays:
                    if payperiod_start < workday.end and payperiod_end > workday.start:
                        payduration_unavailabilities += workday.pay_duration
        return payduration_unavailabilities

    def get_penalty(self, shift):
        penalty = 1
        for employeePayPenalty in self.employee_pay_penalties:
            applyPenalty = True
            if employeePayPenalty.shift_types:
                for st in employeePayPenalty.shift_types:
                    if st not in shift.shift_types:
                        applyPenalty = False

            if employeePayPenalty.from_date and employeePayPenalty.from_date > shift.start:
                applyPenalty = False

            if employeePayPenalty.to_date and employeePayPenalty.to_date < shift.end:
                applyPenalty = False

            if employeePayPenalty.weekdays:
                midnightDate = datetime.utcfromtimestamp(shift.start)
                if midnightDate.weekday() not in employeePayPenalty.weekdays:
                    applyPenalty = False

            if applyPenalty:
                penalty *= employeePayPenalty.penalty

        return penalty

    def is_eligible(self, shift):
        eligible = True
        employeeDepartments = [dep.id for dep in self.departments]
        # check if the employee has all the department ids for each sub shifts of a shift
        if not shift.is_fixed:
            if self.start_contract > 0:
                if self.start_contract > shift.start:
                    eligible = False
            if self.finish_contract > 0:
                if self.finish_contract < shift.end:
                    eligible = False

            if eligible and shift.department_id and shift.department_id not in employeeDepartments:
                eligible = False

            if eligible and shift.subshifts and shift.subshifts[0].department_id:
                for subShift in shift.subshifts:
                    if subShift.department_id not in employeeDepartments:
                        eligible = False
                        break
                    if subShift.department_id in employeeDepartments:
                        # check the date
                        for dep in self.departments:
                            if dep.id == subShift.department_id:
                                if dep.start > shift.start:
                                    eligible = False
                                    break
                                if dep.end < shift.end:
                                    eligible = False
                                    break


            # if the employee is fixed we are not allowed to assign any shifts
            if self.is_fixed:
                eligible = False

            # check for availabilities and if there is full overlap
            if eligible:
                eligible = self.check_shift_inside_availablities(shift)
            # check for unavailabilities and if there is any overlap
            if eligible:
                eligible = self.check_shift_outside_unavailabilities(shift)

            # check for fixed shifts if there is any overlap
            overlappingFixedShifts = [fixed_shift for fixed_shift in self.fixed_shifts if (fixed_shift.start < shift.end and fixed_shift.end > shift.start)]
            if len(overlappingFixedShifts) > 0:
                eligible = False

            # check the licenses
            if len(shift.shift_licenses) > 0 and eligible:
                # if the shift does not exist in the list or if the license has expired
                for shiftLicense in shift.shift_licenses:
                    licenseCheck = False
                    for empLicense in self.licenses:
                        if empLicense.id == shiftLicense.id:
                            # check the dates
                            if empLicense.start < shift.start and empLicense.end > shift.start:
                                licenseCheck = True

                    if not licenseCheck:
                        eligible = False

            if len(shift.shift_skills) > 0 and eligible:
                # if the shift does not exist in the list or if the license has expired
                for shiftSkill in shift.shift_skills:
                    skillCheck = False
                    for empSkill in self.skills:
                        if empSkill.id == shiftSkill.id:
                            # check the dates
                            if empSkill.start < shift.start and empSkill.end > shift.start:
                                skillCheck = True

                    if not skillCheck:
                        eligible = False

            # if the license is there, check whether the employee has the right one which is not expired
        # check for fixed shifts
        elif shift.is_fixed and shift.employee_id and not str(shift.employee_id) == str(self.id):
            eligible = False
        return eligible

    def checkSkillGroup(self, skillGroup):
        # check whether the employee skills match the skill group
        skillGroupOk = True
        if skillGroup:
            for es in self.skills:
                if es.id not in skillGroup:
                    skillGroupOk = False
        return skillGroupOk

    def get_sorted_skill_ids(self):
        return sorted([skill.id for skill in self.skills])

    def check_shift_inside_availablities(self, shift):
        if self.use_availabilities:
            if not any(availability.start <= shift.start and shift.end <= availability.end for availability in
                       self.availabilities):
                return False
        return True

    def check_shift_outside_unavailabilities(self, shift):
        if any(shift.end > unavailability.start and shift.start < unavailability.end for unavailability in
                self.unavailabilities):
            return False
        return True


class EmployeeDepartment:
    def __init__(self, department_spec):
        self.id = department_spec["id"]
        self.proficiency_rating = department_spec.get("proficiency_rating")
        self.start = department_spec.get("from", 0)
        self.end = department_spec.get("to", 253402300799)

class EmployeeSkill:
    def __init__(self, skill_spec):
        self.id = skill_spec["id"]
        self.level = skill_spec.get("level", 1)
        self.start = skill_spec.get("from", 0)
        self.end = skill_spec.get("expires", 253402300799)


class EmployeeAgreement(object):
    def __init__(self, agreement_spec):
        self.id = agreement_spec["id"]
        self.start = agreement_spec.get("start", 0)
        self.end = agreement_spec.get("end", 253402300799)
        self.payperiod_minutes_min = agreement_spec.get("payperiod_minutes_min", 0)
        self.payperiod_minutes_max = agreement_spec.get("payperiod_minutes_max", 0)
        self.payperiod_length_days = agreement_spec.get("payperiod_length_days", 7)
        self.payperiod_start = agreement_spec.get("payperiod_start", 0)
        self.payperiod_length = agreement_spec.get("payperiod_length", self.payperiod_length_days)
        self.scale_contract_minutes = agreement_spec.get("scale_contract_minutes", False)

class EmployeeLicense:
    def __init__(self, license_spec):
        self.id = license_spec["id"]
        self.start = license_spec.get("from", 0)
        self.end = license_spec.get("expires", 253402300799)


class EmployeeUnavailability:
    def __init__(self, unavailability_spec):
        self.start = unavailability_spec["start"]
        self.end = unavailability_spec["end"]
        self.pay_duration = unavailability_spec.get("pay_duration", 0)
        self.unavailabilityWorkdays = [
            EmployeeUnavailabilityWorkday(unavailability_workday_spec)
            for unavailability_workday_spec in unavailability_spec.get("unavailability_workdays", [])
        ]


class EmployeeAvailability(object):
    def __init__(self, availability_dictionary):
        self.start = int(availability_dictionary['start'])
        self.end = int(availability_dictionary['end'])


class EmployeeUnavailabilityWorkday:
    def __init__(self, unavailability_workday_spec):
        self.start = unavailability_workday_spec.get("start")
        self.end = unavailability_workday_spec.get("end")
        self.pay_duration = unavailability_workday_spec.get("pay_duration")

class EmployeeShiftTypePreference:
    def __init__(self, shift_type_preference_spec):
        self.shift_types = shift_type_preference_spec.get("shift_types", [])
        self.weight = shift_type_preference_spec.get("weight", 0)

class EmployeePayPenalty:
    def __init__(self, pay_penalty_spec):
        self.penalty = pay_penalty_spec.get("penalty", 0)
        self.from_date = pay_penalty_spec.get("from_date")
        self.to_date = pay_penalty_spec.get("to_date")
        self.shift_types = pay_penalty_spec.get("shift_type_ids")
        self.weekdays = pay_penalty_spec.get("weekdays")

class EmployeePreference:
    def __init__(self, preference_spec):
        self.penalty = preference_spec.get("penalty", 0)
        self.start = preference_spec.get("start")
        self.end = preference_spec.get("end")
        self.type = preference_spec.get("type")

class EmployeeShiftCount:
    def __init__(self, shift_count_spec):
        self.id = shift_count_spec.get("id")
        self.quantity = shift_count_spec.get("quantity")
