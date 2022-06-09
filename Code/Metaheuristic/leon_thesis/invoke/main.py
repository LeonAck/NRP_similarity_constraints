from Domain.settings import Settings
from Domain.input_NRC import Instance
from output_from_alfa import create_output_dict
from run_stage_functions import run_stage, run_stage_add_similarity

def run(input_dict):
    """
    Function to execute heuristic
    """
    print(input_dict)
    settings = Settings(input_dict['settings'])

    instance = Instance(settings, input_dict)

    # run stage_1
    heuristic_1, stage_1_solution = run_stage(instance, settings.stage_1_settings)
    # check if first stage feasible

    if heuristic_1.stage_1_feasible:
        # run stage 2
        if not settings.similarity and not settings.tuning:
            heuristic_2, stage_2_solution = run_stage_add_similarity(instance, settings.stage_2_settings,
                                                                     previous_solution=stage_1_solution)
        else:
            heuristic_2, stage_2_solution = run_stage(instance, settings.stage_2_settings,
                                                      previous_solution=stage_1_solution)

    else:
        heuristic_2 = None

    output_dict = create_output_dict(instance.instance_name, heuristic_1, heuristic_2)
    return output_dict



