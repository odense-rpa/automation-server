import requests
import logging
from contextlib import contextmanager

from . import automationserver_url
from . import headers

base_url = f"{automationserver_url}/resources"

logger = logging.getLogger(__name__)


@contextmanager
def acquire_resource(fqdn: str, name: str, capabilities: str):
    try:
        resource = register_resource(fqdn=fqdn, name=name, capabilities=capabilities)
        yield resource
    finally:
        logger.info(f"Release resource: {name}")


def register_resource(fqdn: str, name: str, capabilities: str) -> dict:
    response = requests.post(
        f"{base_url}/",
        json={"fqdn": fqdn, "name": name, "capabilities": capabilities},
        headers=headers,
    )
    response.raise_for_status()
    logger.info(f"#{name} has entered the chat")
    return response.json()


def update_resource(resource_id: int, fqdn: str, name: str, capabilities: str) -> dict:
    response = requests.put(
        f"{base_url}/{resource_id}",
        json={"fqdn": fqdn, "name": name, "capabilities": capabilities},
        headers=headers,
    )
    response.raise_for_status()
    logger.info(f"#{name} was updated")
    return response.json()


def ping_resource(resource_id: int):
    response = requests.put(f"{base_url}/{resource_id}/ping", headers=headers)
    response.raise_for_status()
    logger.info(f"#{resource_id} has sent a ping")
