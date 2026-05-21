#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 BigPanda
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
author:
  - Juan Cardozo (@JuanDCardozo)
description:
  - This module resolves a BigPanda alert by providing the alert ID and an optional resolution message.
module: resolve_alert
options:
  alert_ids:
    description: A list of alert IDs to resolve.
    required: true
    type: list
    elements: str
  comments:
    description: A list of resolution comments for the alerts.
    required: false
    type: list
    elements: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
short_description: Resolve a BigPanda alert.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Resolve an alert
  bigpanda.incident.resolve_alert:
    alert_ids:
      - "54321"
    comments:
      - "Alert resolved."
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the alert resolution was successful.
  type: bool
  returned: always
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: success
  sample: "Alert resolved successfully."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    bigpanda_request,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            environment_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
            alert_ids=dict(type='list', required=True, elements='str'),
            comments=dict(type='list', required=False, elements='str'),
        ),
        supports_check_mode=True,
    )

    alert_ids = module.params['alert_ids']
    comments = module.params['comments']

    data = {"ids": alert_ids}
    if comments:
        data['comments'] = comments

    response = bigpanda_request(
        module, "post",
        "batch-resolve/alerts",
        data,
    )
    module.exit_json(changed=True, result=response.text)


if __name__ == '__main__':
    main()
