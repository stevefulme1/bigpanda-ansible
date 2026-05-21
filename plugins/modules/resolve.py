#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 BigPanda
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
author:
  - Juan Cardozo (@JuanDCardozo)
description:
  - This module resolves a BigPanda incident by providing the incident ID and an optional resolution message.
module: resolve
options:
  incident_id:
    description: The ID of the incident to resolve.
    required: true
    type: str
  resolution_comment:
    description: The resolution message for the incident.
    required: false
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
short_description: Resolve a BigPanda incident.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Resolve an incident
  bigpanda.incident.resolve:
    incident_id: "12345"
    resolution_comment: "Incident resolved."
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the incident resolution was successful.
  type: bool
  returned: always
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: success
  sample: "Incident resolved successfully."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    bigpanda_request,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            resolution_comment=dict(type='str', required=False),
            environment_id=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
        ),
        supports_check_mode=True,
    )

    incident_id = module.params['incident_id']
    resolution_comment = module.params['resolution_comment']

    response = bigpanda_request(
        module, "post",
        f"incidents/{incident_id}/resolve",
        {"comments": resolution_comment},
    )
    module.exit_json(changed=True, result=response.text)


if __name__ == '__main__':
    main()
