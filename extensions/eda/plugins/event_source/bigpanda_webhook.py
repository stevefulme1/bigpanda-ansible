"""BigPanda webhook event source for Event-Driven Ansible.

Processes BigPanda alert webhook payloads delivered through the
EDA Gateway event stream. The Gateway handles authentication,
TLS termination, and event routing.

Documentation: https://docs.bigpanda.io/reference/webhooks
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: bigpanda_webhook
short_description: Process BigPanda alert webhooks via EDA Gateway
description:
  - Processes BigPanda webhook payloads received through the EDA Gateway event stream.
  - In AAP 2.6+, configure BigPanda to send webhooks to the EDA Gateway URL.
  - The Gateway handles all authentication and TLS — this source only filters and
    normalizes events for rulebook processing.
version_added: "1.3.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  event_filter:
    description:
      - Filter events by BigPanda alert status.
      - When set, only events matching the specified statuses are emitted.
    type: list
    elements: str
    default: []
"""

EXAMPLES = r"""
# Configure BigPanda to send webhooks to the EDA Gateway:
#   https://<eda-gateway>/api/eda/v1/external_event_stream/<stream-id>/post/
#
# Authentication and TLS are configured in EDA Controller, not here.

- name: BigPanda Alert Automation
  hosts: all
  sources:
    - bigpanda.incident.bigpanda_webhook:
        event_filter:
          - critical
          - warning
  rules:
    - name: Critical alert received
      condition: event.payload.status == "critical"
      action:
        run_playbook:
          name: remediate_critical.yml

    - name: Alert resolved
      condition: event.payload.status == "ok"
      action:
        debug:
          msg: "Alert {{ event.payload.alert_id | default('unknown') }} resolved"
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main(queue: asyncio.Queue, args: dict) -> None:
    """Process BigPanda webhook events from the EDA Gateway event stream."""
    event_filter = args.get("event_filter", [])

    logger.info(
        "BigPanda webhook source started (filter=%s)",
        event_filter or "all",
    )

    while True:
        await asyncio.sleep(0.1)


async def eda_event(event: dict, queue: asyncio.Queue, args: dict) -> None:
    """Process a single event delivered by the EDA Gateway."""
    event_filter = args.get("event_filter", [])

    payload = event.get("payload", event)

    if event_filter:
        status = payload.get("status", "")
        if status not in event_filter:
            return

    normalized = {
        "payload": payload,
        "meta": {
            "source": "bigpanda_webhook",
        },
    }

    await queue.put(normalized)
    logger.info(
        "BigPanda event: status=%s",
        payload.get("status", "unknown"),
    )
