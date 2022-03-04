from datetime import datetime
from unittest.mock import MagicMock
import pytest
from domain.settings import Settings
from domain.day import DayCollection
from domain.shift import ShiftCollection, Shift
from domain.employee import EmployeeCollection, Employee
from domain.shift_type import ShiftTypeCollection, ShiftType
from domain.rule import Rule
from strategies.optimiser.generate.rules import Rule25
from config import constants


class TestRule25:
    """strategies.optimizer.generate.rules.rule25"""

    def test_set_rule(self, solver, rule25_input, domain):
        """use default values: should create sufficient constraints"""
        # Arrange
        rule25 = Rule25(rule25_input)

        # Act
        rule25.set_rule(solver, domain)
        args = solver.create_slacked_constraint.call_args_list

        # Assert
        assert len(args) == 4

    def test_set_rule_with_input_periods(self, solver, rule25_input, domain):
        """with input pay period and shifting window size: should create correct number of constraints"""
        # Arrange
        rule25_input.parameter2 = 14  # payperiod length
        rule25_input.parameter6 = 7  # shifting window size
        rule25 = Rule25(rule25_input)

        # Act
        rule25.set_rule(solver, domain)
        args = solver.create_slacked_constraint.call_args_list

        # Assert
        assert len(args) == 4

    def test_set_rule_with_shift_types(self, solver, rule25_input, domain):
        """with min shift types: should create sufficient constraints"""
        # Arrange
        rule25_input.parameter2 = 14  # pay period length
        rule25_input.parameter3 = 1  # minimum shifts of type
        rule25_input.parameter4 = 1  # shift type id rule
        rule25 = Rule25(rule25_input)

        # Act
        rule25.set_rule(solver, domain)
        args = solver.create_slacked_constraint.call_args_list
        args_not_max_shift_type_cons = [arg for arg in args if not "min_shifts_of_type_max" in arg[1]['id']]

        # Assert
        assert len(args) == 6

    def test_add_violation_to_output(self, solver, rule25_input, domain):
        """should add sufficient violations to output"""
        # Arrange
        rule25 = Rule25(rule25_input)
        output = []

        # Act
        rule25.add_violation_to_output(solver, domain, output)

        # Assert
        assert len(output) == 4

    def test_applicable_combinations(self, rule25_input, domain):
        """should return all applicable employee, day, pay period lenght combinations"""
        # Arrange
        rule25 = Rule25(rule25_input)

        # Act
        combinations = list(rule25._get_rule_applicable_combinations(domain))

        # Assert
        assert [combination[0].id for combination in combinations] == ['1', '1', '2', '2']
        assert [str(combination[1]) for combination in combinations] == ['2022.01.01_00_00_00',
                                                                         '2022.01.08_00_00_00',
                                                                         '2022.01.01_00_00_00',
                                                                         '2022.01.08_00_00_00']
        assert all([combination[2] == 7 for combination in combinations])

    def test_add_constraint_to_solver_default(self, solver, rule25_input, domain):
        """default values: should create constraints with correct input arguments"""
        # Arrange
        rule25 = Rule25(rule25_input)
        pay_period_length = 7

        # Act
        rule25._add_constraint_to_solver(solver, domain, domain.employees[0], domain.days[0], pay_period_length)
        args = solver.create_slacked_constraint.call_args_list

        # Assert
        assert len(args) == 1
        assert args[0][1]['id'] == 'max_working_time1_2022.01.01_00_00_00_0'
        assert [lhs[0] for lhs in args[0][1]['constraint_lhs']] == [480, -480.0]
        assert args[0][1]['constraint_rhs'] == 0
        assert args[0][1]['constraint_sense'] == '<='
        assert all([arg[1]['slack_constraint_coeff'] == -1 for arg in args])
        assert all([arg[1]['slack_lower_bound'] == 0 for arg in args])
        assert all([arg[1]['slack_upper_bound'] == constants.numbers.infinity for arg in args])
        assert all([arg[1]['slack_objective_coeff'] == 1 for arg in args])

    def test_add_constraint_to_solver_with_parameters(self, solver, rule25_input, domain):
        """set parameters: should create constraint with correct input arguments"""
        # Arrange
        rule25_input.parameter1 = 480
        rule25_input.parameter5 = 1
        rule25 = Rule25(rule25_input)
        pay_period_length = 7

        # Act
        rule25._add_constraint_to_solver(solver, domain, domain.employees[0], domain.days[0], pay_period_length)
        args = solver.create_slacked_constraint.call_args_list

        # Assert
        assert len(args) == 1
        assert args[0][1]['id'] == 'max_working_time1_2022.01.01_00_00_00_0'
        assert [lhs[0] for lhs in args[0][1]['constraint_lhs']] == [480, -480.0]
        assert args[0][1]['constraint_rhs'] == 420


    def test_create_shift_type_slack_var(self, solver, rule25_input, domain):
        """should create variable with specific id and call constraint with correct input args"""
        # Arrange
        rule25 = Rule25(rule25_input)

        # Act
        shift_type_slack_var = rule25._create_shift_type_slack_var(solver, domain.employees[0], domain.days[0], domain.shifts, domain.shifts, 1)
        args = solver.create_slacked_constraint.call_args_list

        # Assert
        assert shift_type_slack_var.id == 'var_min_shifts_of_type_min1_2022.01.01_00_00_00_0'
        assert len(args) == 2
        assert [arg[1]['id'] for arg in args] == ['min_shifts_of_type_min1_2022.01.01_00_00_00_0',
                                                  'min_shifts_of_type_max1_2022.01.01_00_00_00_0']
        assert [lhs[0] for arg in args for lhs in arg[1]['constraint_lhs']] == [1, 1, 2, 1, 1, 2]
        assert [arg[1]['constraint_rhs'] for arg in args] == [1, 2]
        assert [arg[1]['constraint_sense'] for arg in args] == ['>=', '<=']
        assert [arg[1]['slack_constraint_coeff'] for arg in args] == [2, 0]
        assert all([arg[1]['slack_lower_bound'] == 0 for arg in args])
        assert [arg[1]['slack_upper_bound'] for arg in args] == [1, 0]
        assert all([arg[1]['slack_objective_coeff'] == 0 for arg in args])

    def test_generate_violation(self, solver, rule25_input, domain):
        """should generate correct violation"""
        # Arrange
        rule25 = Rule25(rule25_input)
        slack_var = MagicMock(x=1, obj=rule25_input.penalty * domain.settings.rule_objective)
        pay_period_length = 7

        # Act
        violation = rule25._generate_violation(solver, domain.employees[0], domain.days[0], pay_period_length)

        # Assert
        assert violation.date == 1640995200
        assert violation.parameters == {'parameter_1': 0, 'parameter_2': 0, 'parameter_3': 0, 'parameter_4': 0, 'parameter_5': 0, 'parameter_6': 0}
        assert violation.relevant_shifts == ['1']
        assert violation.rule_id == '25'
        assert violation.rule_tag == 'max_working_time'
        assert violation.user_id == '1'
        assert violation.violation_costs == 1
        assert violation.violation_description == 'More than 0.0 working hours in the period of 7 days starting on 2022.01.01_00_00_00'

@pytest.fixture(scope='function')
def solver():
    slvr = MagicMock()
    slvr.constraints = []

    def side_effect_slacked_constraint(id, *args, **kwargs):
        constraint = MagicMock(id=id)
        variable = MagicMock(id=f'var_{id}')
        slvr.constraints.append(constraint)
        return constraint, variable

    slvr.create_slacked_constraint = MagicMock(side_effect=side_effect_slacked_constraint)

    def side_effect_variable(id, *args, **kwargs):
        variable = MagicMock(id=id, x=1)
        return variable

    def side_effect_positive_slack_var(id, *args, **kwargs):
        return True

    def side_effect_violation_costs(id, *args, **kwargs):
        return 1

    slvr.find_variable = MagicMock(side_effect=side_effect_variable)
    slvr.find_slack_variable_constraint = MagicMock(x=1)
    slvr.positive_slack_var = side_effect_positive_slack_var
    slvr.get_violation_costs_slack_var = side_effect_violation_costs
    return slvr


@pytest.fixture(scope='function')
def rule25_input(domain):
    return Rule({
        'rule_id': '25',
        'penalty': 1,
    },
        domain.settings
    )


@pytest.fixture(scope='function')
def domain():
    domain = MagicMock()
    domain.settings = Settings({
        'start': int(datetime(2022, 1, 1, 9).timestamp()),
        'end': int(datetime(2022, 1, 14, 17).timestamp()),
        'rule_objective': 1,
    })
    domain.shift_type_definitions = ShiftTypeCollection([ShiftType({
        'id': "1",
        'start_after': 300,
        'start_before': 600,
    })])
    domain.shifts = ShiftCollection([Shift({
        'id': "1",
        'start': int(datetime(2022, 1, 1, 9).timestamp()),
        'end': int(datetime(2022, 1, 1, 17).timestamp()),
        'department_id': 'A'
    },
        domain.shift_type_definitions,
        domain.settings,
    ),
        Shift({
            'id': "2",
            'start': int(datetime(2022, 1, 8, 9).timestamp()),
            'end': int(datetime(2022, 1, 8, 17).timestamp()),
            'department_id': 'A'
        },
            domain.shift_type_definitions,
            domain.settings,
        ),
    ])
    domain.employees = EmployeeCollection([Employee({
        'id': "1",
        'department_ids': [{'id': 'A'}],
        'previous_hours': 1
    },
        domain.shifts,
        domain.settings,
    ),
        Employee({
            'id': "2",
            'department_ids': [{'id': 'A'}]
        },
            domain.shifts,
            domain.settings,
        ),
    ])
    domain.days = DayCollection().initialize_days(domain.shifts, domain.settings)
    return domain
