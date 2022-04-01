import numpy as np


class DayCollection:
    """
    Class to collect all the days
    """
    def __init__(self, num_days_in_horizon):
        self.day_collection = None
        self.num_days_in_horizon = num_days_in_horizon
        self.if_week_day = self.set_week_days()
        self.list_week_days = self.get_weekend_days()

    def collect_days(self):
        """
        Function to collect all of the days
        """
        return None

    def set_week_days(self):
        """
        Function to create array to tell whether day is a weekday
        :return:
        array with True and False
        """
        # d_type_array = np.zeros(scenario.num_days_in_horizon)
        return np.array([Day(d_index).set_day_type(d_index) for d_index in range(0, self.num_days_in_horizon)])

    def get_weekend_days(self):
        """
        Get list of weekends days
        """
        return np.array([d_index for d_index in range(0, self.num_days_in_horizon) if Day(d_index).set_day_type(d_index)])

class Day:
    """
    Class to define a day
    """
    def __init__(self, index):
        self.index = index

        # set if day is weekday or weekend day
        self.day_type = self.set_day_type(self.index)

    def set_day_type(self, d_index):
        """
        Decide whether a day is a week day or a weekend day
        """
        # may change to true/false or 0/1
        if d_index % 6 == 5 or d_index % 7 == 6:
            return False
        else:
            return True

