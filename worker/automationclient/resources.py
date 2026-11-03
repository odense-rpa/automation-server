import logging
from contextlib import contextmanager

import requests

from . import automationserver_url, headers

base_url = f"{automationserver_url}/resources"

logger = logging.getLogger(__name__)


@contextmanager
def acquire_resource(fqdn: str, name: str, capabilities: str):
    try:
        resource = register_resource(fqdn=fqdn, name=name, capabilities=capabilities)
        yield resource
    finally:
        logger.info("Released resource %s", name)


def register_resource(fqdn: str, name: str, capabilities: str) -> dict:
    logger.info("Registering as %s with capabilities '%s' at %s", name, capabilities, base_url)
    response = requests.post(
        f"{base_url}",
        json={"fqdn": fqdn, "name": name, "capabilities": capabilities},
        headers=headers,
    )
    response.raise_for_status()
    logger.info("Registered as resource %s", name)
    return response.json()


def update_resource(resource_id: int, fqdn: str, name: str, capabilities: str) -> dict:
    response = requests.put(
        f"{base_url}/{resource_id}",
        json={"fqdn": fqdn, "name": name, "capabilities": capabilities},
        headers=headers,
    )
    response.raise_for_status()
    logger.info("Updated resource %s", name)
    return response.json()


def ping_resource(resource_id: int):
    response = requests.put(f"{base_url}/{resource_id}/ping", headers=headers)
    response.raise_for_status()
    logger.debug("Pinged resource %s", resource_id)
