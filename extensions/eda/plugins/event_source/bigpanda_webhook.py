"""BigPanda webhook event source for Event-Driven Ansible.

Receives BigPanda alert webhook notifications and emits them as events.
Configure BigPanda to send webhooks to http://<host>:<port>/bigpanda.

Documentation: https://docs.bigpanda.io/reference/webhooks
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: bigpanda_webhook
short_description: Receive BigPanda alert webhooks for Event-Driven Ansible
description:
  - Listens for BigPanda webhook notifications and emits alert events.
  - Configure BigPanda to send webhooks to C(http://<host>:<port>/bigpanda).
  - Supports alert created, changed, and resolved event types.
version_added: "1.3.0"
author:
  - Steve Fulmer (@stevefulme1)
options:
  host:
    description: The hostname to bind the webhook listener to.
    type: str
    default: 0.0.0.0
  port:
    description: The port to bind the webhook listener to.
    type: int
    default: 5000
  token:
    description:
      - Optional bearer token for webhook authentication.
      - When set, only requests with a matching Authorization header are accepted.
    type: str
"""

EXAMPLES = r"""
- name: Listen for BigPanda alerts
  sources:
    - bigpanda.incident.bigpanda_webhook:
        host: 0.0.0.0
        port: 5000
        token: "{{ bigpanda_webhook_token }}"
  rules:
    - name: Alert created
      condition: event.payload.status == "critical"
      action:
        run_playbook:
          name: remediate.yml
"""

import asyncio
import logging
from aiohttp import web

logger = logging.getLogger(__name__)


async def main(queue: asyncio.Queue, args: dict) -> None:
    """Receive BigPanda webhook events."""
    host = args.get("host", "0.0.0.0")
    port = int(args.get("port", 5000))
    token = args.get("token")

    app = web.Application()

    async def handler(request: web.Request) -> web.Response:
        if token:
            auth = request.headers.get("Authorization", "")
            if auth != f"Bearer {token}":
                return web.Response(status=401, text="Unauthorized")

        try:
            payload = await request.json()
        except Exception:
            return web.Response(status=400, text="Invalid JSON")

        event = {
            "payload": payload,
            "meta": {
                "source": "bigpanda_webhook",
                "endpoint": str(request.url),
                "headers": dict(request.headers),
            },
        }

        await queue.put(event)
        logger.info("Received BigPanda event: %s", payload.get("status", "unknown"))

        return web.Response(status=200, text="OK")

    app.router.add_post("/bigpanda", handler)
    app.router.add_post("/", handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("BigPanda webhook listener started on %s:%d", host, port)

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    """Entry point for testing."""

    class MockQueue:
        async def put(self, event):
            print(event)

    asyncio.run(main(MockQueue(), {}))
