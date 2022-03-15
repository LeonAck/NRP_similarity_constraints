from datetime import datetime, timedelta

import pytz

from config import constants
from domain.shift import ShiftCollection

CONSTANTS = constants


class DayCollection:
    """
    A collection of Days. Initializes the day objects
    based on the given specification, and makes them available as a list would.
    """

    def __init__(self, days=None):
        if days is None:
            days = []
        self._collection = days
        self._index_map = {day.day_number_in_schedule: day for day in days}

    def __getitem__(self, key):
        return self._collection[key]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)

    #
    def get_day_from_date(self, date):
        if isinstance(date, datetime):
            for day in self._collection:
                if day.date_time <= date < day.date_time + timedelta(days=1):
                    return day
        else:
            for day in self._collection:
                if day.date <= date < day.date + constants.time.seconds_per_day:
                    return day
        return None

    def get_ts_day_index(self, day_number_in_schedule):
        if day_number_in_schedule in self._index_map:
            return self._index_map[day_number_in_schedule].date
        return self.settings_end

    def get_day_by_index(self, day_number_in_schedule):
        return self._index_map[day_number_in_schedule]

    def get_rule_applicable_days(self, rule):
        return DayCollection([day for day in self._collection if rule.is_applicable_day(day.date)])

    def get_days_in_period(self, period_start, period_end):
        return DayCollection([day for day in self._collection if day.in_interval(period_start, period_end)])

    def get_start_days_for_steps(self, step_size_days, period_start=None, period_end=None):
        if period_start and period_end:
            temp_collection = [day for day in self._collection if period_start <= day.date < period_end]
            return DayCollection([day for idx, day in enumerate(temp_collection) if idx % step_size_days == 0])
        if step_size_days == 1:
            return self
        return DayCollection([day for day in self._collection if day.day_number_in_schedule % step_size_days == 0])

    def get_days_in_payperiod(self, day_start_payperiod, payperiod_length_days):
        return DayCollection(
            [day for day in self._collection
             if day_start_payperiod.day_number_in_schedule
             <= day.day_number_in_schedule
             <= day_start_payperiod.day_number_in_schedule + payperiod_length_days])

    def get_first_day_weekends(self, weekend_days):
        return DayCollection(
            [day for day in self._collection
             if day.weekday == weekend_days[0] or (day.day_number_in_schedule == 0 and day.weekday == weekend_days[1])])

    def initialize_days(self, shifts, settings):
        """
        Initializes the days objects that are to be stored in the DayCollection.
        """
        self.settings_end = settings.end

        utc_dt = datetime.utcfromtimestamp(settings.start).replace(tzinfo=pytz.utc)
        date = utc_dt.astimezone(settings.time_zone)

        date = date.replace(hour=0, minute=0, second=0)
        index = 0
        while int(date.timestamp()) < settings.end:
            day = Day(date, shifts)
            self._collection.append(day)
            date = settings.time_zone.localize(date.replace(tzinfo=None) + timedelta(days=1))
            day.day_number_in_schedule = index
            self._index_map[index] = day
            index += 1

        return self


class Day:
    def __init__(self, date_time, shifts=None):
        if shifts is None:
            shifts = ShiftCollection()

        self.date_time = date_time
        self.date = int(date_time.timestamp())
        self.weekday = date_time.weekday()
        self.shifts_starts_on_day = shifts.get_shifts_starts_in_interval(self.date, self.date + CONSTANTS.time.seconds_per_day)
        self.day_number_in_schedule = None

    def in_interval(self, start, end):
        if isinstance(start, datetime):
            return start <= self.date_time < end
        return start <= self.date < end

    def __str__(self):
        return self.date_time.strftime(constants.time.date_format)
