import json
import time

import click
import requests
from requests import ConnectionError

from cbreaker_decorator import circuit_breaker
from exceptions import CircuitOpenException


@circuit_breaker(exception=ConnectionError, failure_threshold=4, max_open_calls=3)
def make_http_call(endpoint, method="get", data=None, headers=None):
    request_method = getattr(requests, method)
    return request_method(endpoint, json=data, headers=headers)


@click.command()
@click.option("--login", help="API login")
@click.option("--password", help="API password")
def main(login, password):
    base_url = "http://127.0.0.1:8000/v1"
    auth_url = f"{base_url}/authenticate"
    projects_url = f"{base_url}/projects/"

    auth_response = make_http_call(
        auth_url, method="post", data={"login": login, "password": password}
    )

    if not auth_response or auth_response.status_code != 200:
        click.echo(click.style("Login failed...", fg="red", bold=True))
        click.echo(click.style(str(auth_response.json()), fg="red"))
        return

    jwt_token = auth_response.json()["token"]

    while True:
        try:
            result = make_http_call(
                projects_url, headers={"Authorization": f"JWT {jwt_token}"}
            )
            success_msg = f"Request made successfully, status={result.status_code}, content:"
            click.echo(click.style(success_msg, fg="green"))
            click.echo(click.style(json.dumps(result.json(), indent=2), fg="green", bold=True))
            time.sleep(3)
        except requests.ConnectionError as e:
            click.echo(click.style(str(e), fg="yellow"))
            time.sleep(1)
        except CircuitOpenException as e:
            click.echo(click.style(str(e), fg="bright_yellow", bold=True))
            time.sleep(3)


if __name__ == "__main__":
    main()
