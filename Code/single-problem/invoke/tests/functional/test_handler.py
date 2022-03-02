import json
import os
from main import run
import pytest
from collections import defaultdict


class TestCustomerProblems:
    """[Functional] main.run linearized problems"""

    @pytest.fixture(scope="class")
    def directory(self):
        return os.path.join(
                "tests",
                "static",
                "data",
                "functional",
                "linearized_problems"
        )

    def test_customer1(self, directory):
        """test goal score customer 1"""
        # Arrange
        with open(os.path.join(directory, "customer1.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(60900)

    def test_customer2(self, directory):
        """test goal score customer 2"""
        # Arrange
        with open(os.path.join(directory, "customer2.json")) as problem_file:
            problem_customer_2 = json.load(problem_file)

        # Act
        result = run(**problem_customer_2)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(54922)

    def test_customer3(self, directory):
        """test goal score customer 3"""
        # Arrange
        with open(os.path.join(directory, "customer3.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(135001000)

    def test_customer4(self, directory):
        """test goal score customer 4"""
        # Arrange
        with open(os.path.join(directory, "customer4.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(16723000)

    def test_customer5(self, directory):
        """test goal score customer 5"""
        # Arrange
        with open(os.path.join(directory, "customer5.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(1073201)

    def test_customer6(self, directory):
        """test goal score customer 6"""
        # Arrange
        with open(os.path.join(directory, "customer6.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(150)

    def test_customer7(self, directory):
        """test goal score customer 7"""
        # Arrange
        with open(os.path.join(directory, "customer7.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(8154416967)

    def test_customer8(self, directory):
        """test goal score customer 8"""
        # Arrange
        with open(os.path.join(directory, "customer8.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(139000496)

    def test_customer9(self, directory):
        """test goal score customer 9"""
        # Arrange
        with open(os.path.join(directory, "customer9.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(4741503522)

    def test_customer10(self, directory):
        """test goal score customer 10"""
        # Arrange
        with open(os.path.join(directory, "customer10.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(336001151)

    def test_customer11(self, directory):
        """test goal score customer 11"""
        # Arrange
        with open(os.path.join(directory, "customer11.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(0)

    def test_customer12(self, directory):
        """test goal score customer 12"""
        # Arrange
        with open(os.path.join(directory, "customer12.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(3055)

    def test_customer13(self, directory):
        """test goal score customer 13"""
        # Arrange
        with open(os.path.join(directory, "customer13.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        print(result)
        # Assert
        assert round(result["goal_score"]) == pytest.approx(101741)

    def test_customer14(self, directory):
        """test goal score customer 14"""
        # Arrange
        with open(os.path.join(directory, "customer14.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(1420)

    def test_customer15(self, directory):
        """test goal score customer 15"""
        # Arrange
        with open(os.path.join(directory, "customer15.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(46044523949)

    def test_customer16(self, directory):
        """test goal score customer 16"""
        # Arrange
        with open(os.path.join(directory, "customer16.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(-11800)

    def test_customer17(self, directory):
        """test goal score customer 17"""
        # Arrange
        with open(os.path.join(directory, "customer17.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(970080)

    def test_customer18(self, directory):
        """test goal score customer 18"""
        # Arrange
        with open(os.path.join(directory, "customer18.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(1400)

    def test_customer19(self, directory):
        """test goal score customer 19"""
        # Arrange
        with open(os.path.join(directory, "customer19.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(81526)

    def test_customer20(self, directory):
        """test goal score customer 20"""
        # Arrange
        with open(os.path.join(directory, "customer20.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert round(result["goal_score"]) == pytest.approx(303642)


class TestFixedProblems:
    """[Functional] main.run fixed problems"""

    @pytest.fixture(scope="class")
    def directory(self):
        return os.path.join(
                "tests",
                "static",
                "data",
                "functional",
                "fixed_problems"
        )

    def test_rule16_1(self, directory):
        """test output including violation rule 16: scenario 1 (no violation)"""
        # Arrange
        file_name = "Rule16_1.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)

        assert round(result["goal_score"]) == pytest.approx(0)

    def test_rule16_2(self, directory):
        """test output including violation rule 16: scenario 2 (1 violation)"""
        # Arrange
        file_name = "Rule16_2.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)

        assert round(result["goal_score"]) == pytest.approx(1)

    def test_rule25(self, directory):
        """test output including violation rule 25"""
        # Arrange
        file_name = "Rule25.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)

        assert round(result["goal_score"]) == pytest.approx(6600000)

    def test_rule42(self, directory):
        """test output including violation rule 42"""
        # Arrange
        file_name = "Rule42.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


        assert round(result["goal_score"]) == pytest.approx(0)

    def test_rule43(self, directory):
        """test output including violation rule 43"""
        # Arrange
        file_name = "Rule43.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


        assert round(result["goal_score"]) == pytest.approx(0)

    def test_rule45(self, directory):
        """test output including violation rule 45"""
        # Arrange
        file_name = "Rule45.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


        assert round(result["goal_score"]) == pytest.approx(10000)

    def test_rule47(self, directory):
        """test output including violation rule 47"""
        # Arrange
        file_name = "Rule47.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


        assert round(result["goal_score"]) == pytest.approx(14400000)

    def test_rule62(self, directory):
        """test output including violation rule 62"""
        # Arrange
        file_name = "Rule62.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)
        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


        assert round(result["goal_score"]) == pytest.approx(150000)


class TestImprovementHeuristicProblems:
    """[Functional] main.run improvement heuristic problems"""

    @pytest.fixture(scope="class")
    def directory(self):
        return os.path.join(
                "tests",
                "static",
                "data",
                "functional",
                "improvement_heuristic"
        )

    def test_improve_customer1(self, directory):
        """test customer 1"""
        # Arrange
        file_name = "customer1.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


class TestShiftingWindowProblems:
    """[Functional] main.run shifting window problems"""

    @pytest.fixture(scope="class")
    def directory(self):
        return os.path.join(
                "tests",
                "static",
                "data",
                "functional",
                "shifting_window"
        )

    def test_shifting_customer1(self, directory):
        """test customer 1"""
        # Arrange
        file_name = "customer1.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


class TestCombinedHeuristicProblems:
    """[Functional] main.run combined heuristic problems"""

    @pytest.fixture(scope="class")
    def directory(self):
        return os.path.join(
                "tests",
                "static",
                "data",
                "functional",
                "combined_heuristic"
        )

    def test_combined_customer1(self, directory):
        """test customer 1"""
        # Arrange
        file_name = "customer1.json"
        with open(os.path.join(directory, file_name)) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        violations_run = json.loads(json.dumps(result["rule_violations"]), parse_int=str)
        with open(os.path.join(directory, "violations", file_name)) as violation_json:
            violations_file = json.load(violation_json, parse_int=str)

        assert freqs(violations_run) == freqs(violations_file)


def counters():
    return defaultdict(int)


def parse_int(value):
    try:
        return int(value)
    except:
        return value


def freqs(LofD):
    keys_to_check = ["user_id", "rule_id", "violation_costs", "department_id"]
    r = defaultdict(counters)
    for d in LofD:
        for k, v in d.items():
            if k in keys_to_check:
                r[parse_int(k)][parse_int(v)] += 1
    return dict((k, dict(v)) for k, v in r.items())


