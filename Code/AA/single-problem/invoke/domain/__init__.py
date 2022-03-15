from datetime import datetime
from initialSolutionVar import initialSolutionVar
import pytz
from lib import parse
from domain.settings import Settings
from domain.shift import ShiftCollection
from domain.employee import EmployeeCollection
from domain.rule import RuleCollection
from domain.day import DayCollection
from domain.shift_type import ShiftTypeCollection
from alfa_sdk.common.session import Session

class Domain:

    def __init__(self, shift_fill_specifications):
        parse.rename_all_keys(shift_fill_specifications, "finish", "end")
        settings_spec = parse.parse_settings(shift_fill_specifications.get("settings"))
        shift_types_spec = parse.parse_shift_types(shift_fill_specifications.get("shift_type_definitions"))
        shifts_spec = parse.parse_shifts(shift_fill_specifications.get("shifts"))
        employees_spec = parse.parse_employees(shift_fill_specifications["users"])
        rules_spec = parse.parse_rules(shift_fill_specifications.get("rules", []))

        self.settings = Settings(settings_spec)
        self.shift_type_definitions = ShiftTypeCollection().initialize_shift_types(shift_types_spec)
        self.shifts = ShiftCollection().initialize_shifts(shifts_spec, self.shift_type_definitions, self.settings)
        self.employees = EmployeeCollection().initialize_employees(employees_spec, self.shifts, self.settings)
        self.days = DayCollection().initialize_days(self.shifts, self.settings)
        self.rules = RuleCollection(rules_spec, self.settings, self.days)
        self.globalOrganisationId = shift_fill_specifications.get("globalOrganisationId", "")
        self.kpi_properties = self.create_kpi_properties(shift_fill_specifications)

        self.initial_solution = self.input_initial_solution(shift_fill_specifications)

        self.travel_expenses_matrix = {}
        if self.settings.use_travel_expenses:
            self.travel_expenses_matrix = self.create_travel_expenses_matrix()

    def input_initial_solution(self, shift_fill_specifications):
        # initial solution definition
        initial_solution = []
        try:
            if 'initial_solution' in shift_fill_specifications:
                initial_solution_data = shift_fill_specifications['initial_solution']
                for initial_solution_var in initial_solution_data:
                    initialVarObject = initialSolutionVar(initial_solution_var)
                    initial_solution.append(initialVarObject)
        except Exception as e:
            import sys
            raise type(e)(str(e) +
                          ' seems to trip up the import of the initial solution').with_traceback(sys.exc_info()[2])

        return initial_solution


    def create_kpi_properties(self, shift_fill_specifications):
        kpi_properties = {}
        settings = shift_fill_specifications['settings']
        if 'users' in shift_fill_specifications:
            kpi_properties['number_of_employees'] = len(shift_fill_specifications['users'])
        if 'globalOrganisationId' in shift_fill_specifications:
            kpi_properties['entity'] = shift_fill_specifications.get("globalOrganisationId")
        elif 'globalOrganisationId' in settings:
            kpi_properties['entity'] = settings.get("globalOrganisationId")
        else:
            kpi_properties['entity'] = ""
        if 'start' in settings and 'finish' in settings:
            if 'time_zone' in settings:
                kpiPeriodStart = datetime.fromtimestamp(int(settings['start']))
                kpiPeriodFinish = datetime.fromtimestamp(int(settings['finish']))
                tz = pytz.time_zone(settings['time_zone'])

                kpi_properties["period"] = tz.localize(kpiPeriodStart).strftime(
                    '%Y-%m-%d') + ' - ' + tz.localize(kpiPeriodFinish).strftime('%Y-%m-%d')
            else:
                kpiPeriodStart = datetime.fromtimestamp(int(settings['start']))
                kpiPeriodFinish = datetime.fromtimestamp(int(settings['finish']))
                kpi_properties["period"] = kpiPeriodStart.strftime('%Y-%m-%d') + ' - ' + kpiPeriodFinish.strftime(
                    '%Y-%m-%d')
        else:
            kpi_properties["period"] = ''

        return kpi_properties

    def create_travel_expenses_matrix(self):
        employees = self.employees
        shifts = self.shifts
        travel_expense_matrix = {}
        url_dima = 'http://wb-dima-test.widgetbrain.io/dima/determineMatrix'

        unique_employee_postal_codes = set(
            [employee.postal_code for employee in employees if employee.postal_code and employee.postal_code != "None"])
        unique_shift_postal_codes = set(
            [shift.postal_code for shift in shifts if shift.postal_code and shift.postal_code != "None"])
        all_postal_codes = unique_employee_postal_codes | unique_shift_postal_codes
        payload_locations = ["netherlands " + postal_code for postal_code in all_postal_codes]
        payload = {
            "region": "europe/netherlands-latest",
            "locations": payload_locations,
            "customerId": "Trigion"
        }
        session = Session().http_session
        r = session.post(url_dima, json=payload)
        distance_matrix = r.json()

        if 'matrix' in distance_matrix:
            for row in distance_matrix['matrix']:
                for col in row:
                    distance = col['distance'] / 1000
                    travel_expenses = self.calculate_travel_expenses(distance)
                    from_postal_code = col['from'].split(' ')[1]
                    to_postal_code = col['to'].split(' ')[1]
                    if from_postal_code not in travel_expense_matrix:
                        travel_expense_matrix[from_postal_code] = []
                    travel_expense_matrix[from_postal_code].append(
                        {'postal_code': to_postal_code, 'travel_expenses': travel_expenses})

        return travel_expense_matrix

    def calculate_travel_expenses(self,distance):
        travel_expenses = 0
        if distance >= 9:
            travel_expenses = 0.18 * distance
        if distance >= 41:
            distance_above_41 = distance - 41
            travel_expenses += 0.16 * distance_above_41
        return round(2 * travel_expenses, 2)


