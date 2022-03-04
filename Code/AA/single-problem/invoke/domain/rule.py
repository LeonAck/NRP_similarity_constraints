from datetime import datetime
import pytz
from domain.day import Day, DayCollection
from config import configuration, rule_mapping_by_tag, rule_mapping_by_id

DEFAULTS = configuration.domain.rule.defaults


class RuleCollection:
    """
    A collection of rules. Behaves as a list, which means that iterating over it returns
    the rules.
    """

    def __init__(
            self,
            rules_specs,
            settings,
            days
    ):
        self._collection = {}
        self._initialize_rules(rules_specs, settings, days)

    #

    def __getitem__(self, key):
        return self._collection[key]

    def __iter__(self):
        for key in self._collection:
            yield key

    def __len__(self):
        return len(self._collection)

    def __repr__(self):
        return f'RuleCollection({[rule_id for rule_id in self._collection]})'

    def items(self):
        for item in self._collection.items():
            yield item

    def works_on_variable_required(self):
        # we only check the first rule if there are two
        works_on_rule_ids = ["3", "4", "12", "24", "37", "40", "57"]
        if any([works_on_rule_id in self._collection for works_on_rule_id in works_on_rule_ids]) or (
                "30" in self._collection and self._collection["30"][0] and self._collection["30"][
            0].parameter2 == 0) or (
                "7" in self._collection and self._collection["7"][0] and self._collection["7"][0].parameter2 != 1):
            return True
        return False

    def _initialize_rules(self, rules_specs, settings, days):
        """
        Initializes the rule objects that are to be stored in the RuleCollection.
        """
        import sys
        try:
            for rule_spec in rules_specs:
                rule_object = Rule(rule_spec, settings, days)
                if rule_object.id not in self._collection:
                    self._collection[rule_object.id] = []
                rule_object.rule_counter = len(self._collection[rule_object.id])
                self._collection[rule_object.id].append(rule_object)  ##seperate because of possible tag in input
        except Exception as e:
            raise type(e)(str(e) +
                          ' seems to trip up the import of rule with ID = ' + rule_spec.get("rule_id", "'missing id'")).with_traceback(
                sys.exc_info()[2])

        self._add_overlap_rule(settings)

    def _add_overlap_rule(self, settings):
        if "0" not in self._collection: # and not ("15" in self._collection and self._collection["15"][0].parameter1 == 1):
            self._collection["0"] = [Rule(configuration.domain.rule.rule0, settings)]

    def set_shifting_window_rules(self):
        for rule_id, rules in self._collection.items():
            for rule in rules:
                if rule.improvement_heuristic_only:
                    rule.is_active = False

    def set_rules_to_active(self):
        for rule_id, rules in self._collection.items():
            for rule in rules:
                rule.is_active = True

class Rule:
    def __init__(self, rule_spec, settings, days=None):
        if not rule_spec.get("rule_id") and not rule_spec.get("rule_tag"):
            raise ValueError("rule without rule id or rule tag in input")
        self.id = rule_spec.get("rule_id", rule_mapping_by_tag[rule_spec.get("rule_tag")])
        self.tag = rule_spec.get("rule_tag", rule_mapping_by_id[rule_spec.get("rule_id")])
        self.rule_counter = DEFAULTS.rule_counter
        self.department_ids = rule_spec.get("department_ids")
        self.penalty = rule_spec.get("penalty", DEFAULTS.penalty)
        self.parameter1 = rule_spec.get("parameter_1", DEFAULTS.parameter_1)
        self.parameter2 = rule_spec.get("parameter_2", DEFAULTS.parameter_2)
        self.parameter3 = rule_spec.get("parameter_3", DEFAULTS.parameter_3)
        self.parameter4 = rule_spec.get("parameter_4", DEFAULTS.parameter_4)
        self.parameter5 = rule_spec.get("parameter_5", DEFAULTS.parameter_5)
        self.parameter6 = rule_spec.get("parameter_6", DEFAULTS.parameter_6)
        self.parameter7 = rule_spec.get("parameter_7", DEFAULTS.parameter_7)
        self.is_mandatory = rule_spec.get("is_mandatory", DEFAULTS.is_mandatory)
        self.employee_ids = rule_spec.get("user_ids", DEFAULTS.user_ids)
        self.department_id = rule_spec.get("department_id", DEFAULTS.department_id)
        self.department_id_2 = rule_spec.get("department_id_2", DEFAULTS.department_id_2)
        self.shift_types = rule_spec.get("shift_types", DEFAULTS.shift_types)
        self.skill_id = rule_spec.get("skill_id", DEFAULTS.skill_id)
        self.skill_id_2 = rule_spec.get("skill_id_2", DEFAULTS.skill_id_2)
        self.license_id = rule_spec.get("license_id", DEFAULTS.license_id)
        self.license_id_2 = rule_spec.get("license_id_2", DEFAULTS.license_id_2)
        self.weekdays = rule_spec.get("weekdays", DEFAULTS.weekdays)
        self.shift_group_ids = rule_spec.get("shift_group_ids", DEFAULTS.shift_group_ids)
        self.rule_start = rule_spec.get("rule_start", DEFAULTS.rule_start)
        self.rule_end = rule_spec.get("rule_end", DEFAULTS.rule_end)
        self.period_start = rule_spec.get("period_start", DEFAULTS.period_start)
        self.period_end = rule_spec.get("period_end", DEFAULTS.period_end)
        self.rule_time_zone = settings.time_zone
        self.start_payperiod = self.get_midnight_ts(rule_spec.get("start_payperiod", DEFAULTS.start_payperiod), settings.time_zone)
        self.required_times = rule_spec.get("required_times", DEFAULTS.required_times)
        self.special_days = DayCollection([
            days.get_day_from_date(self.get_midnight_ts(date_special_day, settings.time_zone))
            for date_special_day in rule_spec.get("special_days", DEFAULTS.special_days)
            if days.get_day_from_date(self.get_midnight_ts(date_special_day, settings.time_zone))
        ])
        self.improvement_heuristic_only = rule_spec.get("improvement_heuristic_only",
                                                        DEFAULTS.improvement_heuristic_only)
        self.is_active = rule_spec.get("is_active", DEFAULTS.is_active)

    def __repr__(self):
        return f'rule(id={self.id})'

    def get_parameters(self):
        return {"parameter_1": self.parameter1, "parameter_2": self.parameter2,
                "parameter_3": self.parameter3, "parameter_4": self.parameter4,
                "parameter_5": self.parameter5, "parameter_6": self.parameter6}

    def is_applicable_employee(self, employee):
        if not self.employee_ids:
            return True
        return employee.id in self.employee_ids

    def is_applicable_shift(self, shift):
        if not self.department_ids and not self.shift_types:
            return True
        if self.department_ids:
            if shift.department_id not in self.department_ids:
                for sub_shift in shift.subshifts:
                    if sub_shift.department_id in self.department_ids:
                        break
                else:
                    return False
        shift_shift_type_ids = shift.shift_types.get_shift_type_ids()
        if self.shift_types:
            for shift_type in self.shift_types:
                if shift_type in shift_shift_type_ids:
                    break
            else:
                return False
        return True

    def is_applicable(self, shift, employee):
        applicable = True
        if shift and self.department_ids:
            if shift.department_id not in self.department_ids:
                for sub_shift in shift.subshifts:
                    if sub_shift.department_id in self.department_ids:
                        break
                else:
                    applicable = False
        if employee and self.employee_ids:
            if str(employee.id) not in self.employee_ids:
                applicable = False
        if shift and self.shift_types:
            for shift_type in self.shift_types:
                if shift_type in shift.shift_types:
                    break
            else:
                applicable = False
        return applicable

    def is_applicable_day(self, date):
        applicable = True
        if self.rule_start:
            if date >= self.rule_start:
                if self.rule_end:
                    if date <= self.rule_end:
                        applicable = True
                    else:
                        return False
            else:
                return False

        if self.weekdays:
            dt_date = datetime.utcfromtimestamp(date)
            weekday = dt_date.astimezone(self.rule_time_zone).weekday()
            if weekday not in self.weekdays or self.weekdays == []:
                applicable = False

        return applicable

    def get_midnight_ts(self, date, time_zone):
        if date is None:
            return date
        dt_date = datetime.utcfromtimestamp(int(date)).replace(tzinfo=pytz.utc)
        new_date = dt_date.astimezone(time_zone)

        new_date = new_date.replace(hour=0, minute=0, second=0)

        return int(new_date.timestamp())
