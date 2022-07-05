from alfa_sdk.common.exceptions import AlfaError


class TimeoutError(AlfaError):
    template = "{function} run timed out."
    code = "INVOCATION_TIMEOUT"
    status = 400