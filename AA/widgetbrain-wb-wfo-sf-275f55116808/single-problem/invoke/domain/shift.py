from datetime import datetime
import pytz
from config import configuration, constants
from lib.dt import parse_timestamp

DEFAULTS = configuration.domain.shift.defaults


class ShiftCollection:
    """
    A collection of shifts. Behaves as a list, which means that iterating over it returns
    the shifts.
    """

    def __init__(
            self,
            shifts=None
    ):

        if shifts is None:
            shifts = []
        self._collection = shifts

    #

    def __getitem__(self, key):
        return self._collection[key]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)

    def append(self, shift):
        self._collection.append(shift)

    def extend(self, shifts):
        for shift in shifts:
            self.append(shift)

    def copy(self):
        return ShiftCollection([shift for shift in self._collection])

    def get_shifts_by_filter(self, filter = lambda x: True):
        return ShiftCollection(
            [shift for shift in self._collection if filter(shift)]
        )

    def get_non_fixed_shifts(self):
        return ShiftCollection(
            [shift for shift in self._collection if not shift.is_fixed]
        )

    def get_shifts_starts_in_interval(self, start, end):
        return ShiftCollection(
            [shift for shift in self._collection if shift.starts_in_interval(start, end)]
        )

    def get_shifts_ends_in_interval(self, start, end):
        return ShiftCollection(
            [shift for shift in self._collection if shift.ends_in_interval(start, end)]
        )

    def get_shifts_within_interval(self, start, end):
        return ShiftCollection(
            [shift for shift in self._collection if shift.start < end and shift.end > start]
        )

    def get_shifts_eq_in_interval(self, start, end):
        return ShiftCollection(
            [shift for shift in self._collection if shift.start <= end and shift.end >= start]
        )

    def get_shifts_of_type(self, shift_type):
        return ShiftCollection(
            [shift for shift in self._collection if not shift_type or shift_type in shift.shift_types]
        )

    def get_unfixed_shifts(self):
        return ShiftCollection(
            [shift for shift in self._collection if not shift.is_fixed]
        )

    def get_rule_applicable_shifts(self, rule):
        return ShiftCollection([shift for shift in self._collection if rule.is_applicable_shift(shift) and rule.is_applicable_day(shift.start)])

    def exclude_shift(self, shift_to_exclude):
        return ShiftCollection([shift for shift in self._collection if shift is not shift_to_exclude])

    def get_shifts_skill_group(self, skill_group, max_size):
        shift_group_shifts = ShiftCollection([shift for shift in self._collection if shift.checkSkillGroup(skill_group)])
        return shift_group_shifts if len(shift_group_shifts) <= max_size else shift_group_shifts[:500]

    def initialize_shifts(self, shifts_specs, shift_type_definitions, settings):
        """
        Initializes the shift objects that are to be stored in the ShiftCollection.
        """
        import sys
        try:
            for shift_spec in shifts_specs:
                shift = Shift(shift_spec, shift_type_definitions, settings)
                if shift.pay_duration >= 0:
                    if (shift.is_fixed and shift.employee_id) or not shift.is_fixed:
                        self._collection.append(Shift(shift_spec, shift_type_definitions, settings))
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of shift with ID = ' + shift_spec.get("id", "'missing id'")).with_traceback(
                sys.exc_info()[2])

        self._collection.sort(key=lambda x: x.start)

        return self


class Shift:
    def __init__(self, shift_spec, shift_type_definitions, settings):
        self.id = shift_spec["id"]
        self.start = shift_spec["start"]
        self.end = shift_spec["end"]
        self.start_datetime = parse_timestamp(self.start, settings.time_zone)
        self.end_datetime = parse_timestamp(self.end, settings.time_zone)
        self.start_datetime_str = self.start_datetime.strftime(constants.time.date_format)
        self.end_datetime_str = self.end_datetime.strftime(constants.time.date_format)
        ##rewrite this to standard function, not inside object
        utc_start = datetime.utcfromtimestamp(self.start).replace(tzinfo=pytz.utc)
        local_start = utc_start.astimezone(settings.time_zone).replace(hour=0, minute=0, second=0)
        self.midnight_time_stamp = local_start.timestamp()

        self.pay_duration = shift_spec.get("pay_duration", self.calculate_pay_duration())
        self.pay_multiplication_factor = shift_spec.get("pay_multiplication_factor", DEFAULTS.pay_multiplication_factor)

        self.is_fixed = shift_spec.get("is_fixed", DEFAULTS.is_fixed)
        self.employee_id = shift_spec.get("user_id")
        self.department_id = shift_spec.get("department_id")
        self.break_duration = shift_spec.get("break_duration", DEFAULTS.break_duration)
        self.shift_cost = shift_spec.get("shift_cost")
        self.postal_code = shift_spec.get("postal_code")
        if self.postal_code:
            self.postal_code = self.postal_code.replace(' ', "")
        self.group_id = shift_spec.get("group_id")
        self.comment = shift_spec.get("comment")

        self.shift_skills = [
            ShiftSkill(skill_spec)
            for skill_spec in shift_spec.get("skills", [])
        ]
        self.shift_licenses = [
            ShiftLicense(license_spec)
            for license_spec in shift_spec.get("licenses", [])
        ]
        self.subshifts = [
            SubShift(subshift_spec)
            for subshift_spec in shift_spec.get("subshifts", [])
        ]
        self.breaks = [
            Break(break_spec)
            for break_spec in shift_spec.get("breaks", [])
        ]
        self.breaks.sort(key=lambda b: b.start)

        self.shift_types = shift_type_definitions.get_applicable_shift_types(self, settings.time_zone)
        self.shift_types.extend(shift_spec.get("shift_types", []))
        self.overlappingShifts = []
        if not self.department_id or len(self.department_id) == 0:
            self.setdepartment_id()

    def generate_standard_output(self, employee=None):
        return {
            'shift_id': self.id,
            'user_id': employee.id if employee else self.employee_id,
            'start': self.start,
            'finish': self.end,
            'start_datetime_str': self.start_datetime_str,
            'end_datetime_str': self.end_datetime_str,
            'pay_duration': self.pay_duration,
            'department_id': self.department_id,
            'is_fixed': self.is_fixed,
            'shift_types': self.shift_types.get_shift_type_ids(),
            'comment': self.comment
        }

    def calculate_pay_duration(self):
        return (self.end - self.start) / 60

    def in_schedule(self, schedule_start, schedule_end):
        return self.start >= schedule_start and self.start <= schedule_end

    def setdepartment_id(self):
        if not self.department_id:
            self.department_id = ''
        for subshift in self.subshifts:
            if not subshift.department_id:
                subshift.department_id = str(subshift.department_id)
            if len(self.department_id) > 0 and self.department_id.find(subshift.department_id) == -1:
                self.department_id += ','
            if self.department_id.find(subshift.department_id) == -1:
                self.department_id += subshift.department_id

    def startsOnDay(self, day):
        return (self.start >= day.date and self.start < day.date + 24 * 3600)

    def endsOnDay(self, day):
        return self.end >= day.date and self.end < day.date + 24 * 3600

    def checkSkillGroup(self, skillGroup):
        # check whether the employee skills match the skill group
        skillGroupOk = True
        if skillGroup:
            for ss in self.shift_skills:
                if ss.id not in skillGroup:
                    skillGroupOk = False
        return skillGroupOk


    def starts_in_interval(self, start, end):
        """
        Returns whether the shift starts during the interval
        """
        if isinstance(start, datetime):
            return self.start_datetime >= start and self.start_datetime < end
        return self.start >= start and self.start < end

    def ends_in_interval(self, start, end):
        """
        Returns whether the shift ends during the interval
        """
        if isinstance(start, datetime):
            return self.end_datetime >= start and self.end_datetime < end
        return self.end >= start and self.end < end

    def get_overlap_hours(self, start, end):
        overlap_start = start
        overlap_end = end
        if start < self.start:
            overlap_start = self.start
        if end > self.end:
            overlap_end = self.end
        return int((overlap_end - overlap_start) / constants.time.seconds_per_hour)

class ShiftSkill:
    def __init__(self, skill_spec):
        self.id = skill_spec.get("id")
        self.min_level = skill_spec.get('min_level', DEFAULTS.shift_skill.min_level)
        self.difficulty = skill_spec.get("difficulty", DEFAULTS.shift_skill.difficulty)


class ShiftLicense:
    def __init__(self, license_spec):
        self.id = license_spec.get("id")


class SubShift:
    def __init__(self, subshift_spec):
        self.id = subshift_spec.get("id")
        self.start = subshift_spec.get("start")
        self.end = subshift_spec.get("end")
        self.department_id = subshift_spec.get("department_id")


class Break:
    def __init__(self, break_spec):
        self.start = break_spec.get("start")
        self.end = break_spec.get("end")
        self.break_duration = break_spec.get("break_duration")
        self.is_paid = break_spec.get("is_paid")
