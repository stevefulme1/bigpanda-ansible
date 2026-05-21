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
  - This module adds a comment to a BigPanda incident by providing the incident ID and the comment text.
module: comment
options:
  incident_id:
    description: The ID of the incident to add a comment to.
    required: true
    type: str
  comment:
    description: The text of the comment.
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
short_description: Add a comment to a BigPanda incident.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Add a comment to an incident
  bigpanda.incident.comment:
    incident_id: "12345"
    comment: "This is a test comment."
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the comment addition was successful.
  type: bool
  returned: always
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: success
  sample: "Comment added successfully."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    bigpanda_request,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            comment=dict(type='str', required=True),
            environment_id=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
        ),
        supports_check_mode=True,
    )

    incident_id = module.params['incident_id']
    comment_text = module.params['comment']

    response = bigpanda_request(
        module, "post",
        f"incidents/{incident_id}/comments",
        {"comment": comment_text},
    )
    module.exit_json(changed=True, result=response.text)


if __name__ == '__main__':
    main()
