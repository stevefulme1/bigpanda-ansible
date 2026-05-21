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
  - This module merges multiple BigPanda incidents into a single incident.
module: merge
options:
  incident_id:
    description: The ID of the incident to merge into.
    required: true
    type: str
  comment:
    description: A comment describing the merge.
    required: false
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The environment ID.
    required: true
    type: str
  source_incidents:
    description: A list of incident IDs to merge.
    required: true
    type: list
    elements: str
short_description: Merge multiple BigPanda incidents into one.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Merge incidents
  bigpanda.incident.merge:
    incident_id: "target_incident"
    comment: "Merging multiple incidents."
    api_token: "your_api_token"
    environment_id: "your_environment"
    source_incidents:
      - "incident1"
      - "incident2"
"""

RETURN = """
changed:
  description: Indicates if the incidents were successfully merged.
  type: bool
  returned: always
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: success
  sample: "Incidents merged successfully."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    bigpanda_request,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            environment_id=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
            source_incidents=dict(type='list', required=True, elements='str'),
            comment=dict(type='str', required=False),
        ),
        supports_check_mode=True,
    )

    incident_id = module.params['incident_id']
    source_incidents = module.params['source_incidents']
    comment_text = module.params['comment']

    data = {
        'source_incidents': source_incidents,
        'comment': comment_text,
    }

    response = bigpanda_request(
        module, "post",
        f"incidents/{incident_id}/merge",
        data,
    )
    module.exit_json(changed=True, result=response.text)


if __name__ == '__main__':
    main()
