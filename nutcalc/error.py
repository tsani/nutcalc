class NutcalcError(RuntimeError):
    """Base class for any error raised by Nutcalc."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        