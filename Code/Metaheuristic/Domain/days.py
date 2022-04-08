import numpy as np


class DayCollection:
    """
    Class to collect all the days
    """
    def __init__(self, num_days_in_horizon):
        self.day_collection = None
        self.num_days_in_horizon = num_days_in_horizon
        self.if_week_day = self.set_week_days()
        self.list_weekend_days = self.get_weekend_days()
        self.weekend_day_indices = self.get_weekend_day_index(self.list_weekend_days)
        self.weekends = self.get_weekends()
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
        return np.array([d_index for d_index in range(0, self.num_days_in_horizon) if not Day(d_index).set_day_type(d_index)])

    def get_weekend_day_index(self, list_of_weekend_days):
        """
        For each weekend day get the index of the day in the weekend
        0 -> Saturday
        1 --> Sunday
        """
        weekend_day_indices = {}
        for d_index in list_of_weekend_days:
            weekend_day_indices[d_index] = 0 if d_index % 7 == 5 \
                                        else 1
        return weekend_day_indices

    def get_weekends(self):
        """
        Get list of weekends
        """
        i = 0
        weekends = dict()
        while i < len(self.list_weekend_days):
            weekends[int(i/2)] = (self.list_weekend_days[i:i+2])
            i += 2
        return weekends

    def get_index_other_weekend_day(self, index_in_weekend):
        """
        If d_index 0, we need to check +1
        If d_index 1, we need to check -1
        """
        if index_in_weekend==0:
            return 1
        if index_in_weekend==1:
            return -1




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
        if d_index % 7 == 5 or d_index % 7 == 6:
            return False
        else:
            return True

