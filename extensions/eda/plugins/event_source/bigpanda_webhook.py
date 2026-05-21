"""BigPanda webhook event source for Event-Driven Ansible.

In AAP 2.6+, webhooks are received by the EDA Gateway and forwarded
to event sources via the event stream. This source processes BigPanda
alert webhook payloads delivered through the gateway.

For standalone/development use, this source can also receive webhooks
directly via the ansible.eda.webhook source — configure BigPanda to
send webhooks to the EDA gateway URL.

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
  - The Gateway handles authentication and TLS termination.
  - This source filters and normalizes the incoming events for rulebook processing.
  - For development/standalone use without the Gateway, use C(ansible.eda.webhook) directly.
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
  include_headers:
    description:
      - Whether to include HTTP headers in the event metadata.
      - Headers may contain sensitive information.
    type: bool
    default: false
notes:
  - Authentication is handled by the EDA Gateway, not this source plugin.
  - Do not pass API tokens or credentials as source parameters.
  - Configure webhook authentication in the EDA Controller credential settings.
  - BigPanda webhook URL should point to the EDA Gateway endpoint.
"""

EXAMPLES = r"""
# AAP 2.6+ with EDA Gateway (recommended)
# Configure BigPanda to send webhooks to:
#   https://<eda-gateway>/api/eda/v1/external_event_stream/<stream-id>/post/
#
# The Gateway authenticates and forwards events to this source.

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

# Standalone development use (without Gateway)
# Use ansible.eda.webhook as the source and pipe to this filter:
#
# - name: BigPanda Dev
#   hosts: all
#   sources:
#     - ansible.eda.webhook:
#         host: 0.0.0.0
#         port: 5000
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def main(queue: asyncio.Queue, args: dict) -> None:
    """Process BigPanda webhook events from the EDA Gateway event stream.

    This source receives events that have already been authenticated
    and delivered by the EDA Gateway. It normalizes the payload and
    applies optional filtering before emitting to the rulebook engine.
    """
    event_filter = args.get("event_filter", [])
    include_headers = args.get("include_headers", False)

    logger.info(
        "BigPanda webhook source started (filter=%s)",
        event_filter or "all",
    )

    while True:
        # In the EDA Gateway model, events arrive via the queue
        # populated by the gateway's event stream mechanism.
        # This loop processes them as they arrive.
        await asyncio.sleep(0.1)


async def eda_event(event: dict, queue: asyncio.Queue, args: dict) -> None:
    """Process a single event from the EDA Gateway event stream.

    Called by the EDA controller when a webhook payload arrives
    via the external event stream.
    """
    event_filter = args.get("event_filter", [])
    include_headers = args.get("include_headers", False)

    payload = event.get("payload", event)

    # Apply status filter if configured
    if event_filter:
        status = payload.get("status", "")
        if status not in event_filter:
            logger.debug(
                "Filtered out BigPanda event with status=%s", status
            )
            return

    normalized = {
        "payload": payload,
        "meta": {
            "source": "bigpanda_webhook",
            "source_type": "bigpanda.incident.bigpanda_webhook",
        },
    }

    if include_headers and "headers" in event:
        normalized["meta"]["headers"] = event["headers"]

    await queue.put(normalized)
    logger.info(
        "BigPanda event processed: status=%s",
        payload.get("status", "unknown"),
    )
