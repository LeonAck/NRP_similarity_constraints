import json
import pandas as pd

hidden_instances = [
    '035-4-0-1-7-1-8',
    '035-4-0-4-2-1-6',
    '035-4-0-5-9-5-6',
    '035-4-0-9-8-7-7',
    '035-4-1-0-6-9-2',
    '035-4-2-8-6-7-1',
    '035-4-2-8-8-7-5',
    '035-4-2-9-2-2-6',
    '035-4-2-9-7-2-2',
    '035-4-2-9-9-2-1',
    '070-4-0-3-6-5-1',
    '070-4-0-4-9-6-7',
    '070-4-0-4-9-7-6',
    '070-4-0-8-6-0-8',
    '070-4-0-9-1-7-5',
    '070-4-1-1-3-8-8',
    '070-4-2-0-5-6-8',
    '070-4-2-3-5-8-2',
    '070-4-2-5-8-2-5', '070-4-2-9-5-6-5',
    '110-4-0-1-4-2-8', '110-4-0-1-9-3-5',
    '110-4-1-0-1-6-4', '110-4-1-0-5-8-8',
    '110-4-1-2-9-2-0', '110-4-1-4-8-7-2',
    '110-4-2-0-2-7-0', '110-4-2-5-1-3-0',
    '110-4-2-8-9-9-2', '110-4-2-9-8-4-9'
]

late_instances = [
    '030-4-1-6-2-9-1', '030-4-1-6-7-5-3',
    '040-4-0-2-0-6-1', '040-4-2-6-1-0-6',
    '050-4-0-0-4-8-7', '050-4-0-7-2-7-2',
    '060-4-1-6-1-1-5', '060-4-1-9-6-3-8',
    '080-4-2-4-3-3-3', '080-4-2-6-0-4-8',
    '100-4-0-1-1-0-8', '100-4-2-0-6-4-6',
    '120-4-1-4-6-2-6', '120-4-1-5-6-9-8'
]

eight_week_instances = [
    '030-8-1-2-7-0-9-3-6-0-6', '030-8-1-6-7-5-3-5-6-2-9',
    '035-8-0-6-2-9-8-7-7-9-8', '035-8-1-0-8-1-6-1-7-2-0',
    '040-8-0-0-6-8-9-2-6-6-4', '040-8-2-5-0-4-8-7-1-7-2',
    '050-8-1-1-7-8-5-7-4-1-8', '050-8-1-9-7-5-3-8-8-3-1',
    '060-8-0-6-2-9-9-0-8-1-3', '060-8-2-1-0-3-4-0-3-9-1',
    '070-8-0-3-3-9-2-3-7-5-2', '070-8-0-9-3-0-7-2-1-1-0',
    '080-8-1-4-4-9-9-3-6-0-5', '080-8-2-0-4-0-9-1-9-6-2',
    '100-8-0-0-1-7-8-9-1-5-4', '100-8-1-2-4-7-9-3-9-2-8',
    '110-8-0-2-1-1-7-2-6-4-7', '110-8-0-3-2-4-9-4-1-3-7',
    '120-8-0-0-9-9-4-5-1-0-3', '120-8-1-7-2-6-4-5-2-0-2'
]
file_path = "C:/Master_thesis/Code/Metaheuristic/output_files/"

f = open(file_path)
output_json = json.load(f)

mock_values = list(range(len(hidden_instances)))
data = {"hidden_instances": hidden_instances, "Avg cost": mock_values}
df = pd.DataFrame(data)

df.to_latex()
def create_latex_table(list_of_instances, caption):
    pass
    # create dataframe with data
    # dataframe to latex