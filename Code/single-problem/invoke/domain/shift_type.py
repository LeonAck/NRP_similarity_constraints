from datetime import datetime


class ShiftTypeCollection:
    """
    A collection of shifts. Behaves as a list, which means that iterating over it returns
    the shifts.
    """

    def __init__(
            self,
            shift_types=None
    ):
        if shift_types is None:
            shift_types = []
        self._collection = shift_types

    #

    def __getitem__(self, key):
        return self._collection[key]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)

    def __contains__(self, item):
        for shift_type in self._collection:
            if shift_type.id == str(item) or shift_type == item:
                return True
        return False

    def append(self, shift_type):
        if not isinstance(shift_type, ShiftType):
            shift_type = ShiftType({"id": shift_type})
        self._collection.append(shift_type)

    def extend(self, shift_types):
        for shift_type in shift_types:
            self.append(shift_type)

    def get_applicable_shift_types(self, shift, timezone):
        return ShiftTypeCollection(
            [shift_type for shift_type in self._collection if shift_type.is_shift_type(shift, timezone)]
        )

    def get_shift_type_ids(self):
        return [shift_type.id for shift_type in self._collection]

    def initialize_shift_types(self, shift_types_specs):
        """
        Initializes the shift type objects that are to be stored in the ShiftTypeCollection.
        """
        import sys
        try:
            for shift_type_spec in shift_types_specs:
                self._collection.append(ShiftType(shift_type_spec))
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of shift type with ID = ' + shift_type_spec.get(
                "id","'missing id'")).with_traceback(sys.exc_info()[2])

        return self


class ShiftType:
    def __init__(self, shift_type_spec):
        self.id = shift_type_spec["id"]
        self.name = shift_type_spec.get("name")
        self.start_after = shift_type_spec.get("start_after")
        self.start_before = shift_type_spec.get("start_before")
        self.end_after = shift_type_spec.get("end_after")
        self.end_before = shift_type_spec.get("end_before")
        self.minimum_duration = shift_type_spec.get("minimum_duration")
        self.weekdays = shift_type_spec.get("weekdays", [])

    def is_shift_type(self, shift, time_zone):
        # check whether the shift is on the right weekday and whether it starts before and after the definition
        is_shift_type = False

        # create the midnight date and timestamp from the shift start we can use for comparison sake
        start_time_local = datetime.fromtimestamp(shift.start, tz=time_zone)
        end_time_local = datetime.fromtimestamp(shift.end, tz=time_zone)
        minutesStartFromMidnight = (start_time_local - start_time_local.replace(hour=0, minute=0, second=0,
                                                                                microsecond=0)).total_seconds() / 60
        minutesEndFromMidnight = (end_time_local - start_time_local.replace(hour=0, minute=0, second=0,
                                                                            microsecond=0)).total_seconds() / 60

        ##Check minimum duration before such that a combination of minimum duration and start/end times are possible
        if self.minimum_duration is not None:
            shift_duration = shift.pay_duration
            is_shift_type = True
            if shift_duration < self.minimum_duration:
                is_shift_type = False
                return is_shift_type

        if self.start_after is not None and self.start_before is not None:
            if self.start_after <= minutesStartFromMidnight <= self.start_before:
                is_shift_type = True
                if len(self.weekdays) > 0:
                    # check whether the day of the week is correct
                    if start_time_local.weekday() not in self.weekdays:
                        is_shift_type = False
            else:
                is_shift_type = False

        if self.end_after is not None and self.end_before is not None:
            if self.end_before >= minutesEndFromMidnight >= self.end_after:
                is_shift_type = True
                if len(self.weekdays) > 0:
                    # check whether the day of the week is correct
                    if start_time_local.weekday() not in self.weekdays:
                        is_shift_type = False
            else:
                is_shift_type = False

        return is_shift_type
