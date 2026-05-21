# -*- coding: utf-8 -*-
# Copyright 2023 BigPanda
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""Shared utilities for BigPanda incident modules."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

BIGPANDA_API_BASE = "https://api.bigpanda.io/resources/v2.0"


def require_requests(module):
    """Fail the module if the requests library is not available."""
    if not HAS_REQUESTS:
        module.fail_json(
            msg="The 'requests' Python library is required. "
                "Install it with: pip install requests"
        )


def bigpanda_request(module, method, path, data=None):
    """Make an authenticated request to the BigPanda API.

    Args:
        module: AnsibleModule instance (provides params and fail_json)
        method: HTTP method (get, post, put, delete)
        path: API path (appended to base URL)
        data: Optional request body (dict)

    Returns:
        requests.Response object
    """
    require_requests(module)

    env_id = module.params["environment_id"]
    token = module.params["api_token"]

    url = f"{BIGPANDA_API_BASE}/environments/{env_id}/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = getattr(requests, method)(
            url, headers=headers, json=data, timeout=30
        )
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as exc:
        module.fail_json(
            msg=f"BigPanda API error: {exc.response.status_code} "
                f"{exc.response.text}",
            status_code=exc.response.status_code,
        )
    except requests.exceptions.RequestException as exc:
        module.fail_json(msg=f"BigPanda API request failed: {exc}")
