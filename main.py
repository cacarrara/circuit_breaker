import time

import requests


class CircuitOpenException(Exception):
    pass


def circuit_breaker(_func=None, *, failure_threshold=3, max_open_call=5):
    def _circuit_breaker(func):
        def wrapper(*args, **kwargs):
            if (
                wrapper.failure_count > 0
                and wrapper.failure_count >= wrapper.failure_threshold
            ):
                wrapper.circuit_open_call_count += 1

                if wrapper.circuit_open_call_count <= wrapper.max_open_call:
                    raise CircuitOpenException(
                        "Circuit is open. No external calls being made."
                    )
                else:
                    wrapper.circuit_open_call_count = 0

            try:
                result = func(*args, **kwargs)
                wrapper.failure_count = 0
                wrapper.circuit_open_call_count = 0
                return result
            except requests.ConnectionError as e:
                wrapper.failure_count += 1
                raise e

        wrapper.failure_threshold = failure_threshold
        wrapper.failure_count = 0
        wrapper.circuit_open_call_count = 0
        wrapper.max_open_call = max_open_call

        return wrapper

    if _func is None:
        return _circuit_breaker
    else:
        return _circuit_breaker(_func)


@circuit_breaker
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
