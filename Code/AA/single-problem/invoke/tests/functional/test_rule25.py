import json
import os
from main import run
import pytest
from collections import defaultdict

class TestRule25:
    """[Functional] test rule 25"""

    @pytest.fixture(scope="class")
    def directory(self):
        return os.path.join(
            "tests",
            "static",
            "data",
            "functional",
            "rules",
            "rule25"
        )

    def test_linearized(self, directory):
        """test linearized problem"""
        # Arrange
        with open(os.path.join(directory, "linearized_problem.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert result["goal_score"] == pytest.approx(0.2)

    def test_fixed(self, directory):
        """test fixed problem"""
        # Arrange
        with open(os.path.join(directory, "fixed_problem.json")) as problem_file:
            problem = json.load(problem_file)

        # Act
        result = run(**problem)

        # Assert
        assert result["goal_score"] == pytest.approx(1700000)
        assert len([violation for violation in result["rule_violations"] if violation["rule_id"] == "25"]) == 1
