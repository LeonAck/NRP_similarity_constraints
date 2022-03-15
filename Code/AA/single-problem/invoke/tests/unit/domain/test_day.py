from datetime import datetime

from utils import create_shift
from domain.day import Day
from domain.shift import ShiftCollection, Shift


class TestDay:
    """domain.day.Day"""

    def test_day_no_shifts(self):
        """should return no shifts which start on that day when passing empty collection for shifts"""

        # Arrange
        date_time = datetime(2022, 1, 13)
        shifts = ShiftCollection()

        # Act
        day = Day(date_time, shifts)

        # Assert
        assert day.date_time == date_time
        assert day.date == int(date_time.timestamp())
        assert day.day_number_in_schedule is None
        assert day.weekday == 3
        assert len(day.shifts_starts_on_day) == 0

    def test_day_none_shifts(self):
        """should return no shifts which start on that day without passing the shifts"""

        # Arrange
        date_time = datetime(2022, 1, 13)

        # Act
        day = Day(date_time)

        # Assert
        assert len(day.shifts_starts_on_day) == 0

    def test_day_with_shifts(self):
        """should return two shifts which start on that day"""

        # Arrange
        shift1 = create_shift(1, datetime(2022, 1, 13, 8), datetime(2022, 1, 13, 17))
        shift2 = create_shift(2, datetime(2022, 1, 13, 20), datetime(2022, 1, 14, 3))
        shift3 = create_shift(3, datetime(2022, 1, 15, 8), datetime(2022, 1, 15, 17))
        shift4 = create_shift(4, datetime(2022, 1, 12, 20), datetime(2022, 1, 13, 3))

        date_time = datetime(2022, 1, 13)

        # Act
        day = Day(date_time, ShiftCollection([shift1, shift2, shift3, shift4]))

        # Assert
        assert len(day.shifts_starts_on_day) == 2
        shift_ids = [shift.id for shift in day.shifts_starts_on_day]
        assert 1 in shift_ids
        assert 2 in shift_ids

    def test_day_str(self):
        """should return string representation of day"""

        # Arrange
        date_time = datetime(2022, 1, 13)

        # Act
        day = Day(date_time)

        # Assert
        assert str(day) == "2022.01.13_00_00_00"

    def test_day_in_period(self):
        """should test if day is inside given period"""

        # Arrange
        date_time = datetime(2022, 1, 13)

        # Act
        day = Day(date_time)

        # Assert
        assert day.in_interval(datetime(2022, 1, 13), datetime(2022, 1, 14)) is True
        assert day.in_interval(datetime(2022, 1, 12), datetime(2022, 1, 13)) is False
        assert day.in_interval(int(datetime(2022, 1, 13).timestamp()), int(datetime(2022, 1, 14).timestamp())) is True
        assert day.in_interval(int(datetime(2022, 1, 12).timestamp()), int(datetime(2022, 1, 13).timestamp())) is False
