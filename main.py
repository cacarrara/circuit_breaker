import time

import requests


class CircuitOpenException(Exception):
    pass


def circuit_breaker(
    _func=None, *, exception=Exception, failure_threshold=3, max_open_call=5
):
    def _circuit_breaker(func):
        def circuit(*args, **kwargs):
            if (
                circuit.failure_count > 0
                and circuit.failure_count >= circuit.failure_threshold
            ):
                circuit.circuit_open_call_count += 1

                if circuit.circuit_open_call_count <= circuit.max_open_call:
                    raise CircuitOpenException(
                        "Circuit is open. No external calls being made."
                    )
                else:
                    circuit.circuit_open_call_count = 0

            try:
                result = func(*args, **kwargs)
                circuit.failure_count = 0
                circuit.circuit_open_call_count = 0
                return result
            except exception as e:
                circuit.failure_count += 1
                raise e

        circuit.failure_threshold = failure_threshold
        circuit.max_open_call = max_open_call
        circuit.failure_count = 0
        circuit.circuit_open_call_count = 0

        return circuit

    if _func is None:
        return _circuit_breaker
    else:
        return _circuit_breaker(_func)


@circuit_breaker(
    exception=requests.ConnectionError, failure_threshold=4, max_open_call=3
)
def make_call(endpoint):
    return requests.get(endpoint)


if __name__ == "__main__":
    while True:
        try:
            result = make_call("https://jsonplaceholder.typicode.com/users/1")
            print(f"Request made successfully, status={result.status_code}, content:")
            print(result.json())
            time.sleep(3)
        except requests.ConnectionError as e:
            print(e)
            time.sleep(1)
        except CircuitOpenException as e:
            print(e)
            time.sleep(3)
