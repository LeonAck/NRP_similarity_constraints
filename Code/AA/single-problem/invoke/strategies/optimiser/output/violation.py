
class ViolationCollection:
    """
    A collection of Violations. Initializes the violation objects
    based on the given specification, and makes them available as a list would.
    """

    def __init__(self, days=None):
        if days is None:
            days = []
        self._collection = days

    #
    def __getitem__(self, key):
        return self._collection[key]

    def __iter__(self):
        for item in self._collection:
            yield item

    def __len__(self):
        return len(self._collection)


    # def initialize_violations(self, shifts, settings):
    #     """
    #     Initializes the days objects that are to be stored in the DayCollection.
    #     """
    #     utc_dt = datetime.utcfromtimestamp(settings.start).replace(tzinfo=pytz.utc)
    #     date = utc_dt.astimezone(settings.time_zone)
    #
    #     date = date.replace(hour=0, minute=0, second=0)
    #     while int(date.timestamp()) < settings.end:
    #         day = Day(date, shifts)
    #         self._collection.append(day)
    #         date = settings.time_zone.localize(date.replace(tzinfo=None) + timedelta(days=1))
    #
    #     return self

class Violation:
    def __init__(self, rule_id, violation_costs, **kwargs):
        self.rule_id = rule_id
        self.violation_costs = violation_costs
        if kwargs.get("user_id"):
            self.user_id = kwargs.get("user_id")
        if kwargs.get("rule_tag"):
            self.rule_tag = kwargs.get("rule_tag")
        if kwargs.get("shift_id"):
            self.shift_id = kwargs.get("shift_id")
        if kwargs.get("date"):
            self.date = kwargs.get("date")
        if kwargs.get("date_time"):
            self.date_time = kwargs.get("date_time")
        if kwargs.get("shift_start"):
            self.shift_start = kwargs.get("shift_start")
        if kwargs.get("shift_finish"):
            self.shift_finish = kwargs.get("shift_finish")
        if kwargs.get("department_id"):
            self.department_id = kwargs.get("department_id")
        if kwargs.get("relevant_shifts") and isinstance(kwargs.get("relevant_shifts"), list):
            self.relevant_shifts = kwargs.get("relevant_shifts")
        if kwargs.get("violation_description"):
            self.violation_description = kwargs.get("violation_description")
        if kwargs.get("parameters"):
            self.parameters = kwargs.get("parameters")
        if kwargs.get("shift_group"):
            self.shift_group = kwargs.get("shift_group")
        if kwargs.get("agreement_id"):
            self.agreement_id = kwargs.get("agreement_id")

    def generate_output(self):
        return vars(self)

def generate_violation_output(solver, domain):
    pass