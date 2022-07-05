import json
from alfa_sdk.common.session import Session


def execute_heuristic(problem):
    algorithm_id = "fde9e297-7579-4ac3-ab2a-078fb74e4040"
    environment = "thesis_env"

    session = Session(keepalive=True)
    result = session.invoke_algorithm(algorithm_id, environment, problem)
    print("single run done")
    return result


with open("./input.json", "r") as file:
    data = json.loads(file.read())


print("started")
output = execute_heuristic(data)
print("done")

print(output)
