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
  - This module updates a BigPanda incident tag by providing the tag ID, tag value, incident ID, and an API token.
module: add_tag
options:
  tag_id:
    description: The ID of the tag to update.
    required: true
    type: str
  tag_value:
    description: The new value for the tag.
    required: true
    type: str
  incident_id:
    description: The ID of the incident to update.
    required: true
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
short_description: Update a BigPanda incident tag.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Update an incident tag
  bigpanda.incident.add_tag:
    tag_id: "tag123"
    tag_value: "NewTagValue"
    incident_id: "incident456"
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the tag update was successful.
  type: bool
  returned: always
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: success
  sample: "Tag updated successfully."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    bigpanda_request,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            tag_id=dict(type='str', required=True),
            tag_value=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
            environment_id=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )

    incident_id = module.params['incident_id']
    tag_id = module.params['tag_id']
    tag_value = module.params['tag_value']

    response = bigpanda_request(
        module, "post",
        f"incidents/{incident_id}/tags/{tag_id}",
        {"tag_value": tag_value},
    )
    module.exit_json(changed=True, result=response.text)


if __name__ == '__main__':
    main()
