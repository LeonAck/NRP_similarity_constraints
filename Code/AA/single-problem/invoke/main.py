from domain import Domain
import json
from strategies import Strategies


def run(
    users,
    shifts,
    rules,
    settings,
    shift_type_definitions=[],
    initial_solution=[],
    data_to_return={},
    globalOrganisationId="",
):
    """
    The main function of the algorithm. Parses the problem to domain objects, translates
    those objects to a problem (variables, constraints, and objective function), solves the
    problem, and returns the solution to the client.
    """
    domain = Domain(
        {
            "users": users,
            "shifts": shifts,
            "rules": rules,
            "settings": settings,
            "shift_type_definitions": shift_type_definitions,
            "initial_solution": initial_solution,
            "data_to_return": data_to_return,
        }
    )
    strategies = Strategies(domain)
    strategy = strategies.get_strategy()
    results = strategy.find_solution()
    output = {"result": results}
    if data_to_return and results.get("result"):
        output["result"]["data_to_return"] = data_to_return

    return output["result"]


# def run_input():
#     directory = './../input_data/problem.json'
#     with open(directory) as json_file:
#         data = json.load(json_file)
#     result = run(**data)
#     with open('./output.json', 'w') as out_file:
#         json.dump(result, out_file, indent=2)
#     print(result["goal_score"])
#
# run_input()
