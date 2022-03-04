from datetime import date, datetime, timezone, timedelta
import pytz

from lib import dt


stockholm_timezone_str = 'Europe/Stockholm'


class TestDateToDatetime:
    """lib.dt.date_to_datetime"""

    def test_date_to_datetime_utc(self):
        """should return datetime in utc"""

        # Arrange
        date_to_convert = date(2022, 1, 14)

        # Act
        datetime_object = dt.date_to_datetime(date_to_convert)

        # Assert
        assert datetime_object == datetime(2022, 1, 14, tzinfo=timezone.utc)

    def test_date_to_datetime_stockholm(self):
        """should return datetime in Stockholm timezone"""

        # Arrange
        date_to_convert = date(2022, 1, 14)
        tz = pytz.timezone(stockholm_timezone_str)

        # Act
        datetime_object = dt.date_to_datetime(date_to_convert, tz)

        # Assert
        assert datetime_object == tz.localize(datetime(2022, 1, 14))


class TestAdditionTimezoneAware:
    """lib.dt.addition_timezone_aware"""

    def test_addition_timezone_aware_utc(self):
        """should return datetime in utc timezone with additional day"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 13))

        # Act
        datetime_utc_delta = dt.addition_timezone_aware(datetime_object, timedelta(days=1), tz)

        # Assert
        assert datetime_utc_delta == tz.localize(datetime(2022, 1, 21, 13))

    def test_addition_timezone_aware_stockholm(self):
        """should return datetime in Stockholm timezone with additional day"""

        # Arrange
        tz = pytz.timezone(stockholm_timezone_str)
        datetime_object = tz.localize(datetime(2022, 1, 20, 13))

        # Act
        datetime_utc_delta = dt.addition_timezone_aware(datetime_object, timedelta(days=1), tz)

        # Assert
        assert datetime_utc_delta == tz.localize(datetime(2022, 1, 21, 13))

    def test_addition_timezone_aware_helsinki(self):
        """should return datetime in Helsinki timezone with additional day"""

        # Arrange
        tz = pytz.timezone('Europe/Helsinki')
        datetime_object = tz.localize(datetime(2021, 9, 21, 1))

        # Act
        datetime_utc_delta = dt.addition_timezone_aware(datetime_object, timedelta(days=182), tz)

        # Assert
        assert datetime_utc_delta == tz.localize(datetime(2022, 3, 22, 1))

    def test_addition_timezone_aware_helsinki_dst(self):
        """should return datetime in Helsinki timezone with additional week during DST"""

        # Arrange
        tz = pytz.timezone('Europe/Helsinki')
        datetime_object = tz.localize(datetime(2022, 10, 24, 0))

        # Act
        datetime_utc_delta = dt.addition_timezone_aware(datetime_object, timedelta(weeks=1), tz)

        # Assert
        assert datetime_utc_delta == tz.localize(datetime(2022, 10, 31, 0))

    def test_addition_timezone_aware_stockholm_dst(self):
        """should return datetime in Stockholm timezone during dst with additional hours"""

        # Arrange
        tz = pytz.timezone(stockholm_timezone_str)
        datetime_object = tz.localize(datetime(2021, 3, 28, 1))

        # Act
        datetime_utc_delta = dt.addition_timezone_aware(datetime_object, timedelta(hours=3), tz)

        # Assert
        assert datetime_utc_delta == tz.localize(datetime(2021, 3, 28, 5))


class TestDifferenceTimezoneAware:
    """lib.dt.difference_timezone_aware"""

    def test_difference_timezone_aware_utc(self):
        """should return difference between two date/times in utc timezone"""

        # Arrange
        tz = pytz.utc
        datetime_object1 = tz.localize(datetime(2022, 1, 20, 13))
        datetime_object2 = tz.localize(datetime(2022, 1, 20, 15))

        # Act
        datetime_diff = dt.difference_timezone_aware(datetime_object1, datetime_object2)

        # Assert
        assert datetime_diff == timedelta(hours=2)

    def test_difference_timezone_aware_stockholm(self):
        """should return difference between two date/times in Stockholm timezone"""

        # Arrange
        tz = pytz.timezone(stockholm_timezone_str)
        datetime_object1 = tz.localize(datetime(2022, 1, 20, 13))
        datetime_object2 = tz.localize(datetime(2022, 1, 20, 15))

        # Act
        datetime_diff = dt.difference_timezone_aware(datetime_object1, datetime_object2)

        # Assert
        assert datetime_diff == timedelta(hours=2)

    def test_difference_timezone_aware_stockholm_dst(self):
        """should return difference between two date/times in Stockholm timezone during DST"""

        # Arrange
        tz = pytz.timezone(stockholm_timezone_str)
        datetime_object1 = tz.localize(datetime(2021, 3, 28, 1))
        datetime_object2 = tz.localize(datetime(2021, 3, 28, 5))

        # Act
        datetime_diff = dt.difference_timezone_aware(datetime_object1, datetime_object2)

        # Assert
        assert datetime_diff == timedelta(hours=3)

    def test_difference_timezone_aware_stockholm_dst_days(self):
        """should return difference (in days) between two dates with same time in Stockholm timezone during DST"""

        # Arrange
        tz = pytz.timezone(stockholm_timezone_str)
        datetime_object1 = tz.localize(datetime(2021, 3, 27, 5))
        datetime_object2 = tz.localize(datetime(2021, 3, 29, 5))

        # Act
        datetime_diff = dt.difference_timezone_aware(datetime_object1, datetime_object2)

        # Assert
        assert datetime_diff == timedelta(days=2)

    def test_difference_timezone_aware_different_timezones(self):
        """should return difference between two date/times with different timezones"""

        # Arrange
        tz = pytz.timezone(stockholm_timezone_str)
        datetime_object1 = tz.localize(datetime(2022, 1, 20, 16))
        datetime_object2 = pytz.utc.localize(datetime(2022, 1, 20, 20))

        # Act
        datetime_diff = dt.difference_timezone_aware(datetime_object1, datetime_object2)

        # Assert
        assert datetime_diff == timedelta(hours=5)


class TestStartOfMinute:
    """lib.dt.start_of_minute"""

    def test_start_of_minute(self):
        """should return minute start of given datetime"""

        # Arrange
        datetime_object = datetime(2022, 1, 20, 13, 54, 33)

        # Act
        datetime_res = dt.start_of_minute(datetime_object)

        # Assert
        assert datetime_res == datetime(2022, 1, 20, 13, 54)


class TestStartOfDay:
    """lib.dt.start_of_day"""

    def test_start_of_day(self):
        """should return start of day for given datetime"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 13, 54))

        # Act
        datetime_res = dt.start_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 20))

    def test_start_of_day_hour23(self):
        """should return start of day for given datetime with time 23:59:59"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 23, 59, 59))

        # Act
        datetime_res = dt.start_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 21))

    def test_start_of_day_midnight(self):
        """should return start of day for given datetime with time 00:00:00"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20))

        # Act
        datetime_res = dt.start_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 20))

    def test_start_of_day_hour5(self):
        """should return start of day for given datetime with time 05:00:00"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 5))

        # Act
        datetime_res = dt.start_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 20))


class TestEndOfDay:
    """lib.dt.end_of_day"""

    def test_end_of_day(self):
        """should return end of day for given datetime"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 13, 54))

        # Act
        datetime_res = dt.end_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 21))

    def test_end_of_day_midnight(self):
        """should return end of day for given datetime with time 00:00:00"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20))

        # Act
        datetime_res = dt.end_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 20))

    def test_end_of_day_hour0(self):
        """should return end of day for given datetime with time 00:00:01"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 0, 0, 1))

        # Act
        datetime_res = dt.end_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 21))

    def test_end_of_day_hour23(self):
        """should return end of day for given datetime with time 23:54"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 23, 54))

        # Act
        datetime_res = dt.end_of_day(datetime_object)

        # Assert
        assert datetime_res == tz.localize(datetime(2022, 1, 21))


class TestParseTimestamp:
    """lib.dt.parse_timestamp"""

    def test_parse_timestamp(self):
        """should return datetime from given timestamp"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 15, 54))
        timestamp_object = datetime.timestamp(datetime_object)

        # Act
        datetime_res = dt.parse_timestamp(timestamp_object)

        # Assert
        assert datetime_res == datetime_object

    def test_parse_timestamp_times1000(self):
        """should return datetime from given timestamp (times 1000)"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 15, 54))
        timestamp_object = datetime.timestamp(datetime_object) * 1000

        # Act
        datetime_res = dt.parse_timestamp(timestamp_object)

        # Assert
        assert datetime_res == datetime_object

    def test_parse_timestamp_datetime(self):
        """should return datetime from given datetime without timezone"""

        # Arrange
        datetime_object = datetime(2022, 1, 20, 15, 54)

        # Act
        datetime_res = dt.parse_timestamp(datetime_object)

        # Assert
        assert datetime_res == datetime_object.replace(tzinfo=pytz.utc)

    def test_parse_timestamp_datetime_utc(self):
        """should return datetime from given utc datetime"""

        # Arrange
        tz = pytz.utc
        datetime_object = tz.localize(datetime(2022, 1, 20, 15, 54))

        # Act
        datetime_res = dt.parse_timestamp(datetime_object)

        # Assert
        assert datetime_res == datetime_object
