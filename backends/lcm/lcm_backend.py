class Backend:

    def __init__(self, led_count):
        raise NotImplementedError(
            "Could not load backend as it has not been implemented, go implement it!"
        )

    def set_led(self, led_index: int, on: bool):
        pass
