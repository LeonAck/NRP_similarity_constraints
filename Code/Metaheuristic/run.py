from Input.input_NRC import Instance

def run(settings, rules=None):
    """
    Function to execute heuristic
    """
    if settings.source == "NRC":
        instance = Instance(settings)

    return None