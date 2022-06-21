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

eight_week_legrain_cost = [
    2070,
    1735,
    2555,
    2305,
    2620,
    2420,
    4900,
    4925,
    2345,
    2590,
    4595,
    4760,
    4180,
    4450,
    2125,
    2210,
    4010,
    3560,
    2600,
    3095
]

eight_week_ceschia_avg = [
    2098,
    1787,
    2737,
    2527,
    2782,
    2854,
    5002,
    4958.5,
    2146,
    2675,
    4866,
    5030.5,
    4477,
    4795,
    2410.5,
    2557,
    4226,
    3688.5,
    2871,
    3317
]

eight_week_ceschia_best = [
    2055,
    1750,
    2705,
    2465,
    2695,
    2525,
    4935,
    4920,
    2375,
    2630,
    4785,
    4950,
    4350,
    4710,
    2340,
    2510,
    4170,
    3650,
    2810,
    3260
]

# file_path = "C:/Master_thesis/Code/Metaheuristic/output_files/"

# f = open(file_path)
# output_json = json.load(f)

mock_values = list(range(len(hidden_instances)))
hidden_dict = {"hidden_instances": hidden_instances, "legrain_et_al": {}}
eight_week_dict = {"Instance": eight_week_instances, "\cite{legrain2020rotation}": eight_week_legrain_cost,
                   "\cite{ceschia2020solving} Avg cost": eight_week_ceschia_avg,
                   "\cite{ceschia2020solving} Best cost": eight_week_ceschia_best,
                   }

eight_week_run_reg = {"fixed_data": eight_week_dict,
                      "metrics": {"avg_best_solution": "ALNS Avg cost",
                                  "best_best_solution": "ALNS Best cost"},
                      "caption": "Results on 8-week instances",
                      "label": "tab:8_week_reg"
                      }

eight_week_w_similarity = {"fixed_data": {"Instance": eight_week_instances},
                           "metrics": {"avg_best_solution_similarity": "Extended model Avg cost",
                                       "best_best_solution_similarity": "Extended model Best cost",
                                       "avg_best_solution_no_similarity": "Basic Avg cost",
                                       "best_best_solution_no_similarity": "Basic model Best cost"
                                       },
                           "caption": "Results on new 4-week instances with similarity constraints",
                           "label": "tab:8_week_similarity"
                           }

eight_week_wo_similarity = {"fixed_data": {"Instance": eight_week_instances},
                            "metrics": {"avg_best_solution_similarity": "Extended Avg cost",
                                        "best_best_solution_similarity": "Extended Best cost",
                                        "avg_best_solution_no_similarity": "Basic Avg cost",
                                        "best_best_solution_no_similarity": "Basic Best cost"
                                        },
                            "caption": "Results on new 4-week instances without similarity constraints",
                            "label": "tab:8_week_similarity"
                            }


def add_results_to_dict(path, metrics, dict):
    with open(path, "r") as file:
        data = json.loads(file.read())

    for metric, name in metrics.items():
        dict[name] = [output[metric] for output in data.values()]

    return dict


def create_latex_table(settings, path):
    dict = add_results_to_dict(path, settings['metrics'], settings['fixed_data'])
    df = pd.DataFrame(dict)

    print(df.to_latex(index=False, caption=settings['caption'], label=settings['label'], position="h!",
                      float_format="%.1f"))


# create_latex_table(eight_week_run_reg,
#                    path="C:/Master_thesis/Code/Metaheuristic/output_files/17_06_2022__15_01_52/summary.json")
create_latex_table(eight_week_w_similarity,
                   path="C:/Master_thesis/Code/Metaheuristic/output_files/19_06_2022_8_week_w_similarity_1/summary.json")

create_latex_table(eight_week_wo_similarity,
                   path="C:/Master_thesis/Code/Metaheuristic/output_files/20_06_2022_9_runs_no_similarity/summary.json")
