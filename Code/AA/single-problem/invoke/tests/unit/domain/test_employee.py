from datetime import datetime
from unittest.mock import MagicMock
import pytest
import pytz

from utils import create_shift
from domain.employee import Employee, EmployeeUnavailability, EmployeeAvailability


class TestEmployee:
    """domain.employee.Employee"""

    @pytest.fixture(scope="class")
    def employee(self):
        employee_spec = {
            "id": 1,
        }
        settings = MagicMock()
        settings.time_zone = pytz.utc
        shifts = MagicMock()

        return Employee(employee_spec, shifts, settings)

    @pytest.fixture(scope="class")
    def unavailabilities(self):
        unavailabilties = [
            EmployeeUnavailability({"start": datetime(2022, 2, 10, 6).timestamp(), "end": datetime(2022, 2, 10, 10).timestamp()}),
            EmployeeUnavailability({"start": datetime(2022, 2, 11, 8).timestamp(), "end": datetime(2022, 2, 11, 10).timestamp()}),
            EmployeeUnavailability({"start": datetime(2022, 2, 12, 22).timestamp(), "end": datetime(2022, 2, 13, 2).timestamp()}),
        ]
        return unavailabilties

    @pytest.fixture(scope="class")
    def availabilities(self):
        availabilties = [
            EmployeeAvailability({"start": datetime(2022, 2, 10, 8).timestamp(), "end": datetime(2022, 2, 10, 18).timestamp()}),
            EmployeeAvailability({"start": datetime(2022, 2, 11, 8).timestamp(), "end": datetime(2022, 2, 11, 18).timestamp()}),
            EmployeeAvailability({"start": datetime(2022, 2, 12, 8).timestamp(), "end": datetime(2022, 2, 13, 18).timestamp()}),
        ]
        return availabilties

    def test_unavailability_no_overlap(self, employee, unavailabilities):
        """should return employee is available, when shift is not overlapping with any unavailability"""
        # Arrange
        employee.unavailabilities = unavailabilities
        shift_1 = create_shift(1, datetime(2022, 2, 10, 6), datetime(2022, 2, 9, 9))

        # Act
        is_available = employee.check_shift_outside_unavailabilities(shift_1)

        # Assert
        assert is_available

    def test_unavailability_overlap(self, employee, unavailabilities):
        """should return employee is not available, when shift is overlapping with one or more unavailabilities"""
        # Arrange
        employee.unavailabilities = unavailabilities
        shift_1 = create_shift(1, datetime(2022, 2, 10, 8), datetime(2022, 2, 10, 14))

        # Act
        is_available = employee.check_shift_outside_unavailabilities(shift_1)

        # Assert
        assert not is_available

    def test_availability_full_overlap(self, employee, availabilities):
        """should return employee is available, when shift is fully overlapping with an availability"""
        # Arrange
        employee.availabilities = availabilities
        employee.use_availabilities = True
        shift_1 = create_shift(1, datetime(2022, 2, 10, 10), datetime(2022, 2, 10, 16))

        # Act
        is_available = employee.check_shift_inside_availablities(shift_1)

        # Assert
        assert is_available

    def test_availability_no_full_overlap(self, employee, availabilities):
        """should return employee is not available, when shift is not fully overlapping with an availability"""
        # Arrange
        employee.availabilities = availabilities
        employee.use_availabilities = True
        shift_1 = create_shift(1, datetime(2022, 2, 10, 7), datetime(2022, 2, 10, 12))

        # Act
        is_available = employee.check_shift_inside_availablities(shift_1)

        # Assert
        assert not is_available
