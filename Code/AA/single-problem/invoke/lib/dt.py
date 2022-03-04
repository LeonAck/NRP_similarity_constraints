from datetime import datetime, timedelta, timezone
import pytz


def date_to_datetime(date, tz=pytz.utc):
    """
    Converts a date object to a datetime object.
    """
    datetime_obj = datetime.combine(date, datetime.min.time())
    if tz:
        datetime_obj = tz.localize(datetime_obj)
    return datetime_obj


def parse_timestamp(timestamp, tz=pytz.utc):
    """
    Parses the timestamp to a datetime object and assigns it the time_zone.
    """
    if not isinstance(timestamp, datetime):
        try:
            timestamp = datetime.fromtimestamp(timestamp, tz=tz)
        except (OSError, ValueError):
            timestamp = datetime.fromtimestamp(timestamp/1000, tz=tz)
    if not timestamp.tzinfo:
        timestamp = timestamp.replace(tzinfo=tz)
    return timestamp


def start_of_day(dt):
    """
    Returns the start of the day for the provided datetime.
    If datetime is second before midnight it will return the next day, otherwise it will return start of the same day.
    """

    dt_plus_second = dt + timedelta(seconds=1)

    return datetime(dt_plus_second.year, dt_plus_second.month, dt_plus_second.day, tzinfo=dt_plus_second.tzinfo)


def end_of_day(dt):
    """
    Returns the end of the day for the provided datetime.
    If datetime is at midnight it will return same datetime, if not it will return start of the day after.
    """
    dt_minus_second = dt - timedelta(seconds=1)

    return addition_timezone_aware(datetime(dt_minus_second.year, dt_minus_second.month, dt_minus_second.day,
                                            tzinfo=dt_minus_second.tzinfo), timedelta(days=1), dt_minus_second.tzinfo)


def start_of_minute(dt):
    """
    Returns the start of the minute for the provided datetime.
    """
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, tzinfo=dt.tzinfo)


def addition_timezone_aware(dt, time_delta, tz):
    """
    Returns timezone aware datetime with additional timedelta.
    It's DST aware but timedelta bigger than hour (like day, week, etc.) should not affect hour/minute values.
    """
    time_delta_days = timedelta(days=time_delta.days)
    time_delta_rest = time_delta - time_delta_days

    dt_res = tz.localize(dt.replace(tzinfo=None) + time_delta_days)

    return (dt_res.astimezone(timezone.utc) + time_delta_rest).astimezone(tz)


def difference_timezone_aware(date_time1, date_time2):
    """
    Returns difference between two timezone aware datetimes.
    It's DST aware unless hour/minute values are the same and have same timezone.
    """
    zone1 = date_time1.tzinfo.zone
    zone2 = date_time2.tzinfo.zone

    if zone1 == zone2 and date_time1.hour == date_time2.hour and date_time1.minute == date_time2.minute:
        return date_time2.replace(tzinfo=None) - date_time1.replace(tzinfo=None)

    return date_time2 - date_time1
