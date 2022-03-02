from unittest.mock import MagicMock
from domain.shift import Shift


def create_shift(shift_id, start, end):
    shift_spec = {"start": int(start.timestamp()),
                  "end": int(end.timestamp()),
                  "id": shift_id}

    shift_type_definitions = MagicMock()
    settings = MagicMock()
    settings.time_zone = None

    return Shift(shift_spec, shift_type_definitions, settings)
