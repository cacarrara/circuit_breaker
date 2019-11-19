from exceptions import CircuitOpenException


class CircuitBreaker:
    def __init__(
        self, func, exception=Exception, failure_threshold=3, max_open_calls=5
    ):
        self.inner_func = func
        self.exception_to_catch = exception
        self.failure_threshold = failure_threshold
        self.max_open_calls = max_open_calls
        self.reset_failures()

    def __call__(self, *args, **kwargs):
        if self.is_circuit_open():
            self.raise_circuit_open()

        try:
            result = self.inner_func(*args, **kwargs)
            self.reset_failures()
            return result
        except self.exception_to_catch as e:
            self.failure_count += 1
            raise e

    def is_circuit_open(self):
        return self.failure_count > 0 and self.failure_count > self.failure_threshold

    def reset_failures(self):
        self.failure_count = 0
        self.circuit_open_call_count = 0

    def raise_circuit_open(self):
        self.circuit_open_call_count += 1
        if self.circuit_open_call_count <= self.max_open_calls:
            raise CircuitOpenException("Circuit is open. No external calls being made.")
        else:
            self.circuit_open_call_count = 0


def circuit_breaker(
    _func=None, exception=Exception, failure_threshold=3, max_open_calls=5
):
    def _circuit_breaker(func):
        return CircuitBreaker(
            func,
            exception=exception,
            failure_threshold=failure_threshold,
            max_open_calls=max_open_calls,
        )

    if _func is None:
        return _circuit_breaker
    else:
        return _circuit_breaker(_func)
