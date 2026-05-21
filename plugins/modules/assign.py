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
  - This module assigns a user to be responsible for a BigPanda incident by providing the incident ID and the user's ID.
module: assign
options:
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  incident_id:
    description: The ID of the incident to assign a user to.
    required: true
    type: str
  assignee_id:
    description: The ID of the user to be assigned.
    required: true
    type: str
short_description: Assign a user to be responsible for an incident in BigPanda.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Assign a user to an incident
  bigpanda.incident.assign:
    environment_id: "your_environment_id"
    api_token: "your_api_token"
    incident_id: "your_incident_id"
    assignee_id: "AssigneeID"
"""

RETURN = """
changed:
  description: Indicates if the user assignment was successful.
  type: bool
  returned: always
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: success
  sample: "User assigned successfully to the incident."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    bigpanda_request,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            environment_id=dict(type="str", required=True),
            api_token=dict(type="str", required=True, no_log=True),
            incident_id=dict(type="str", required=True),
            assignee_id=dict(type="str", required=True),
        ),
        supports_check_mode=True,
    )

    incident_id = module.params["incident_id"]
    assignee_id = module.params["assignee_id"]

    response = bigpanda_request(
        module, "put",
        f"incidents/{incident_id}/assignment",
        {"assignee": assignee_id},
    )
    module.exit_json(changed=True, result=response.text)


if __name__ == "__main__":
    main()
