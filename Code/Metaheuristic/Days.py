
class DayCollection:
    """
    Class to collect all the days
    """
    def __init__(self):
        self.day_collection = None

    def collect_days(self):
        """
        Function to collect all of the days
        """
        return None


class Day:
    """
    Class to define a day
    """
    def __init__(self, index):
        self.index = index

        # set if day is weekday or weekend day
        self.day_type = self.set_day_type()

    def set_day_type(self):
        """
        Decide whether a day is a week day or a weekend day
        """
        # may change to true/false or 0/1
        if self.index % 6 == 0 or self.index % 7 == 0:
            return "weekend"
        else:
            return "week"

