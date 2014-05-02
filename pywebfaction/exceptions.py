class WebFactionFault(Exception):
    def __init__(self, underlying_fault):
        self.underlying_fault = underlying_fault
